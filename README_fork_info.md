---

### Clock & Weather Overlay

PhotoFrameCast can stamp a live clock and current weather icon directly onto photos as they are displayed. Both the cast slideshow and the web slideshow support this feature, though they implement it differently to suit each context.

---

#### Cast Slideshow Overlay (`__init__.py`)

When a photo is served to a Chromecast or Nest Hub, it passes through the `GlobalPhotoView` HTTP handler. Before the image is sent, it is opened with Pillow, the current time and a weather icon are drawn directly onto the image in memory, and the stamped JPEG is returned to the player. The original file on disk is never modified.

**What is drawn:**

- The current time in `H:MM AM/PM` format, positioned in the **bottom-right corner**.
- A weather icon (drawn as white vector art with a dark drop shadow) immediately to the **left of the clock**, vertically centred on it.

**Personalization edit points in `__init__.py`:**

| What to change | Where to find it |
|---|---|
| Weather entity | `WEATHER_ENTITY = "weather.forecast_home"` near the top of the file — change to match your own HA weather entity ID |
| Clock position | `margin_right` and `margin_bottom` variables inside `stamp_image()` |
| Clock font size | `font_size = max(20, int(img.height * 0.06))` — adjust the `0.06` multiplier |
| Clock font | The `ImageFont.truetype(...)` path — swap for any `.ttf` font available on your system |
| Clock text colour | `fill=(255, 255, 255, 255)` in the `draw.text(...)` calls inside `stamp_image()` |
| Shadow colour / opacity | `fill=(0, 0, 0, 180)` in the shadow `draw.text(...)` call — adjust the `180` alpha value |
| Icon size | `icon_radius = int(font_size * 0.55)` — adjust the multiplier |
| Gap between icon and clock | `icon_gap = int(font_size * 0.4)` — adjust the multiplier |
| Weather conditions covered | The `draw_weather_icon()` function and the individual `_sun`, `_cloud`, `_rain_drops` etc. drawing helpers — add or modify conditions as needed |

---

#### Web Slideshow Overlay (`webslideshow.py`)

The web slideshow renders its overlay entirely in the browser, keeping the server-side path lightweight. The clock and weather icon are HTML elements positioned over the photo with CSS, updated by JavaScript.

**What is shown:**

- A weather emoji in the **bottom-right corner**, followed by the current time in `H:MM AM/PM` format, inside a semi-transparent pill.
- The clock updates every **60 seconds**; the weather emoji refreshes every **5 minutes** by polling a small local endpoint.

A new HTTP endpoint, `WebSlideshowWeatherView`, serves the current weather condition at:

```
/api/photoframecast/webslideshow/weather
```

This endpoint reads `weather.forecast_home` from HA state and returns a JSON object like `{"condition": "sunny"}`. The browser maps this to an emoji using a built-in lookup table.

**Personalization edit points in `webslideshow.py`:**

| What to change | Where to find it |
|---|---|
| Weather entity | `WEATHER_ENTITY = "weather.forecast_home"` inside the `WebSlideshowWeatherView` class |
| Weather emoji mapping | The `WEATHER_EMOJI` JavaScript object in the `WebSlideshowView` HTML — add, remove or swap emojis for any HA weather condition string |
| Overlay position | `.overlay-container` CSS — change `bottom` / `right` values, or swap to `left` / `top` |
| Overlay appearance | `.overlay-container` CSS — adjust `font-size`, `background`, `padding`, `border-radius` |
| Clock update frequency | `setInterval(updateClock, 60000)` — value is in milliseconds |
| Weather update frequency | `setInterval(updateWeather, 300000)` — value is in milliseconds (default 5 minutes) |

---

#### Registering the new web weather endpoint (`__init__.py`)

The `WebSlideshowWeatherView` class must be imported and registered alongside the other web slideshow views. In `__init__.py`:

**Import line** (update the existing webslideshow import):
```python
from .webslideshow import (
    start_webslideshow_service,
    stop_webslideshow_service,
    WebSlideshowView,
    WebSlideshowCurrentView,
    WebSlideshowWeatherView,
    WebFileView,
)
```

**Registration** (add after the `WebSlideshowCurrentView` registration):
```python
hass.http.register_view(WebSlideshowWeatherView())
```
