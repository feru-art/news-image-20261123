"""news-image-20261123 V6 — 'Democrats Retake the House' broadsheet.

Writes the pre-rendered front-page image for 23 November 2026 to
$MAKEFUN_OUTPUT_DIR/entry.png. The image itself is the entry; this
program only copies its bytes, unchanged, so both runs are identical.
"""

import os
import shutil
import sys


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "image.jpg")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    with open(src, "rb") as f:
        data = f.read()
    if len(data) > 1048576:
        print("image over 1 MiB", file=sys.stderr)
        return 1
    if data[:3] != b"\xff\xd8\xff":
        print("image is not a JPEG", file=sys.stderr)
        return 1
    if data[-2:] != b"\xff\xd9":
        print("image is not a whole JPEG", file=sys.stderr)
        return 1
    with open(dst, "wb") as f:
        f.write(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
