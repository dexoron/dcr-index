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

def parse_toml_metadata(path):
    """Simple regex-based TOML parser for package metadata."""
    import re
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    metadata = {}
    # Extract [package] section
    package_match = re.search(r"\[package\](.*?)(?=\n\[|$)", content, re.DOTALL)
    if package_match:
        section = package_match.group(1)
        for key in ["name", "version", "type", "description", "author", "homepage", "license", "repository"]:
            m = re.search(rf'^{key}\s*=\s*"(.*?)"', section, re.MULTILINE)
            if m:
                metadata[key] = m.group(1)
    return metadata

def main():
    parser = argparse.ArgumentParser(description="Generate DCR Index package template")
    parser.add_argument("--type", choices=["lib", "app"], help="Package type")
    parser.add_argument("--name", help="Package name")
    parser.add_argument("--from-toml", help="Path to dcr.toml to extract metadata from")
    args = parser.parse_args()

    metadata = {}
    if args.from_toml:
        metadata = parse_toml_metadata(args.from_toml)
        if not args.name:
            args.name = metadata.get("name")
        if not args.type:
            args.type = metadata.get("type")
            if args.type == "none": # map none to lib if unsure
                 args.type = "lib"

    if not args.name or not args.type:
        print("Error: --name and --type are required (or provided via --from-toml)")
        return 1

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
    
    # Override template with metadata from TOML
    if metadata:
        if "description" in metadata: template["description"] = metadata["description"]
        if "license" in metadata: template["license"] = metadata["license"]
        if "homepage" in metadata: template["homepage"] = metadata["homepage"]
        if "repository" in metadata: template["repository"] = metadata["repository"]
        if "author" in metadata: template["author"]["name"] = metadata["author"]
        if "version" in metadata:
            template["versions"][0]["version"] = metadata["version"]
            template["versions"][0]["tag"] = f"v{metadata['version']}"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Created: {output_path}")
    print(f"Fill in the required fields and open a Pull Request.")
    return 0

if __name__ == "__main__":
    exit(main())