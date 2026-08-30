#!/usr/bin/env python3
"""Read-only: print SLUG + display name + pubkey prefix for each profile with Buzz.
Never prints BUZZ_PRIVATE_KEY. Does not change anything.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

HERMES = Path.home() / ".hermes"
RELAY = os.environ.get("BUZZ_RELAY_URL") or "https://buzz.example.com"


def profiles():
    yield "default", HERMES
    pdir = HERMES / "profiles"
    if pdir.is_dir():
        for d in sorted(pdir.iterdir()):
            if d.is_dir() and (d / "config.yaml").exists():
                yield d.name, d


def priv_from_env(home: Path) -> str | None:
    envp = home / ".env"
    if not envp.exists():
        return None
    for ln in envp.read_text(errors="replace").splitlines():
        if ln.startswith("BUZZ_PRIVATE_KEY="):
            v = ln.split("=", 1)[1].strip().strip('"').strip("'")
            return v or None
    return None


def main() -> None:
    for slug, home in profiles():
        priv = priv_from_env(home)
        if not priv:
            print(f"{slug}\tNO_BUZZ_KEY")
            continue
        env = os.environ.copy()
        env["BUZZ_PRIVATE_KEY"] = priv
        env["BUZZ_RELAY_URL"] = RELAY
        p = subprocess.run(
            ["buzz", "users", "get"],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        out = (p.stdout or "") + (p.stderr or "")
        out = out.replace(priv, "[PRIV]")
        one = " ".join(out.split())[:220]
        print(f"{slug}\trc={p.returncode}\t{one}")


if __name__ == "__main__":
    main()
