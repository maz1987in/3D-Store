#!/usr/bin/env python
"""Generate OpenAPI spec JSON and optionally update snapshot hash.

Usage:
  python -m scripts.generate_spec --out backend/openapi.json
  python -m scripts.generate_spec --update-hash
  python -m scripts.generate_spec --out backend/openapi.json --update-hash

Options:
  --out PATH        Write full spec JSON to PATH (directories auto-created)
  --update-hash     Recompute and overwrite tests/openapi_spec_hash.txt
  --check           Exit non-zero if current spec hash != snapshot (CI check)

Safe Defaults:
  Without flags, prints current hash to stdout.

Exit Codes:
  0 success / in-check mode hash matches
  2 mismatch in --check mode
  3 other error
"""
from __future__ import annotations
import argparse, json, hashlib, pathlib, sys

# Allow running from repo root or backend/ directory
ROOT = pathlib.Path(__file__).resolve().parents[2]
TESTS_DIR = ROOT / 'backend' / 'tests'
SNAPSHOT = TESTS_DIR / 'openapi_spec_hash.txt'

try:
    from app.openapi import build_openapi_spec  # type: ignore
except ImportError:
    # fallback if module path differs
    from app.openapi_builder import build_openapi_spec  # type: ignore


def compute_spec_and_hash():
    spec = build_openapi_spec()
    blob = json.dumps(spec, sort_keys=True, separators=(',', ':')).encode()
    h = hashlib.sha256(blob).hexdigest()
    return spec, h


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Generate deterministic OpenAPI spec")
    p.add_argument('--out', dest='out', help='Path to write JSON spec')
    p.add_argument('--update-hash', action='store_true', help='Overwrite snapshot hash file')
    p.add_argument('--check', action='store_true', help='Check current hash vs snapshot and exit 2 on mismatch')
    args = p.parse_args(argv)

    spec, h = compute_spec_and_hash()

    if args.out:
        out_path = pathlib.Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(spec, indent=2, sort_keys=True) + '\n')
        print(f"Wrote spec JSON to {out_path} ({len(json.dumps(spec))} bytes)")

    if args.check:
        expected = SNAPSHOT.read_text().strip()
        if h != expected:
            print(f"Spec hash mismatch: expected={expected} current={h}", file=sys.stderr)
            return 2
        print(f"Spec hash OK: {h}")

    if args.update_hash:
        SNAPSHOT.write_text(h + '\n')
        print(f"Updated snapshot hash -> {h}")

    if not args.out and not args.update_hash and not args.check:
        print(h)

    return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv[1:]))
