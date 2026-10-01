"""
Generates the application icon (assets/app.ico).

Draws a clean "recording" mark: a dark rounded square with a red record
dot and a small play/record accent. Exports a multi-resolution .ico so
Windows shows a crisp icon at every size (taskbar, Start Menu, Explorer).
"""

import os

from PIL import Image, ImageDraw

SIZES = [16, 24, 32, 48, 64, 128, 256]

BG_TOP = (30, 39, 46)      # dark slate
ACCENT = (9, 132, 227)     # blue ring
RECORD = (192, 57, 43)     # record red
RECORD_HI = (231, 76, 60)  # lighter red


def rounded_rect(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def render(size):
    """Render a single square icon image at the given size."""
    # Supersample for smooth edges, then downscale.
    scale = 4
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Background rounded square.
    margin = int(s * 0.06)
    rounded_rect(d, [margin, margin, s - margin, s - margin],
                 radius=int(s * 0.22), fill=BG_TOP)

    # Outer blue ring (camera/record framing).
    ring_margin = int(s * 0.20)
    ring_width = max(2, int(s * 0.05))
    d.ellipse(
        [ring_margin, ring_margin, s - ring_margin, s - ring_margin],
        outline=ACCENT, width=ring_width,
    )

    # Central red record dot with a lighter highlight.
    dot_margin = int(s * 0.33)
    d.ellipse(
        [dot_margin, dot_margin, s - dot_margin, s - dot_margin],
        fill=RECORD,
    )
    hi = int(s * 0.40)
    hi_size = int(s * 0.10)
    d.ellipse([hi, hi, hi + hi_size, hi + hi_size], fill=RECORD_HI)

    return img.resize((size, size), Image.LANCZOS)


def main():
    os.makedirs("assets", exist_ok=True)
    images = [render(sz) for sz in SIZES]
    out = os.path.join("assets", "app.ico")
    # Pillow writes a multi-size ICO from the largest image + sizes list.
    images[-1].save(out, format="ICO",
                    sizes=[(sz, sz) for sz in SIZES])
    print("Wrote", out)


if __name__ == "__main__":
    main()
