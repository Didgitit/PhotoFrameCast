---

### Clock & Weather Overlay

PhotoFrameCast can stamp a live clock and current weather icon directly onto photos as they are displayed. Both the cast slideshow and the web slideshow support this feature, though they implement it differently to suit each context.

---

#### Cast Slideshow Overlay (`__init__.py` + `weather_icons.py`)

When a photo is served to a Chromecast or Nest Hub, it passes through the `GlobalPhotoView` HTTP handler. Before the image is sent, it is opened with Pillow, the current time and a weather icon are drawn directly onto the image in memory, and the stamped JPEG is returned to the player. The original file on disk is never modified.

**What is drawn:**

- The current time in `H:MM AM/PM` format, positioned in the **bottom-right corner**.
- A weather icon drawn as **white vector art with a dark drop shadow**, immediately to the **left of the clock**, vertically centred on it.

**Weather icons** are rendered entirely with Pillow drawing primitives — no image assets required. Each condition maps to a composed illustration:

| Condition | Icon |
|---|---|
| `sunny` | Sun with 8 rays (swaps to moon at night) |
| `clear-night` | Crescent or phase-accurate moon |
| `partlycloudy` | Large sun or moon with a small cloud in the lower corner |
| `cloudy` / `windy-variant` | Sun or moon behind a larger foreground cloud |
| `windy` | Three tapered horizontal lines with right-side curls |
| `rainy` / `pouring` | Cloud with three diagonal rain lines |
| `snowy` | Cloud with six snowflake dots |
| `snowy-rainy` | Cloud with mixed snow dots |
| `fog` | Three horizontal lines of decreasing length |
| `lightning` / `lightning-rainy` | Cloud with a zigzag bolt |
| `exceptional` | Yellow exclamation-mark triangle |

**Moon phase awareness**

When the condition is `clear-night` or `sunny` at night, the moon icon reflects the actual current lunar phase. The integration reads `sensor.moon_phase` from HA and maps its state to one of seven rendered shapes:

| Phase state | Rendered shape |
|---|---|
| `full_moon` | Filled circle |
| `new_moon` | Circle outline only |
| `waxing_crescent`, `first_quarter`, `waxing_gibbous` | Right-lit crescent |
| `waning_gibbous`, `last_quarter`, `waning_crescent` | Left-lit crescent |

If the sensor is unavailable, a standard waxing crescent is used as a fallback.

**Personalization edit points:**

| What to change | Where |
|---|---|
| Weather entity | `WEATHER_ENTITY = "weather.forecast_home"` near the top of `__init__.py` |
| Moon phase sensor | `self.hass.states.get("sensor.moon_phase")` inside `GlobalPhotoView.get()` |
| Clock position | `margin_right` and `margin_bottom` inside `stamp_image()` |
| Clock font size | `font_size = max(20, int(img.height * 0.06))` — adjust the `0.06` multiplier |
| Clock font | The `ImageFont.truetype(...)` path — swap for any `.ttf` available on your system |
| Clock text colour | `fill=(255, 255, 255, 255)` in the `draw.text(...)` calls inside `stamp_image()` |
| Shadow colour / opacity | `fill=(0, 0, 0, 180)` in the shadow `draw.text(...)` call — adjust the `180` alpha |
| Icon size | `icon_radius = int(font_size * 0.45)` — adjust the multiplier |
| Gap between icon and clock | `icon_gap = int(font_size * 0.4)` — adjust the multiplier |
| Icon shapes / new conditions | The drawing helpers in `weather_icons.py` — `_sun`, `_moon`, `_cloud`, `_rain_drops`, etc. Add or modify as needed, then wire them up in `draw_weather_icon()` |

---

#### Web Slideshow Overlay (`webslideshow.py`)

The web slideshow renders its overlay entirely in the browser, keeping the server-side path lightweight. The clock and weather icon are HTML elements positioned over the photo with CSS, updated by JavaScript.

**What is shown:**

- A weather emoji followed by the current time in `H:MM AM/PM` format, displayed in the **bottom-right corner** inside a semi-transparent rounded pill.
- The clock updates every **60 seconds**; the weather emoji refreshes every **5 minutes** by polling a small local endpoint.

A dedicated HTTP endpoint serves the current weather condition at:

```
/api/photoframecast/webslideshow/weather
```

This reads `weather.forecast_home` from HA state and returns JSON like `{"condition": "sunny"}`. The browser maps this to an emoji using a built-in lookup table (`WEATHER_EMOJI` in the page's JavaScript).

**Personalization edit points:**

| What to change | Where |
|---|---|
| Weather entity | `WEATHER_ENTITY = "weather.forecast_home"` inside the `WebSlideshowWeatherView` class |
| Weather emoji mapping | The `WEATHER_EMOJI` JavaScript object in `WebSlideshowView` — add, remove, or swap emojis for any HA condition string |
| Overlay position | `.overlay-container` CSS — change `bottom` / `right`, or swap to `left` / `top` |
| Overlay appearance | `.overlay-container` CSS — adjust `font-size`, `background`, `padding`, `border-radius` |
| Clock update frequency | `setInterval(updateClock, 60000)` — value is in milliseconds |
| Weather update frequency | `setInterval(updateWeather, 300000)` — value is in milliseconds (default 5 minutes) |
