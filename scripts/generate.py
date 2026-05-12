#!/usr/bin/env python3
"""
Генерирует структуру папок и шаблон метаданных для нового пакета.

Использование:
  python scripts/generate.py --type lib --name mylib
  python scripts/generate.py --type app --name myapp
"""

import argparse
import json
import os
from datetime import date

TEMPLATE_LIB = {
    "name": "",
    "type": "lib",
    "description": "",
    "license": "MIT",
    "homepage": None,
    "repository": "",
    "keywords": [],
    "categories": [],
    "language": {
        "c": True,
        "cpp": False
    },
    "platforms": {
        "linux": True,
        "macos": True,
        "windows": False,
        "linux_arm": False,
        "macos_arm": False
    },
    "dcr": {
        "min_version": None,
        "native": False,
        "notes": None
    },
    "versions": [
        {
            "version": "0.1.0",
            "git": "",
            "tag": "v0.1.0",
            "checksum": "sha256:",
            "yanked": False,
            "published_at": str(date.today())
        }
    ],
    "author": {
        "name": "",
        "github": ""
    }
}

TEMPLATE_APP = {
    "name": "",
    "type": "app",
    "description": "",
    "license": "MIT",
    "homepage": None,
    "repository": "",
    "keywords": [],
    "categories": [],
    "language": {
        "c": True,
        "cpp": False
    },
    "platforms": {
        "linux": True,
        "macos": True,
        "windows": False,
        "linux_arm": False,
        "macos_arm": False
    },
    "dcr": {
        "min_version": None,
        "native": False,
        "notes": None
    },
    "install": {
        "via_dcr": False,
        "manual": None
    },
    "versions": [
        {
            "version": "0.1.0",
            "git": "",
            "tag": "v0.1.0",
            "checksum": "sha256:",
            "yanked": False,
            "published_at": str(date.today())
        }
    ],
    "author": {
        "name": "",
        "github": ""
    }
}

def main():
    parser = argparse.ArgumentParser(description="Generate DCR Index package template")
    parser.add_argument("--type", required=True, choices=["lib", "app"], help="Package type")
    parser.add_argument("--name", required=True, help="Package name")
    args = parser.parse_args()

    name = args.name.lower().strip()
    pkg_type = args.type
    first_letter = name[0]

    base_dir = os.path.join("packages", f"{pkg_type}s", first_letter)
    os.makedirs(base_dir, exist_ok=True)

    output_path = os.path.join(base_dir, f"{name}.json")

    if os.path.exists(output_path):
        print(f"Error: {output_path} already exists")
        return 1

    template = TEMPLATE_LIB.copy() if pkg_type == "lib" else TEMPLATE_APP.copy()
    template["name"] = name

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Created: {output_path}")
    print(f"Fill in the required fields and open a Pull Request.")
    return 0

if __name__ == "__main__":
    exit(main())