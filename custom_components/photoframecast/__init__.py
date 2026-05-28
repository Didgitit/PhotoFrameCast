import asyncio
import io
import logging
import math
from pathlib import Path

import voluptuous as vol
from aiohttp import web
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.integration_platform import async_process_integration_platforms
from homeassistant.helpers.storage import Store
from homeassistant.helpers import config_validation as cv
from datetime import datetime, timedelta

from .services import start_slideshow_service, stop_slideshow_service, reset_resume_service, photo_of_the_day_service, pause_slideshow_service, resume_slideshow_service, PAUSE_RESUME_SCHEMA, START_SLIDESHOW_SCHEMA
from .helpers import notify_user
from .const import DOMAIN, STORAGE_KEY, STORAGE_VERSION
from .webslideshow import start_webslideshow_service, stop_webslideshow_service, WebSlideshowView, WebSlideshowCurrentView, WebFileView


_LOGGER = logging.getLogger(__name__)

WEATHER_ENTITY = "weather.nanaimo_forecast"

# CONFIG_SCHEMA remains unchanged
CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)


# ----------------- Weather Icon Drawing ----------------- #

def _draw_shadow(draw, draw_fn, offset, *args, **kwargs):
    """Call draw_fn twice: once offset in black (shadow), once at original position in white."""
    draw_fn(draw, *args, offset=offset, color=(0, 0, 0, 180), **kwargs)
    draw_fn(draw, *args, offset=(0, 0), color=(255, 255, 255, 255), **kwargs)


def _circle(draw, cx, cy, r, offset=(0, 0), color=(255, 255, 255, 255), fill=True):
    ox, oy = offset
    bbox = [cx - r + ox, cy - r + oy, cx + r + ox, cy + r + oy]
    if fill:
        draw.ellipse(bbox, fill=color)
    else:
        draw.ellipse(bbox, outline=color, width=max(2, r // 6))


def _sun(draw, cx, cy, radius, offset=(0, 0), color=(255, 255, 255, 255)):
    """Sun: filled circle + 8 rays."""
    ox, oy = offset
    core_r = int(radius * 0.45)
    ray_inner = int(radius * 0.55)
    ray_outer = int(radius * 0.95)
    lw = max(2, radius // 10)

    draw.ellipse(
        [cx - core_r + ox, cy - core_r + oy, cx + core_r + ox, cy + core_r + oy],
        fill=color
    )
    for i in range(8):
        angle = math.radians(i * 45)
        x1 = cx + int(math.cos(angle) * ray_inner) + ox
        y1 = cy + int(math.sin(angle) * ray_inner) + oy
        x2 = cx + int(math.cos(angle) * ray_outer) + ox
        y2 = cy + int(math.sin(angle) * ray_outer) + oy
        draw.line([(x1, y1), (x2, y2)], fill=color, width=lw)


def _moon(draw, cx, cy, radius, offset=(0, 0), color=(255, 255, 255, 255)):
    """Crescent moon: large circle minus offset circle."""
    from PIL import Image, ImageDraw
    ox, oy = offset
    # Draw onto a temp mask to create crescent
    size = radius * 4
    tmp = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    tcx, tcy = size // 2, size // 2
    r = radius
    # Main moon circle
    td.ellipse([tcx - r, tcy - r, tcx + r, tcy + r], fill=color)
    # Bite out of it (offset to upper-right, drawn in transparent)
    bite = int(r * 0.75)
    bx = tcx + int(r * 0.35)
    by = tcy - int(r * 0.25)
    td.ellipse([bx - bite, by - bite, bx + bite, by + bite], fill=(0, 0, 0, 0))

    # Paste onto main image
    paste_x = cx - size // 2 + ox
    paste_y = cy - size // 2 + oy
    draw._image.paste(tmp, (paste_x, paste_y), tmp)


def _cloud(draw, cx, cy, radius, offset=(0, 0), color=(255, 255, 255, 255)):
    """Simple cloud: three overlapping filled ellipses."""
    ox, oy = offset
    r = radius
    # Main body
    draw.ellipse([cx - r + ox, cy - int(r * 0.4) + oy,
                  cx + r + ox, cy + int(r * 0.5) + oy], fill=color)
    # Left bump
    draw.ellipse([cx - int(r * 0.9) + ox, cy - int(r * 0.6) + oy,
                  cx - int(r * 0.1) + ox, cy + int(r * 0.2) + oy], fill=color)
    # Right bump
    draw.ellipse([cx + int(r * 0.1) + ox, cy - int(r * 0.7) + oy,
                  cx + int(r * 0.8) + ox, cy + int(r * 0.1) + oy], fill=color)


def _rain_drops(draw, cx, cy, radius, offset=(0, 0), color=(255, 255, 255, 255)):
    """Three short diagonal rain lines below a centre point."""
    ox, oy = offset
    lw = max(2, radius // 8)
    drop_len = int(radius * 0.5)
    spacing = int(radius * 0.4)
    base_y = cy + int(radius * 0.45)
    for i in range(3):
        bx = cx - spacing + i * spacing + ox
        by = base_y + oy
        draw.line([(bx, by), (bx - int(drop_len * 0.3), by + drop_len)],
                  fill=color, width=lw)


def _snow_dots(draw, cx, cy, radius, offset=(0, 0), color=(255, 255, 255, 255)):
    """Six small dots in a snowflake pattern below centre."""
    ox, oy = offset
    dot_r = max(2, radius // 10)
    base_y = cy + int(radius * 0.45)
    for i in range(3):
        angle = math.radians(i * 60)
        dx = int(math.cos(angle) * radius * 0.35)
        dy = int(math.sin(angle) * radius * 0.25)
        for sign in (1, -1):
            px = cx + sign * dx + ox
            py = base_y + sign * dy + oy
            draw.ellipse([px - dot_r, py - dot_r, px + dot_r, py + dot_r], fill=color)


def _fog_lines(draw, cx, cy, radius, offset=(0, 0), color=(255, 255, 255, 255)):
    """Three horizontal lines of decreasing length."""
    ox, oy = offset
    lw = max(2, radius // 8)
    spacing = int(radius * 0.35)
    for i, width_factor in enumerate([0.9, 0.7, 0.5]):
        half = int(radius * width_factor)
        y = cy - spacing + i * spacing + oy
        draw.line([(cx - half + ox, y), (cx + half + ox, y)], fill=color, width=lw)


def _lightning_bolt(draw, cx, cy, radius, offset=(0, 0), color=(255, 255, 255, 255)):
    """Simple zigzag lightning bolt."""
    ox, oy = offset
    lw = max(2, radius // 7)
    # Bolt points: top-right → middle-left → bottom-right
    top_x = cx + int(radius * 0.15) + ox
    top_y = cy - int(radius * 0.1) + oy
    mid_x = cx - int(radius * 0.1) + ox
    mid_y = cy + int(radius * 0.15) + oy
    bot_x = cx + int(radius * 0.2) + ox
    bot_y = cy + int(radius * 0.55) + oy
    draw.line([(top_x, top_y), (mid_x, mid_y), (bot_x, bot_y)], fill=color, width=lw)


def _alert_triangle(draw, cx, cy, radius, offset=(0, 0), color=(255, 200, 0, 255)):
    """Exclamation mark in a triangle. Yellow to stand out."""
    ox, oy = offset
    lw = max(2, radius // 8)
    h = int(radius * 1.0)
    # Triangle
    pts = [
        (cx + ox, cy - h + oy),
        (cx - int(h * 0.65) + ox, cy + int(h * 0.4) + oy),
        (cx + int(h * 0.65) + ox, cy + int(h * 0.4) + oy),
    ]
    draw.polygon(pts, outline=color)
    # Exclamation stem
    draw.line([(cx + ox, cy - int(h * 0.45) + oy),
               (cx + ox, cy + int(h * 0.05) + oy)], fill=color, width=lw)
    # Dot
    dot_r = max(2, radius // 10)
    draw.ellipse([cx - dot_r + ox, cy + int(h * 0.15) + oy,
                  cx + dot_r + ox, cy + int(h * 0.28) + oy], fill=color)


def draw_weather_icon(draw, condition, cx, cy, radius):
    """
    Draw the appropriate weather icon centred at (cx, cy).
    condition is a Met.no / HA standard weather condition string.
    Shadow is drawn first (offset), then the white icon on top.
    """
    shadow = (max(2, radius // 20), max(2, radius // 20))

    if condition == "clear-night":
        _moon(draw, cx, cy + shadow[1], radius, offset=(0, 0), color=(0, 0, 0, 180))
        _moon(draw, cx, cy, radius)

    elif condition in ("sunny", "windy"):
        _sun(draw, cx, cy, radius, offset=shadow, color=(0, 0, 0, 180))
        _sun(draw, cx, cy, radius)

    elif condition in ("cloudy", "windy-variant"):
        _cloud(draw, cx, cy, radius, offset=shadow, color=(0, 0, 0, 180))
        _cloud(draw, cx, cy, radius)

    elif condition == "partlycloudy":
        # Sun/moon peeking behind cloud — sun offset up-left, cloud centred
        _sun(draw, cx - int(radius * 0.2), cy - int(radius * 0.2), int(radius * 0.65),
             offset=shadow, color=(0, 0, 0, 180))
        _sun(draw, cx - int(radius * 0.2), cy - int(radius * 0.2), int(radius * 0.65))
        _cloud(draw, cx + int(radius * 0.15), cy + int(radius * 0.1), int(radius * 0.75),
               offset=shadow, color=(0, 0, 0, 180))
        _cloud(draw, cx + int(radius * 0.15), cy + int(radius * 0.1), int(radius * 0.75))

    elif condition in ("rainy", "pouring", "snowy-rainy"):
        cloud_r = int(radius * 0.65)
        cloud_cy = cy - int(radius * 0.2)
        _cloud(draw, cx, cloud_cy, cloud_r, offset=shadow, color=(0, 0, 0, 180))
        _cloud(draw, cx, cloud_cy, cloud_r)
        if condition == "snowy-rainy":
            _snow_dots(draw, cx, cy + int(radius * 0.1), radius,
                       offset=shadow, color=(0, 0, 0, 180))
            _snow_dots(draw, cx, cy + int(radius * 0.1), radius)
        else:
            _rain_drops(draw, cx, cy + int(radius * 0.1), radius,
                        offset=shadow, color=(0, 0, 0, 180))
            _rain_drops(draw, cx, cy + int(radius * 0.1), radius)

    elif condition == "snowy":
        cloud_r = int(radius * 0.65)
        cloud_cy = cy - int(radius * 0.2)
        _cloud(draw, cx, cloud_cy, cloud_r, offset=shadow, color=(0, 0, 0, 180))
        _cloud(draw, cx, cloud_cy, cloud_r)
        _snow_dots(draw, cx, cy + int(radius * 0.1), radius,
                   offset=shadow, color=(0, 0, 0, 180))
        _snow_dots(draw, cx, cy + int(radius * 0.1), radius)

    elif condition == "fog":
        _fog_lines(draw, cx, cy, radius, offset=shadow, color=(0, 0, 0, 180))
        _fog_lines(draw, cx, cy, radius)

    elif condition in ("lightning", "lightning-rainy"):
        cloud_r = int(radius * 0.6)
        cloud_cy = cy - int(radius * 0.25)
        _cloud(draw, cx, cloud_cy, cloud_r, offset=shadow, color=(0, 0, 0, 180))
        _cloud(draw, cx, cloud_cy, cloud_r)
        _lightning_bolt(draw, cx, cy + int(radius * 0.05), radius,
                        offset=shadow, color=(0, 0, 0, 180))
        _lightning_bolt(draw, cx, cy + int(radius * 0.05), radius)

    elif condition == "exceptional":
        _alert_triangle(draw, cx, cy, radius, offset=shadow, color=(0, 0, 0, 180))
        _alert_triangle(draw, cx, cy, radius)

    else:
        # Unknown condition — draw a simple question-mark-ish dot
        r = max(3, radius // 4)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 255))


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

        # Fetch weather condition from HA state (safe — runs in async context)
        weather_condition = None
        try:
            weather_state = self.hass.states.get(WEATHER_ENTITY)
            if weather_state:
                weather_condition = weather_state.state  # e.g. "sunny", "rainy"
        except Exception:
            pass

        def stamp_image():
            from PIL import Image, ImageDraw, ImageFont
            img = Image.open(file_path).convert("RGB")
            draw = ImageDraw.Draw(img, "RGBA")
            now = datetime.now().strftime("%-I:%M %p")
            font_size = max(20, int(img.height * 0.06))
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
            except Exception:
                font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), now, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            margin_right = 95
            margin_bottom = 60

            # Clock position (unchanged from original)
            x = img.width - text_w - margin_right
            y = img.height - text_h - margin_bottom
            shadow_offset = max(2, font_size // 20)

            # Draw clock shadow + text
            draw.text((x + shadow_offset, y + shadow_offset), now, font=font, fill=(0, 0, 0, 180))
            draw.text((x, y), now, font=font, fill=(255, 255, 255, 255))

            # Draw weather icon to the left of the clock text
            if weather_condition:
                icon_radius = int(font_size * 0.55)
                icon_gap = int(font_size * 0.4)   # gap between icon and clock text
                icon_cx = x - icon_gap - icon_radius
                icon_cy = y + text_h // 2          # vertically centred on text

                draw_weather_icon(draw, weather_condition, icon_cx, icon_cy, icon_radius)

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
    hass.http.register_view(WebFileView())

    return True
