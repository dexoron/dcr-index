#!/usr/bin/env python3
"""
Валидирует JSON-пакеты на соответствие схеме DCR Index.

Использование:
  python scripts/validate.py packages/libs/m/mylib.json
  python scripts/validate.py --all
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime

ALLOWED_CATEGORIES = {
    "Systems", "Networking", "Security", "Database", "Game Dev", "Graphics",
    "Audio", "Math", "Parsing", "Embedded", "Crypto", "Media",
    "Developer Tools", "Build Systems", "Testing", "UI", "Serialization", "Compression"
}

RE_NAME = re.compile(r"^[a-z0-9-]+$")
RE_SEMVER = re.compile(r"^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$")
RE_CHECKSUM = re.compile(r"^sha256:[a-f0-9]{64}$")
RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def error(path, message):
    print(f"FAILED: {path}\n  Error: {message}")
    return False

def validate_package(path):
    if not os.path.exists(path):
        return error(path, "File does not exist")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return error(path, f"Invalid JSON syntax: {e}")

    # 1. Basic fields
    required_fields = ["name", "type", "description", "license", "repository", "keywords", "categories", "language", "platforms", "dcr", "versions", "author"]
    for field in required_fields:
        if field not in data:
            return error(path, f"Missing required field: '{field}'")

    name = data["name"]
    if not RE_NAME.match(name):
        return error(path, f"Invalid name format: '{name}'. Use only lowercase letters, numbers and '-'")

    if data["type"] not in ["lib", "app"]:
        return error(path, f"Invalid type: '{data['type']}'. Must be 'lib' or 'app'")

    # Path check
    pkg_type_plural = f"{data['type']}s"
    expected_path = os.path.join("packages", pkg_type_plural, name[0], f"{name}.json")
    # Normalize paths for comparison
    if os.path.normpath(path) != os.path.normpath(expected_path):
        return error(path, f"File location mismatch. Expected: {expected_path}")

    if len(data["description"]) > 200:
        return error(path, "Description too long (max 200 chars)")

    # 2. Keywords & Categories
    if not (1 <= len(data["keywords"]) <= 8):
        return error(path, f"Keywords count must be between 1 and 8 (got {len(data['keywords'])})")

    for cat in data["categories"]:
        if cat not in ALLOWED_CATEGORIES:
            return error(path, f"Invalid category: '{cat}'. Allowed: {', '.join(sorted(ALLOWED_CATEGORIES))}")

    # 3. Language & Platforms
    for section in ["language", "platforms"]:
        if section not in data or not isinstance(data[section], dict):
            return error(path, f"'{section}' must be an object")

    # 4. App specific
    if data["type"] == "app":
        if "install" not in data:
            return error(path, "Missing 'install' field for app type")
        if not isinstance(data["install"], dict):
            return error(path, "'install' must be an object")
        if "via_dcr" not in data["install"]:
            return error(path, "Missing 'install.via_dcr'")

    # 5. Versions
    if not isinstance(data["versions"], list) or len(data["versions"]) == 0:
        return error(path, "'versions' must be a non-empty array")

    for idx, v in enumerate(data["versions"]):
        v_ctx = f"versions[{idx}]"
        req_v_fields = ["version", "git", "tag", "checksum", "yanked", "published_at"]
        for vf in req_v_fields:
            if vf not in v:
                return error(path, f"Missing field '{vf}' in {v_ctx}")

        if not RE_SEMVER.match(v["version"]):
            return error(path, f"Invalid SemVer format: '{v['version']}' in {v_ctx}")

        if not RE_CHECKSUM.match(v["checksum"]):
            return error(path, f"Invalid checksum format: '{v['checksum']}' in {v_ctx}. Must be 'sha256:HEX64'")

        if not RE_DATE.match(v["published_at"]):
            return error(path, f"Invalid date format: '{v['published_at']}' in {v_ctx}. Use YYYY-MM-DD")
        try:
            datetime.strptime(v["published_at"], "%Y-%m-%d")
        except ValueError:
            return error(path, f"Invalid date value: '{v['published_at']}' in {v_ctx}")

    print(f"OK: {path}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Validate DCR Index package metadata")
    parser.add_argument("files", nargs="*", help="Files to validate")
    parser.add_argument("--all", action="store_true", help="Validate all packages in repository")
    args = parser.parse_args()

    files_to_validate = args.files

    if args.all:
        for root, _, filenames in os.walk("packages"):
            for filename in filenames:
                if filename.endswith(".json"):
                    files_to_validate.append(os.path.join(root, filename))

    if not files_to_validate:
        parser.print_help()
        return 0

    success = True
    for file in files_to_validate:
        if not validate_package(file):
            success = False

    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
