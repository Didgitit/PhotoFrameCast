import math


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


def _wind_lines(draw, cx, cy, radius, offset=(0, 0), color=(255, 255, 255, 255)):
"""Three horizontal lines that taper and curl at the right end, indicating wind."""
ox, oy = offset
lw = max(2, radius // 8)
spacing = int(radius * 0.38)
lengths = [int(radius * 0.95), int(radius * 0.75), int(radius * 0.55)]
curl_radius = int(radius * 0.18)

for i, length in enumerate(lengths):
y = cy - spacing + i * spacing + oy
x_start = cx - int(radius * 0.5) + ox
x_end = cx - int(radius * 0.5) + length + ox

# Horizontal line
draw.line([(x_start, y), (x_end, y)], fill=color, width=lw)

# Curl at the end: small arc curling downward
draw.arc(
[x_end - curl_radius, y - curl_radius,
x_end + curl_radius, y + curl_radius],
start=270, end=90,
fill=color, width=lw
)


def draw_weather_icon(draw, condition, cx, cy, radius, is_night=False):
    """
    Draw the appropriate weather icon centred at (cx, cy).
    condition is a Met.no / HA standard weather condition string.
    is_night controls whether sun-based icons swap to moon equivalents.
    Shadow is drawn first (offset), then the white icon on top.
    """
    shadow = (max(2, radius // 20), max(2, radius // 20))

    if condition == "clear-night":
        _moon(draw, cx, cy + shadow[1], radius, offset=(0, 0), color=(0, 0, 0, 180))
        _moon(draw, cx, cy, radius)

    elif condition == "sunny":
        if is_night:
            _moon(draw, cx, cy + shadow[1], radius, offset=(0, 0), color=(0, 0, 0, 180))
            _moon(draw, cx, cy, radius)
        else:
            _sun(draw, cx, cy, radius, offset=shadow, color=(0, 0, 0, 180))
            _sun(draw, cx, cy, radius)

    elif condition == "windy":
        _wind_lines(draw, cx, cy, radius, offset=shadow, color=(0, 0, 0, 180))
        _wind_lines(draw, cx, cy, radius)

    elif condition in ("cloudy", "windy-variant"):
        # Sun or moon peeking behind cloud — formerly the partlycloudy look
        if is_night:
            _moon(draw, cx - int(radius * 0.2), cy - int(radius * 0.2), int(radius * 0.65),
                  offset=(0, 0), color=(0, 0, 0, 180))
            _moon(draw, cx - int(radius * 0.2), cy - int(radius * 0.2), int(radius * 0.65))
        else:
            _sun(draw, cx - int(radius * 0.2), cy - int(radius * 0.2), int(radius * 0.65),
                 offset=shadow, color=(0, 0, 0, 180))
            _sun(draw, cx - int(radius * 0.2), cy - int(radius * 0.2), int(radius * 0.65))
        _cloud(draw, cx + int(radius * 0.15), cy + int(radius * 0.1), int(radius * 0.75),
               offset=shadow, color=(0, 0, 0, 180))
        _cloud(draw, cx + int(radius * 0.15), cy + int(radius * 0.1), int(radius * 0.75))

    elif condition == "partlycloudy":
        # Prominent sun or moon with a small cloud drifting across the lower corner
        if is_night:
            _moon(draw, cx, cy - int(radius * 0.1), radius,
                  offset=(0, 0), color=(0, 0, 0, 180))
            _moon(draw, cx, cy - int(radius * 0.1), radius)
        else:
            _sun(draw, cx, cy - int(radius * 0.1), radius,
                 offset=shadow, color=(0, 0, 0, 180))
            _sun(draw, cx, cy - int(radius * 0.1), radius)
        _cloud(draw, cx + int(radius * 0.3), cy + int(radius * 0.45), int(radius * 0.5),
               offset=shadow, color=(0, 0, 0, 180))
        _cloud(draw, cx + int(radius * 0.3), cy + int(radius * 0.45), int(radius * 0.5))

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
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 255))        draw.line([(x1, y1), (x2, y2)], fill=color, width=lw)


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


def _wind_lines(draw, cx, cy, radius, offset=(0, 0), color=(255, 255, 255, 255)):
    """Three horizontal lines that taper and curl at the right end, indicating wind."""
    ox, oy = offset
    lw = max(2, radius // 8)
    spacing = int(radius * 0.38)
    lengths = [int(radius * 0.95), int(radius * 0.75), int(radius * 0.55)]
    curl_radius = int(radius * 0.18)

    for i, length in enumerate(lengths):
        y = cy - spacing + i * spacing + oy
        x_start = cx - int(radius * 0.5) + ox
        x_end = cx - int(radius * 0.5) + length + ox

        # Horizontal line
        draw.line([(x_start, y), (x_end, y)], fill=color, width=lw)

        # Curl at the end: small arc curling downward
        draw.arc(
            [x_end - curl_radius, y - curl_radius,
             x_end + curl_radius, y + curl_radius],
            start=270, end=90,
            fill=color, width=lw
        )


def draw_weather_icon(draw, condition, cx, cy, radius, is_night=False):
"""
   Draw the appropriate weather icon centred at (cx, cy).
   condition is a Met.no / HA standard weather condition string.
   is_night controls whether sun-based icons swap to moon equivalents.
   Shadow is drawn first (offset), then the white icon on top.
   """
shadow = (max(2, radius // 20), max(2, radius // 20))

if condition == "clear-night":
_moon(draw, cx, cy + shadow[1], radius, offset=(0, 0), color=(0, 0, 0, 180))
_moon(draw, cx, cy, radius)

elif condition == "sunny":
if is_night:
_moon(draw, cx, cy + shadow[1], radius, offset=(0, 0), color=(0, 0, 0, 180))
_moon(draw, cx, cy, radius)
else:
_sun(draw, cx, cy, radius, offset=shadow, color=(0, 0, 0, 180))
_sun(draw, cx, cy, radius)

elif condition == "windy":
_wind_lines(draw, cx, cy, radius, offset=shadow, color=(0, 0, 0, 180))
_wind_lines(draw, cx, cy, radius)

elif condition in ("cloudy", "windy-variant"):
_cloud(draw, cx, cy, radius, offset=shadow, color=(0, 0, 0, 180))
_cloud(draw, cx, cy, radius)

elif condition == "partlycloudy":
# Sun or moon peeking behind cloud depending on time of day
if is_night:
_moon(draw, cx - int(radius * 0.2), cy - int(radius * 0.2), int(radius * 0.65),
offset=(0, 0), color=(0, 0, 0, 180))
_moon(draw, cx - int(radius * 0.2), cy - int(radius * 0.2), int(radius * 0.65))
else:
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
draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 255))        draw.line([(x1, y1), (x2, y2)], fill=color, width=lw)


def _moon(draw, cx, cy, radius, offset=(0, 0), color=(255, 255, 255, 255), facing="waxing"):
    """Crescent moon: large circle minus offset circle.
    facing='waxing' lights the right side; facing='waning' lights the left.
    """
    from PIL import Image, ImageDraw
    ox, oy = offset
    size = radius * 4
    tmp = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    tcx, tcy = size // 2, size // 2
    r = radius
    td.ellipse([tcx - r, tcy - r, tcx + r, tcy + r], fill=color)
    bite = int(r * 0.75)
    # Waxing: bite from the left; waning: bite from the right
    if facing == "waxing":
        bx = tcx - int(r * 0.35)
    else:
        bx = tcx + int(r * 0.35)
    by = tcy - int(r * 0.25)
    td.ellipse([bx - bite, by - bite, bx + bite, by + bite], fill=(0, 0, 0, 0))

    paste_x = cx - size // 2 + ox
    paste_y = cy - size // 2 + oy
    draw._image.paste(tmp, (paste_x, paste_y), tmp)


def _full_moon(draw, cx, cy, radius, offset=(0, 0), color=(255, 255, 255, 255)):
    """Full moon: plain filled circle."""
    ox, oy = offset
    draw.ellipse([cx - radius + ox, cy - radius + oy,
                  cx + radius + ox, cy + radius + oy], fill=color)


def _new_moon(draw, cx, cy, radius, offset=(0, 0), color=(255, 255, 255, 255)):
    """New moon: circle outline only."""
    ox, oy = offset
    lw = max(2, radius // 8)
    draw.ellipse([cx - radius + ox, cy - radius + oy,
                  cx + radius + ox, cy + radius + oy], outline=color, width=lw)


def _cloud(draw, cx, cy, radius, offset=(0, 0), color=(255, 255, 255, 255)):
    """Simple cloud: three overlapping filled ellipses."""
    ox, oy = offset
    r = radius
    draw.ellipse([cx - r + ox, cy - int(r * 0.4) + oy,
                  cx + r + ox, cy + int(r * 0.5) + oy], fill=color)
    draw.ellipse([cx - int(r * 0.9) + ox, cy - int(r * 0.6) + oy,
                  cx - int(r * 0.1) + ox, cy + int(r * 0.2) + oy], fill=color)
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
    pts = [
        (cx + ox, cy - h + oy),
        (cx - int(h * 0.65) + ox, cy + int(h * 0.4) + oy),
        (cx + int(h * 0.65) + ox, cy + int(h * 0.4) + oy),
    ]
    draw.polygon(pts, outline=color)
    draw.line([(cx + ox, cy - int(h * 0.45) + oy),
               (cx + ox, cy + int(h * 0.05) + oy)], fill=color, width=lw)
    dot_r = max(2, radius // 10)
    draw.ellipse([cx - dot_r + ox, cy + int(h * 0.15) + oy,
                  cx + dot_r + ox, cy + int(h * 0.28) + oy], fill=color)


def _wind_lines(draw, cx, cy, radius, offset=(0, 0), color=(255, 255, 255, 255)):
    """Three horizontal lines that taper and curl at the right end, indicating wind."""
    ox, oy = offset
    lw = max(2, radius // 8)
    spacing = int(radius * 0.38)
    lengths = [int(radius * 0.95), int(radius * 0.75), int(radius * 0.55)]
    curl_radius = int(radius * 0.18)

    for i, length in enumerate(lengths):
        y = cy - spacing + i * spacing + oy
        x_start = cx - int(radius * 0.5) + ox
        x_end = cx - int(radius * 0.5) + length + ox

        draw.line([(x_start, y), (x_end, y)], fill=color, width=lw)
        draw.arc(
            [x_end - curl_radius, y - curl_radius,
             x_end + curl_radius, y + curl_radius],
            start=270, end=90,
            fill=color, width=lw
        )


def _draw_moon_for_phase(draw, cx, cy, radius, offset, shadow_color, moon_phase):
    """Draw the correct moon primitive for the given phase, with shadow."""
    if moon_phase == "full_moon":
        _full_moon(draw, cx, cy, radius, offset=offset, color=shadow_color)
        _full_moon(draw, cx, cy, radius)
    elif moon_phase == "new_moon":
        _new_moon(draw, cx, cy, radius, offset=offset, color=shadow_color)
        _new_moon(draw, cx, cy, radius)
    elif moon_phase in ("waxing_crescent", "first_quarter", "waxing_gibbous"):
        _moon(draw, cx, cy, radius, offset=offset, color=shadow_color, facing="waxing")
        _moon(draw, cx, cy, radius, facing="waxing")
    else:
        # waning_crescent, last_quarter, waning_gibbous, or unknown — default to waning crescent
        _moon(draw, cx, cy, radius, offset=offset, color=shadow_color, facing="waning")
        _moon(draw, cx, cy, radius, facing="waning")


def draw_weather_icon(draw, condition, cx, cy, radius, is_night=False, moon_phase=None):
    """
    Draw the appropriate weather icon centred at (cx, cy).
    condition is a Met.no / HA standard weather condition string.
    is_night controls whether sun-based icons swap to moon equivalents.
    moon_phase is the state of sensor.moon_phase; when provided and is_night
    is True, moon icons reflect the actual current phase.
    Shadow is drawn first (offset), then the white icon on top.
    """
    shadow = (max(2, radius // 20), max(2, radius // 20))
    shadow_color = (0, 0, 0, 180)

    if condition == "clear-night":
        _draw_moon_for_phase(draw, cx, cy, radius, shadow, shadow_color, moon_phase)

    elif condition == "sunny":
        if is_night:
            _draw_moon_for_phase(draw, cx, cy, radius, shadow, shadow_color, moon_phase)
        else:
            _sun(draw, cx, cy, radius, offset=shadow, color=shadow_color)
            _sun(draw, cx, cy, radius)

    elif condition == "windy":
        _wind_lines(draw, cx, cy, radius, offset=shadow, color=shadow_color)
        _wind_lines(draw, cx, cy, radius)

    elif condition in ("cloudy", "windy-variant"):
        # Moon or sun peeking behind cloud
        moon_cx = cx - int(radius * 0.2)
        moon_cy = cy - int(radius * 0.2)
        moon_r = int(radius * 0.65)
        if is_night:
            _draw_moon_for_phase(draw, moon_cx, moon_cy, moon_r, shadow, shadow_color, moon_phase)
        else:
            _sun(draw, moon_cx, moon_cy, moon_r, offset=shadow, color=shadow_color)
            _sun(draw, moon_cx, moon_cy, moon_r)
        _cloud(draw, cx + int(radius * 0.15), cy + int(radius * 0.1), int(radius * 0.75),
               offset=shadow, color=shadow_color)
        _cloud(draw, cx + int(radius * 0.15), cy + int(radius * 0.1), int(radius * 0.75))

    elif condition == "partlycloudy":
        # Prominent moon or sun with small cloud in lower corner
        main_cy = cy - int(radius * 0.1)
        if is_night:
            _draw_moon_for_phase(draw, cx, main_cy, radius, shadow, shadow_color, moon_phase)
        else:
            _sun(draw, cx, main_cy, radius, offset=shadow, color=shadow_color)
            _sun(draw, cx, main_cy, radius)
        _cloud(draw, cx + int(radius * 0.3), cy + int(radius * 0.45), int(radius * 0.5),
               offset=shadow, color=shadow_color)
        _cloud(draw, cx + int(radius * 0.3), cy + int(radius * 0.45), int(radius * 0.5))

    elif condition in ("rainy", "pouring", "snowy-rainy"):
        cloud_r = int(radius * 0.65)
        cloud_cy = cy - int(radius * 0.2)
        _cloud(draw, cx, cloud_cy, cloud_r, offset=shadow, color=shadow_color)
        _cloud(draw, cx, cloud_cy, cloud_r)
        if condition == "snowy-rainy":
            _snow_dots(draw, cx, cy + int(radius * 0.1), radius, offset=shadow, color=shadow_color)
            _snow_dots(draw, cx, cy + int(radius * 0.1), radius)
        else:
            _rain_drops(draw, cx, cy + int(radius * 0.1), radius, offset=shadow, color=shadow_color)
            _rain_drops(draw, cx, cy + int(radius * 0.1), radius)

    elif condition == "snowy":
        cloud_r = int(radius * 0.65)
        cloud_cy = cy - int(radius * 0.2)
        _cloud(draw, cx, cloud_cy, cloud_r, offset=shadow, color=shadow_color)
        _cloud(draw, cx, cloud_cy, cloud_r)
        _snow_dots(draw, cx, cy + int(radius * 0.1), radius, offset=shadow, color=shadow_color)
        _snow_dots(draw, cx, cy + int(radius * 0.1), radius)

    elif condition == "fog":
        _fog_lines(draw, cx, cy, radius, offset=shadow, color=shadow_color)
        _fog_lines(draw, cx, cy, radius)

    elif condition in ("lightning", "lightning-rainy"):
        cloud_r = int(radius * 0.6)
        cloud_cy = cy - int(radius * 0.25)
        _cloud(draw, cx, cloud_cy, cloud_r, offset=shadow, color=shadow_color)
        _cloud(draw, cx, cloud_cy, cloud_r)
        _lightning_bolt(draw, cx, cy + int(radius * 0.05), radius, offset=shadow, color=shadow_color)
        _lightning_bolt(draw, cx, cy + int(radius * 0.05), radius)

    elif condition == "exceptional":
        _alert_triangle(draw, cx, cy, radius, offset=shadow, color=shadow_color)
        _alert_triangle(draw, cx, cy, radius)

    else:
        # Unknown condition — draw a simple dot
        r = max(3, radius // 4)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 255))        draw.line([(x1, y1), (x2, y2)], fill=color, width=lw)


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


def _wind_lines(draw, cx, cy, radius, offset=(0, 0), color=(255, 255, 255, 255)):
    """Three horizontal lines that taper and curl at the right end, indicating wind."""
    ox, oy = offset
    lw = max(2, radius // 8)
    spacing = int(radius * 0.38)
    lengths = [int(radius * 0.95), int(radius * 0.75), int(radius * 0.55)]
    curl_radius = int(radius * 0.18)

    for i, length in enumerate(lengths):
        y = cy - spacing + i * spacing + oy
        x_start = cx - int(radius * 0.5) + ox
        x_end = cx - int(radius * 0.5) + length + ox

        # Horizontal line
        draw.line([(x_start, y), (x_end, y)], fill=color, width=lw)

        # Curl at the end: small arc curling downward
        draw.arc(
            [x_end - curl_radius, y - curl_radius,
             x_end + curl_radius, y + curl_radius],
            start=270, end=90,
            fill=color, width=lw
        )


def draw_weather_icon(draw, condition, cx, cy, radius, is_night=False):
    """
    Draw the appropriate weather icon centred at (cx, cy).
    condition is a Met.no / HA standard weather condition string.
    is_night controls whether sun-based icons swap to moon equivalents.
    Shadow is drawn first (offset), then the white icon on top.
    """
    shadow = (max(2, radius // 20), max(2, radius // 20))

    if condition == "clear-night":
        _moon(draw, cx, cy + shadow[1], radius, offset=(0, 0), color=(0, 0, 0, 180))
        _moon(draw, cx, cy, radius)

    elif condition == "sunny":
        if is_night:
            _moon(draw, cx, cy + shadow[1], radius, offset=(0, 0), color=(0, 0, 0, 180))
            _moon(draw, cx, cy, radius)
        else:
            _sun(draw, cx, cy, radius, offset=shadow, color=(0, 0, 0, 180))
            _sun(draw, cx, cy, radius)

    elif condition == "windy":
        _wind_lines(draw, cx, cy, radius, offset=shadow, color=(0, 0, 0, 180))
        _wind_lines(draw, cx, cy, radius)

    elif condition in ("cloudy", "windy-variant"):
        # Sun or moon peeking behind cloud — formerly the partlycloudy look
        if is_night:
            _moon(draw, cx - int(radius * 0.2), cy - int(radius * 0.2), int(radius * 0.65),
                  offset=(0, 0), color=(0, 0, 0, 180))
            _moon(draw, cx - int(radius * 0.2), cy - int(radius * 0.2), int(radius * 0.65))
        else:
            _sun(draw, cx - int(radius * 0.2), cy - int(radius * 0.2), int(radius * 0.65),
                 offset=shadow, color=(0, 0, 0, 180))
            _sun(draw, cx - int(radius * 0.2), cy - int(radius * 0.2), int(radius * 0.65))
        _cloud(draw, cx + int(radius * 0.15), cy + int(radius * 0.1), int(radius * 0.75),
               offset=shadow, color=(0, 0, 0, 180))
        _cloud(draw, cx + int(radius * 0.15), cy + int(radius * 0.1), int(radius * 0.75))

    elif condition == "partlycloudy":
        # Prominent sun or moon with a small cloud drifting across the lower corner
        if is_night:
            _moon(draw, cx, cy - int(radius * 0.1), radius,
                  offset=(0, 0), color=(0, 0, 0, 180))
            _moon(draw, cx, cy - int(radius * 0.1), radius)
        else:
            _sun(draw, cx, cy - int(radius * 0.1), radius,
                 offset=shadow, color=(0, 0, 0, 180))
            _sun(draw, cx, cy - int(radius * 0.1), radius)
        _cloud(draw, cx + int(radius * 0.3), cy + int(radius * 0.45), int(radius * 0.5),
               offset=shadow, color=(0, 0, 0, 180))
        _cloud(draw, cx + int(radius * 0.3), cy + int(radius * 0.45), int(radius * 0.5))

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
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 255))        draw.line([(x1, y1), (x2, y2)], fill=color, width=lw)


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


def _wind_lines(draw, cx, cy, radius, offset=(0, 0), color=(255, 255, 255, 255)):
    """Three horizontal lines that taper and curl at the right end, indicating wind."""
    ox, oy = offset
    lw = max(2, radius // 8)
    spacing = int(radius * 0.38)
    lengths = [int(radius * 0.95), int(radius * 0.75), int(radius * 0.55)]
    curl_radius = int(radius * 0.18)

    for i, length in enumerate(lengths):
        y = cy - spacing + i * spacing + oy
        x_start = cx - int(radius * 0.5) + ox
        x_end = cx - int(radius * 0.5) + length + ox

        # Horizontal line
        draw.line([(x_start, y), (x_end, y)], fill=color, width=lw)

        # Curl at the end: small arc curling downward
        draw.arc(
            [x_end - curl_radius, y - curl_radius,
             x_end + curl_radius, y + curl_radius],
            start=270, end=90,
            fill=color, width=lw
        )


def draw_weather_icon(draw, condition, cx, cy, radius, is_night=False):
    """
    Draw the appropriate weather icon centred at (cx, cy).
    condition is a Met.no / HA standard weather condition string.
    is_night controls whether sun-based icons swap to moon equivalents.
    Shadow is drawn first (offset), then the white icon on top.
    """
    shadow = (max(2, radius // 20), max(2, radius // 20))

    if condition == "clear-night":
        _moon(draw, cx, cy + shadow[1], radius, offset=(0, 0), color=(0, 0, 0, 180))
        _moon(draw, cx, cy, radius)

    elif condition == "sunny":
        if is_night:
            _moon(draw, cx, cy + shadow[1], radius, offset=(0, 0), color=(0, 0, 0, 180))
            _moon(draw, cx, cy, radius)
        else:
            _sun(draw, cx, cy, radius, offset=shadow, color=(0, 0, 0, 180))
            _sun(draw, cx, cy, radius)

    elif condition == "windy":
        _wind_lines(draw, cx, cy, radius, offset=shadow, color=(0, 0, 0, 180))
        _wind_lines(draw, cx, cy, radius)

    elif condition in ("cloudy", "windy-variant"):
        _cloud(draw, cx, cy, radius, offset=shadow, color=(0, 0, 0, 180))
        _cloud(draw, cx, cy, radius)

    elif condition == "partlycloudy":
        # Sun or moon peeking behind cloud depending on time of day
        if is_night:
            _moon(draw, cx - int(radius * 0.2), cy - int(radius * 0.2), int(radius * 0.65),
                  offset=(0, 0), color=(0, 0, 0, 180))
            _moon(draw, cx - int(radius * 0.2), cy - int(radius * 0.2), int(radius * 0.65))
        else:
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
