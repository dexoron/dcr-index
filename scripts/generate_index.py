#!/usr/bin/env python3
"""
Генерирует index.json из всех пакетов в папке packages.
"""

import json
import os

def generate():
    index = {"packages": []}
    packages_dir = "packages"
    
    if not os.path.exists(packages_dir):
        print(f"Error: {packages_dir} not found")
        return

    for root, _, filenames in os.walk(packages_dir):
        for filename in filenames:
            if filename.endswith(".json"):
                path = os.path.join(root, filename)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        pkg = json.load(f)
                        # Добавляем только минимальную информацию для поиска
                        index["packages"].append({
                            "name": pkg["name"],
                            "type": pkg["type"],
                            "description": pkg["description"],
                            "latest_version": pkg["versions"][-1]["version"],
                            "path": path
                        })
                except Exception as e:
                    print(f"Error reading {path}: {e}")

    with open("index.json", "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Generated index.json")

if __name__ == "__main__":
    generate()
