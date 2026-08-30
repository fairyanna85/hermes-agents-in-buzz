#!/usr/bin/env python3
"""Mint a unique secp256k1 Buzz key into ONE new slug's .env.

Usage: 04-mint-unique-key.py SLUG

For a NEW person only. Never run this on a live helper (Achilles, Hephaestus, …)
just because the file already has a key — that key might be a clone.

Never prints the private key. Prints PUBHEX=... only.
chmod 600 the .env. Leaves every other profile untouched.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

try:
    import secp256k1
except ImportError:
    raise SystemExit("need python module secp256k1 (pip install secp256k1)")

HERMES = Path.home() / ".hermes"


def read_priv(envp: Path):
    if not envp.exists():
        return None
    for ln in envp.read_text().splitlines():
        if ln.startswith("BUZZ_PRIVATE_KEY="):
            v = ln.split("=", 1)[1].strip().strip('"').strip("'")
            return v or None
    return None


def pub_of(priv_hex: str) -> str:
    k = secp256k1.PrivateKey(bytes.fromhex(priv_hex), raw=True)
    return k.pubkey.serialize(compressed=True)[1:].hex()


def all_homes():
    yield "default", HERMES
    pdir = HERMES / "profiles"
    if pdir.is_dir():
        for d in sorted(pdir.iterdir()):
            if d.is_dir() and (d / "config.yaml").exists():
                yield d.name, d


def upsert_priv(envp: Path, priv: str) -> None:
    lines = envp.read_text().splitlines() if envp.exists() else []
    out = []
    found = False
    for ln in lines:
        if ln.startswith("BUZZ_PRIVATE_KEY="):
            out.append("BUZZ_PRIVATE_KEY=" + priv)
            found = True
        else:
            out.append(ln)
    if not found:
        if out and out[-1].strip():
            out.append("")
        out.append("BUZZ_PRIVATE_KEY=" + priv)
    envp.write_text("\n".join(out) + "\n")
    envp.chmod(0o600)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: 04-mint-unique-key.py SLUG")
    slug = sys.argv[1]
    if slug == "default":
        raise SystemExit("refusing default — that is the Buzz person Hermes")
    home = HERMES / "profiles" / slug
    envp = home / ".env"
    if not home.is_dir():
        raise SystemExit("no profile dir " + str(home))

    used = {}
    for name, h in all_homes():
        priv = read_priv(h / ".env")
        if not priv:
            continue
        try:
            used[name] = pub_of(priv)
        except Exception as e:
            print("SKIP parse", name, type(e).__name__)

    before = used.get(slug)
    others = {n: p for n, p in used.items() if n != slug}
    if before and before in others.values():
        donor = [n for n, p in others.items() if p == before]
        print("CLONE detected. this slug shared a pubkey with", ",".join(donor))
        print("minting a NEW key into", envp)
        print("leaving donors unchanged")
    elif before:
        print("slug already has a unique key. refusing to rotate.")
        print("PUBHEX=" + before)
        return

    used_pubs = set(others.values())
    new_priv = None
    new_pub = None
    for _ in range(100):
        k = secp256k1.PrivateKey()
        ser = k.serialize()
        priv = ser.hex() if isinstance(ser, bytes) else ser.lower()
        if len(priv) != 64:
            raise SystemExit("unexpected priv length")
        pub = pub_of(priv)
        if pub not in used_pubs:
            new_priv, new_pub = priv, pub
            break
    if not new_priv:
        raise SystemExit("could not mint unique key")

    upsert_priv(envp, new_priv)
    check = read_priv(envp)
    if check != new_priv:
        raise SystemExit("write verify failed")
    if (envp.stat().st_mode & 0o777) != 0o600:
        raise SystemExit("chmod 600 failed")
    # donor unchanged
    for n, p in others.items():
        again = pub_of(read_priv((HERMES if n == "default" else HERMES / "profiles" / n) / ".env"))
        if again != p:
            raise SystemExit("DONOR KEY CHANGED " + n)
    print("mode", oct(envp.stat().st_mode & 0o777))
    print("sha16", hashlib.sha256(new_priv.encode()).hexdigest()[:16])
    print("PUBHEX=" + new_pub)


if __name__ == "__main__":
    main()
