"""Dynamic 1200x630 Open Graph PNG generator using Pillow."""

import io
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageOps

OG_WIDTH = 1200
OG_HEIGHT = 630

# Brand Palette
BG_DARK = (20, 18, 16)       # #141210 Espresso Charcoal
BG_CARD = (32, 28, 25)       # #201C19 Elevated Surface
ACCENT_EMBER = (217, 78, 40) # #D94E28 Terracotta Ember
ACCENT_GOLD = (229, 169, 60) # #E5A93C Saffron Gold
TEXT_CREAM = (250, 246, 240) # #FAF6F0 Warm Ivory
TEXT_MUTED = (186, 177, 166) # #BAB1A6 Warm Stone


def _load_font(static_dir: str, size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        os.path.join(static_dir, "fonts", "ChakraPetch-Regular.otf"),
        "C:/Windows/Fonts/segoeui.ttf" if not bold else "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arial.ttf" if not bold else "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _load_square_image(path: str, size: int, radius: int = 36) -> Image.Image | None:
    if not path or not os.path.exists(path):
        return None
    try:
        img = Image.open(path).convert("RGBA")
        fitted = ImageOps.fit(img, (size, size), method=Image.Resampling.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, size, size), radius=radius, fill=255)
        output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        output.paste(fitted, (0, 0), mask)
        return output
    except Exception:
        return None


def generate_og_image(
    static_dir: str,
    title: str,
    subtitle: str = "Wood-Fired Neapolitan Pizza & Fresh Hand-Rolled Sushi",
    eyebrow: str = "NIDEPIZZA • NETHERLANDS",
    badge: str | None = None,
    image_filename: str | None = None,
) -> bytes:
    """Render a branded 1200x630 PNG Open Graph card and return raw PNG bytes."""
    canvas = Image.new("RGBA", (OG_WIDTH, OG_HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(canvas)

    # Subtle decorative background card & accent bars
    draw.rounded_rectangle((36, 36, OG_WIDTH - 36, OG_HEIGHT - 36), radius=28, fill=BG_CARD, outline=(54, 48, 42), width=2)
    draw.rectangle((36, 36, 52, OG_HEIGHT - 36), fill=ACCENT_EMBER)

    # Fonts
    font_eyebrow = _load_font(static_dir, 22, bold=True)
    font_title = _load_font(static_dir, 54, bold=True)
    font_sub = _load_font(static_dir, 26, bold=False)
    font_badge = _load_font(static_dir, 28, bold=True)
    font_footer = _load_font(static_dir, 20, bold=False)

    # Right-side artwork (product image or hero pizza photo)
    img_path = None
    if image_filename:
        candidate = os.path.join(static_dir, "img", image_filename)
        if os.path.exists(candidate):
            img_path = candidate
    if not img_path:
        fallback = os.path.join(static_dir, "img", "pizza1.jpg")
        if os.path.exists(fallback):
            img_path = fallback

    art_size = 380
    art_x = OG_WIDTH - 36 - 48 - art_size
    art_y = (OG_HEIGHT - art_size) // 2

    art_img = _load_square_image(img_path, art_size, radius=28) if img_path else None
    if art_img:
        # Soft accent frame behind image
        draw.rounded_rectangle(
            (art_x - 8, art_y - 8, art_x + art_size + 8, art_y + art_size + 8),
            radius=32,
            outline=ACCENT_GOLD,
            width=3,
        )
        canvas.paste(art_img, (art_x, art_y), art_img)
        text_max_chars = 22
    else:
        text_max_chars = 34

    # Brand logo small top-left inside card
    left_x = 92
    top_y = 84
    logo_path = os.path.join(static_dir, "img", "pizza_logo.png")
    logo_img = _load_square_image(logo_path, 48, radius=12)
    if logo_img:
        canvas.paste(logo_img, (left_x, top_y - 8), logo_img)
        draw.text((left_x + 64, top_y + 4), eyebrow.upper(), font=font_eyebrow, fill=ACCENT_GOLD)
    else:
        draw.text((left_x, top_y), eyebrow.upper(), font=font_eyebrow, fill=ACCENT_GOLD)

    # Main Title (wrapped)
    wrapped_title = textwrap.wrap(title, width=text_max_chars)[:3]
    curr_y = 165
    for line in wrapped_title:
        draw.text((left_x, curr_y), line, font=font_title, fill=TEXT_CREAM)
        curr_y += 66

    # Subtitle (wrapped)
    curr_y += 14
    wrapped_sub = textwrap.wrap(subtitle, width=36)[:3]
    for line in wrapped_sub:
        draw.text((left_x, curr_y), line, font=font_sub, fill=TEXT_MUTED)
        curr_y += 36

    # Price or status pill
    if badge:
        pill_y = OG_HEIGHT - 145
        bbox = draw.textbbox((0, 0), badge, font=font_badge)
        pill_w = (bbox[2] - bbox[0]) + 48
        pill_h = 54
        draw.rounded_rectangle((left_x, pill_y, left_x + pill_w, pill_y + pill_h), radius=14, fill=ACCENT_EMBER)
        draw.text((left_x + 24, pill_y + 11), badge, font=font_badge, fill=TEXT_CREAM)

    # Bottom domain watermark
    draw.text((left_x, OG_HEIGHT - 78), "nidepizza.nl  •  iDEAL & Card Checkout  •  30-Min Delivery", font=font_footer, fill=TEXT_MUTED)

    out = io.BytesIO()
    canvas.convert("RGB").save(out, format="PNG", optimize=True)
    out.seek(0)
    return out.read()
