#!/usr/bin/env python3
"""Set Buzz kind-0 name (and optional avatar URL) using the slug's existing key.
Usage: 02-set-kind0-profile.py SLUG DISPLAY_NAME [AVATAR_URL]
Never prints the private key.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

RELAY = os.environ.get("BUZZ_RELAY_URL") or "https://buzz.example.com"


def priv(home: Path) -> str:
    envp = home / ".env"
    for ln in envp.read_text().splitlines():
        if ln.startswith("BUZZ_PRIVATE_KEY="):
            v = ln.split("=", 1)[1].strip()
            if v:
                return v
    raise SystemExit(f"no BUZZ_PRIVATE_KEY in {envp}")


def main() -> None:
    if len(sys.argv) not in (3, 4):
        raise SystemExit("usage: 02-set-kind0-profile.py SLUG DISPLAY_NAME [AVATAR_URL]")
    slug, name = sys.argv[1], sys.argv[2]
    avatar = sys.argv[3] if len(sys.argv) == 4 else None
    home = (
        Path.home() / ".hermes"
        if slug == "default"
        else Path.home() / ".hermes" / "profiles" / slug
    )
    key = priv(home)
    env = os.environ.copy()
    env["BUZZ_PRIVATE_KEY"] = key
    env["BUZZ_RELAY_URL"] = RELAY
    args = ["buzz", "users", "set-profile", "--name", name]
    if avatar:
        args += ["--avatar", avatar]
    p = subprocess.run(args, env=env, capture_output=True, text=True, timeout=30)
    out = ((p.stdout or "") + (p.stderr or "")).replace(key, "[PRIV]")
    print("set-profile rc", p.returncode, out[:500])
    p2 = subprocess.run(
        ["buzz", "users", "get", "--name", name],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    out2 = ((p2.stdout or "") + (p2.stderr or "")).replace(key, "[PRIV]")
    print("get rc", p2.returncode, out2[:800])
    if p.returncode != 0:
        raise SystemExit(p.returncode)


if __name__ == "__main__":
    main()
