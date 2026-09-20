#!/usr/bin/env python3
"""Render the Impressum contact details as a deliberately distorted PNG so
the address and e-mail are readable by people but not by scrapers.
Usage: gen_contact_image.py "line1" "line2" ... > public/img/contact.png
The text is passed on the command line on purpose: it must not live in the
repository as plain text."""
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT = "/usr/share/fonts/truetype/msttcorefonts/comicbd.ttf"
SIZE = 30
lines = sys.argv[1:] or sys.exit("usage: gen_contact_image.py line...")
random.seed(sum(map(len, lines)))
font = ImageFont.truetype(FONT, SIZE)

W, H = 620, 52 * len(lines) + 30
img = Image.new("L", (W, H), 255)
draw = ImageDraw.Draw(img)

# Per-character jitter: position, size and rotation vary a little each time.
y = 20
for line in lines:
    x = 24
    for ch in line:
        if ch == " ":
            x += 12; continue
        f = ImageFont.truetype(FONT, SIZE + random.randint(-3, 4))
        box = f.getbbox(ch)
        cw, chh = box[2] - box[0] + 6, box[3] - box[1] + 6
        glyph = Image.new("L", (cw + 12, chh + 12), 255)
        ImageDraw.Draw(glyph).text((6 - box[0], 6 - box[1]), ch, font=f, fill=0)
        glyph = glyph.rotate(random.uniform(-9, 9), resample=Image.BICUBIC, fillcolor=255)
        img.paste(glyph, (x, y + box[1] + random.randint(-3, 3)), Image.eval(glyph, lambda v: 255 - v))
        x += cw - 4
    y += 52 if line.strip() else 26

# Wave distortion, slight blur, noise and specks.
src = img.load()
out = Image.new("L", (W, H), 255)
dst = out.load()
import math
for yy in range(H):
    for xx in range(W):
        sx = int(xx + 3 * math.sin(yy / 11.0))
        sy = int(yy + 2 * math.sin(xx / 17.0))
        if 0 <= sx < W and 0 <= sy < H:
            dst[xx, yy] = src[sx, sy]
out = out.filter(ImageFilter.GaussianBlur(0.7))
px = out.load()
for _ in range(W * H // 12):
    xx, yy = random.randrange(W), random.randrange(H)
    px[xx, yy] = max(0, min(255, px[xx, yy] + random.randint(-70, 70)))
d = ImageDraw.Draw(out)
for _ in range(12):
    x0, y0 = random.randrange(W), random.randrange(H)
    d.line((x0, y0, x0 + random.randint(-40, 40), y0 + random.randint(-15, 15)), fill=random.randint(120, 200), width=1)
out = out.filter(ImageFilter.GaussianBlur(0.4))
out.save(sys.stdout.buffer, "PNG")
