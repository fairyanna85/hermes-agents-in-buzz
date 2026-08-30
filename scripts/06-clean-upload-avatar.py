#!/usr/bin/env python3
"""Strip image metadata, upload to Buzz Blossom, set kind-0 avatar.

Usage: 06-clean-upload-avatar.py SLUG DISPLAY_NAME /path/to/image.png-or-jpg

Relay 422 if JPEG has extra metadata channels. This opens the file, converts
to RGB, center-crops square, resizes to 1024, saves a clean JPEG, uploads
with that slug's BUZZ_PRIVATE_KEY (never printed), then set-profile --avatar.

Requires Pillow (Hermes venv has it):
  /Users/YOURUSER/.hermes/hermes-agent/.venv/bin/python 06-clean-upload-avatar.py ...
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image

RELAY = os.environ.get("BUZZ_RELAY_URL") or "https://buzz.example.com"


def priv(home: Path) -> str:
    envp = home / ".env"
    for ln in envp.read_text().splitlines():
        if ln.startswith("BUZZ_PRIVATE_KEY="):
            v = ln.split("=", 1)[1].strip().strip('"')
            if v:
                return v
    raise SystemExit("no BUZZ_PRIVATE_KEY in " + str(envp))


def clean_jpeg(src: Path, dest: Path) -> None:
    im = Image.open(src).convert("RGB")
    w, h = im.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    im = im.crop((left, top, left + side, top + side))
    if side > 1024:
        im = im.resize((1024, 1024), Image.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "JPEG", quality=90, optimize=True)


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("usage: 06-clean-upload-avatar.py SLUG DISPLAY_NAME /path/to/image")
    slug, name, src_s = sys.argv[1], sys.argv[2], sys.argv[3]
    src = Path(src_s).expanduser()
    if not src.is_file():
        raise SystemExit("no image " + str(src))
    home = (
        Path.home() / ".hermes"
        if slug == "default"
        else Path.home() / ".hermes" / "profiles" / slug
    )
    key = priv(home)
    dest = Path("/tmp/olympus-avatars") / (slug + "-clean.jpg")
    clean_jpeg(src, dest)
    print("clean", dest, dest.stat().st_size)

    env = os.environ.copy()
    env["BUZZ_PRIVATE_KEY"] = key
    env["BUZZ_RELAY_URL"] = RELAY
    r = subprocess.run(
        ["buzz", "upload", "file", "--file", str(dest)],
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    out = ((r.stdout or "") + (r.stderr or "")).replace(key, "[PRIV]")
    print("upload rc", r.returncode)
    print(out[:800])
    if r.returncode != 0:
        raise SystemExit(r.returncode)
    data = json.loads(r.stdout)
    url = data.get("url")
    if not url:
        raise SystemExit("upload json had no url")
    print("AVATAR_URL", url)
    r2 = subprocess.run(
        ["buzz", "users", "set-profile", "--name", name, "--avatar", url],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    print("set-profile rc", r2.returncode, ((r2.stdout or "") + (r2.stderr or "")).replace(key, "[PRIV]")[:400])
    r3 = subprocess.run(
        ["buzz", "users", "get", "--name", name],
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
    )
    got = ((r3.stdout or "") + (r3.stderr or "")).replace(key, "[PRIV]")
    print("get", got[:800])
    if "picture" not in got:
        raise SystemExit("users get has no picture")
    if r2.returncode != 0:
        raise SystemExit(r2.returncode)


if __name__ == "__main__":
    main()
