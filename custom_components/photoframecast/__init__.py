import asyncio
import io
import logging
import math
from pathlib import Path
from datetime import datetime, timedelta

import voluptuous as vol
from aiohttp import web
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.integration_platform import async_process_integration_platforms
from homeassistant.helpers.storage import Store
from homeassistant.helpers import config_validation as cv

from .services import start_slideshow_service, stop_slideshow_service, reset_resume_service, photo_of_the_day_service, pause_slideshow_service, resume_slideshow_service, PAUSE_RESUME_SCHEMA, START_SLIDESHOW_SCHEMA
from .helpers import notify_user
from .const import DOMAIN, STORAGE_KEY, STORAGE_VERSION
from .webslideshow import start_webslideshow_service, stop_webslideshow_service, WebSlideshowView, WebSlideshowCurrentView, WebSlideshowWeatherView, WebFileView
from .weather_icons import draw_weather_icon

_LOGGER = logging.getLogger(__name__)

WEATHER_ENTITY = "weather.forecast_home"

# Bundled clock font, kept alongside this file so it travels with the
# integration regardless of what OS/container HA is running in.
# To use your own font, replace this file with another .ttf of the same name.
FONT_PATH = Path(__file__).parent / "clock_font.ttf"

CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)


# ----------------- HTTP View ----------------- #
class GlobalPhotoView(HomeAssistantView):
    requires_auth = False
    url = "/api/photoframecast/{entity_id}/{filename:.*}"
    name = "api:photoframecast"

    def __init__(self, hass: HomeAssistant):
        self.hass = hass

    async def get(self, request, entity_id, filename):
        slideshow = self.hass.data[DOMAIN]["running_slideshows"].get(entity_id)
        if not slideshow:
            return web.Response(status=404, text="No active slideshow")

        folder_path: Path = slideshow["folder"]
        file_path = folder_path / filename

        try:
            if not file_path.resolve().is_relative_to(folder_path.resolve()):
                return web.Response(status=403, text="Forbidden")
        except Exception:
            return web.Response(status=403, text="Forbidden")

        if not await self.hass.async_add_executor_job(file_path.is_file):
            return web.Response(status=404, text="File not found")

        # Fetch weather condition and sun state from HA
        weather_condition = None
        is_night = False
        try:
            weather_state = self.hass.states.get(WEATHER_ENTITY)
            if weather_state:
                weather_condition = weather_state.state
        except Exception:
            pass
        try:
            sun_state = self.hass.states.get("sun.sun")
            if sun_state:
                is_night = sun_state.state == "below_horizon"
        except Exception:
            pass

        # Fetch moon phase state from HA
        moon_phase = None
        try:
            moon_state = self.hass.states.get("sensor.moon_phase")
            if moon_state:
                moon_phase = moon_state.state
        except Exception:
            pass

        def stamp_image():
            from PIL import Image, ImageDraw, ImageFont
            img = Image.open(file_path).convert("RGB")
            draw = ImageDraw.Draw(img, "RGBA")
            now = datetime.now().strftime("%-I:%M %p")
            font_size = max(20, int(img.height * 0.06))
            try:
                font = ImageFont.truetype(str(FONT_PATH), font_size)
            except Exception as e:
                _LOGGER.warning(
                    "PhotoFrameCast: clock_font.ttf failed to load (%s); using tiny built-in fallback font.",
                    e
                )
                font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), now, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            margin_right = 95
            margin_bottom = 60

            # Clock position
            x = img.width - text_w - margin_right
            y = img.height - text_h - margin_bottom
            shadow_offset = max(2, font_size // 20)

            # Draw clock shadow + text
            draw.text((x + shadow_offset, y + shadow_offset), now, font=font, fill=(0, 0, 0, 180))
            draw.text((x, y), now, font=font, fill=(255, 255, 255, 255))

            # Draw weather icon to the left of the clock text
            if weather_condition:
                icon_radius = int(font_size * 0.45)
                icon_gap = int(font_size * 0.4)
                icon_cx = x - icon_gap - icon_radius
                icon_cy = y + text_h // 2

                # Call the updated custom icon processor with moon phase tracking
                draw_weather_icon(draw, weather_condition, icon_cx, icon_cy, icon_radius, is_night=is_night, moon_phase=moon_phase)

            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=90)
            buf.seek(0)
            return buf.read()

        image_bytes = await self.hass.async_add_executor_job(stamp_image)
        return web.Response(body=image_bytes, content_type="image/jpeg")


# ----------------- Setup ----------------- #
async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the PhotoFrameCast integration asynchronously."""
    await async_process_integration_platforms(hass, DOMAIN, "services")

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault("running_slideshows", {})
    hass.data[DOMAIN].setdefault("sync_groups", {})

    # Persistent storage for resume feature
    hass.data[DOMAIN]["store"] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    stored = await hass.data[DOMAIN]["store"].async_load()
    if stored is None:
        stored = {}
    hass.data[DOMAIN]["resume_data"] = stored

    hass.http.register_view(GlobalPhotoView(hass))

    # Register Services
    hass.services.async_register(DOMAIN, "start_slideshow", start_slideshow_service, schema=START_SLIDESHOW_SCHEMA)
    hass.services.async_register(DOMAIN, "stop_slideshow", stop_slideshow_service)
    hass.services.async_register(DOMAIN, "reset_resume", reset_resume_service)
    hass.services.async_register(DOMAIN, "photo_of_the_day", photo_of_the_day_service)
    hass.services.async_register(DOMAIN, "pause_slideshow", pause_slideshow_service, schema=PAUSE_RESUME_SCHEMA)
    hass.services.async_register(DOMAIN, "resume_slideshow", resume_slideshow_service, schema=PAUSE_RESUME_SCHEMA)

    # Register WebSlideshow services
    hass.services.async_register(DOMAIN, "start_webslideshow", start_webslideshow_service)
    hass.services.async_register(DOMAIN, "stop_webslideshow", stop_webslideshow_service)

    # Register WebSlideshow HTTP views
    hass.http.register_view(WebSlideshowView())
    hass.http.register_view(WebSlideshowCurrentView())
    hass.http.register_view(WebSlideshowWeatherView())
    hass.http.register_view(WebFileView())

    return True
