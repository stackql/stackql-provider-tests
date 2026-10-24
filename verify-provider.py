"""Verify provider metadata through a fresh StackQL CLI, without a shared server."""

import argparse
import csv
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile


def identifier(name):
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        return name
    return "`" + name.replace("`", "``") + "`"


def query(binary, registry, statement, app_root):
    result = subprocess.run(
        [str(binary), "exec", statement, "--registry=" + json.dumps(registry),
         "--output=csv", "--approot=" + app_root],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    # StackQL currently reports some query errors on stderr with exit status zero.
    if result.returncode or result.stderr.strip():
        raise RuntimeError(f"{statement}: {result.stderr.strip() or result.stdout.strip()}")
    rows = csv.DictReader(io.StringIO(result.stdout))
    if not rows.fieldnames or "name" not in rows.fieldnames:
        raise RuntimeError(f"{statement}: expected named metadata columns, got {result.stdout!r}")
    return list(rows)


def verify_provider(binary, provider, registry):
    if registry.get("verifyConfig", {}).get("nopVerify") is not False:
        raise ValueError("signed provider tests require explicit nopVerify: false")
    with tempfile.TemporaryDirectory(prefix="stackql-verify-") as app_root:
        services = query(binary, registry, f"SHOW SERVICES IN {identifier(provider)};", app_root)
        if not services:
            raise RuntimeError(f"no services found for {provider}")
        resources = 0
        for service in services:
            address = f"{identifier(provider)}.{identifier(service['name'])}"
            resources += len(query(binary, registry, f"SHOW RESOURCES IN {address};", app_root))
    return len(services), resources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("provider")
    parser.add_argument("--registry-root", required=True, type=Path)
    parser.add_argument("--stackql-bin", required=True, type=Path)
    parser.add_argument("--public-keys", type=Path, help="optional kid-to-hex public key JSON for private/test registries")
    args = parser.parse_args()
    try:
        root = args.registry_root.resolve(strict=True)
        binary = args.stackql_bin.resolve(strict=True)
        verify_config = {"nopVerify": False}
        if args.public_keys:
            keys = json.loads(args.public_keys.read_text(encoding="utf-8"))
            if not isinstance(keys, dict) or not keys or not all(
                isinstance(k, str) and isinstance(v, str) for k, v in keys.items()
            ):
                raise ValueError("--public-keys must contain a non-empty kid-to-hex object")
            verify_config["publicKeys"] = keys
        registry = {"url": root.as_uri(), "localDocRoot": str(root), "verifyConfig": verify_config}
        services, resources = verify_provider(binary, args.provider, registry)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Verified {services} services and {resources} resources in {args.provider}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
