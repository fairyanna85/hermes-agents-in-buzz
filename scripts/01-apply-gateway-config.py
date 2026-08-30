#!/usr/bin/env python3
"""Apply cardless Buzz gateway config to ONE slug.

Usage: 01-apply-gateway-config.py SLUG OWNER_HEX [wss://relay-host]

Does not restart the gateway. Does not touch BUZZ_PRIVATE_KEY.
Strips non-secret BUZZ_* overrides from .env after copying values to config.
Never prints secrets.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

STRIP_ENV = [
    "BUZZ_RELAY_URL",
    "BUZZ_CHANNELS",
    "BUZZ_HOME_CHANNEL",
    "BUZZ_HOME_CHANNEL_THREAD_ID",
    "BUZZ_ALLOWED_USERS",
    "BUZZ_ALLOW_ALL_USERS",
    "BUZZ_POLL_INTERVAL",
    "BUZZ_CLI_PATH",
    "BUZZ_TRANSPORT",
]


def hermes(slug, args):
    cmd = ["hermes"]
    if slug != "default":
        cmd += ["-p", slug]
    cmd += args
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    out = (p.stdout or "") + (p.stderr or "")
    if p.returncode != 0:
        raise SystemExit("fail %s: %s" % (cmd, out[:500]))
    return out


def main():
    if len(sys.argv) not in (3, 4):
        raise SystemExit("usage: 01-apply-gateway-config.py SLUG OWNER_HEX [wss://relay]")
    slug = sys.argv[1]
    owner = sys.argv[2].strip().lower()
    if len(owner) != 64 or any(c not in "0123456789abcdef" for c in owner):
        raise SystemExit("OWNER_HEX must be 64 lowercase hex characters")
    relay = sys.argv[3] if len(sys.argv) == 4 else "wss://buzz.example.com"
    import shutil

    cli = shutil.which("buzz") or "/usr/local/bin/buzz"
    sets = [
        ("gateway.platforms.buzz.enabled", "true"),
        ("gateway.platforms.buzz.extra.relay_url", relay),
        ("gateway.platforms.buzz.extra.cli_path", cli),
        ("gateway.platforms.buzz.extra.channels", "[]"),
        ("gateway.platforms.buzz.extra.poll_interval", "4"),
        ("gateway.platforms.buzz.extra.require_mention", "true"),
        ("gateway.platforms.buzz.extra.allow_all_users", "false"),
        ("gateway.platforms.buzz.extra.allowed_users", '["%s"]' % owner),
        ("display.platforms.buzz.interim_assistant_messages", "false"),
        ("display.platforms.buzz.tool_progress", "off"),
        ("gateway.platforms.buzz.gateway_restart_notification", "false"),
        ("gateway.delivery_ledger", "false"),
    ]
    for k, v in sets:
        print(hermes(slug, ["config", "set", k, v]).strip())
        got = hermes(slug, ["config", "get", k]).strip().splitlines()[-1]
        print(" GET", k, "=", got)

    home = Path.home() / ".hermes" if slug == "default" else Path.home() / ".hermes" / "profiles" / slug
    envp = home / ".env"
    if envp.exists():
        keep = []
        for ln in envp.read_text().splitlines():
            key = ln.split("=", 1)[0] if "=" in ln else ""
            if key in STRIP_ENV:
                continue
            keep.append(ln)
        envp.write_text("\n".join(keep) + ("\n" if keep else ""))
        envp.chmod(0o600)
        print("stripped non-secret BUZZ_* from", envp)
    print("config written. Start/restart later: hermes -p", slug, "gateway start")


if __name__ == "__main__":
    main()
