"""Capture full-page screenshots via headless Chrome and slice them for review.

Development helper only — safe to delete.
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUT = Path(r"C:\Users\EKHTIY~1\AppData\Local\Temp\atlas-shots")
BASE = "http://127.0.0.1:8741"

# (slug, path, viewport width, full page height)
TARGETS = [
    ("fa-home", "/fa/", 1440, 8065),
    ("fa-company", "/fa/company/", 1440, 4474),
    ("fa-technologies", "/fa/technologies/", 1440, 4593),
    ("fa-industries", "/fa/industries/", 1440, 3087),
    ("fa-quality", "/fa/quality/", 1440, 4938),
    ("fa-products", "/fa/products/", 1440, 2382),
    ("fa-product-detail", "/fa/products/portable-emergency-oxygen-unit/", 1440, 3752),
    ("fa-tech-detail", "/fa/technologies/pressurised-gas-systems/", 1440, 2264),
    ("fa-insights", "/fa/insights/", 1440, 1870),
    ("fa-contact", "/fa/contact/", 1440, 2986),
    ("en-home", "/en/", 1440, 8460),
    ("en-product-detail", "/en/products/portable-emergency-oxygen-unit/", 1440, 3790),
    ("m-fa-home", "/fa/", 390, 14334),
    ("m-fa-products", "/fa/products/", 390, 3628),
    ("m-fa-product-detail", "/fa/products/portable-emergency-oxygen-unit/", 390, 5866),
]

SLICE = 1500          # review-friendly slice height
OVERLAP = 60          # keep a little context between slices


def capture(slug, path, width, height):
    raw = OUT / f"raw-{slug}.png"
    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
         "--force-device-scale-factor=1", f"--window-size={width},{height}",
         f"--screenshot={raw}", BASE + path],
        capture_output=True, timeout=180,
    )
    if not raw.exists():
        print(f"  !! capture failed: {slug}")
        return []
    im = Image.open(raw)
    parts, top, idx = [], 0, 1
    while top < im.height:
        bottom = min(top + SLICE, im.height)
        dest = OUT / f"{slug}-{idx:02d}.png"
        im.crop((0, top, im.width, bottom)).save(dest, optimize=True)
        parts.append(dest)
        if bottom >= im.height:
            break
        top = bottom - OVERLAP
        idx += 1
    raw.unlink()
    return parts


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.png"):
        old.unlink()
    wanted = sys.argv[1:]
    for slug, path, width, height in TARGETS:
        if wanted and slug not in wanted:
            continue
        parts = capture(slug, path, width, height)
        print(f"{slug}: {len(parts)} slice(s)")
        for p in parts:
            print("   ", p)


if __name__ == "__main__":
    main()
