"""news-image-20261123 entry (V1 broadsheet): copy the finished front-page
image to the output folder as entry.png.

Stdlib only, no network. The image ships beside this program as image.jpg
(1024x1024 JPEG, <= 1 MiB). This program writes the bytes DIRECTLY to
$MAKEFUN_OUTPUT_DIR/entry.png -- no temporary file, no atomic rename, and
no dotfile is ever created inside the output folder (the grader rejects
dotfiles in /output; a mkstemp-based write got the 21 Nov slot 1 rejected).

Usage:
    MAKEFUN_OUTPUT_DIR=out python3 main.py   # write entry.png
    python3 main.py --check                   # validate image.jpg only
"""

import hashlib
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(BASE, "image.jpg")
SIZE_LIMIT = 1024 * 1024
WANT_WIDTH = 1024
WANT_HEIGHT = 1024

# SOF markers that carry width/height (baseline, extended, progressive).
SOF_MARKERS = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}


def read_jpeg_size(data):
    """Return (width, height) from a JPEG's first SOF segment."""
    if len(data) < 4 or data[0] != 0xFF or data[1] != 0xD8:
        raise ValueError("not a JPEG (missing SOI marker)")
    pos = 2
    while pos + 9 <= len(data):
        if data[pos] != 0xFF:
            raise ValueError("bad JPEG marker at offset %d" % pos)
        marker = data[pos + 1]
        if marker == 0xD9:  # EOI
            break
        if marker == 0xDA:  # SOS: image data follows, no more headers
            break
        if pos + 4 > len(data):
            break
        seg_len = (data[pos + 2] << 8) | data[pos + 3]
        if marker in SOF_MARKERS:
            height = (data[pos + 5] << 8) | data[pos + 6]
            width = (data[pos + 7] << 8) | data[pos + 8]
            return width, height
        pos += 2 + seg_len
    raise ValueError("no SOF segment found in JPEG")


def load_image():
    with open(IMAGE_PATH, "rb") as fh:
        data = fh.read()
    if len(data) > SIZE_LIMIT:
        raise ValueError("image.jpg is %d bytes, over the 1 MiB limit"
                         % len(data))
    if data[-2:] != b"\xff\xd9":
        raise ValueError("image.jpg is truncated (missing EOI marker)")
    width, height = read_jpeg_size(data)
    if (width, height) != (WANT_WIDTH, WANT_HEIGHT):
        raise ValueError("image.jpg is %dx%d, expected %dx%d"
                         % (width, height, WANT_WIDTH, WANT_HEIGHT))
    return data


def main(argv):
    if "--check" in argv:
        data = load_image()
        print("image.jpg OK: %d bytes, %dx%d, sha256 %s"
              % (len(data), WANT_WIDTH, WANT_HEIGHT,
                 hashlib.sha256(data).hexdigest()))
        return 0
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not outdir:
        sys.stderr.write("MAKEFUN_OUTPUT_DIR is not set\n")
        return 2
    data = load_image()
    os.makedirs(outdir, exist_ok=True)
    target = os.path.join(outdir, "entry.png")
    with open(target, "wb") as fh:
        fh.write(data)
    print("wrote %s (%d bytes, sha256 %s)"
          % (target, len(data), hashlib.sha256(data).hexdigest()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
