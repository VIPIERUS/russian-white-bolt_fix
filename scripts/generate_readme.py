#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def generate_readme():
    meta_path = Path("configs/metadata.json")
    if not meta_path.exists():
        print("metadata.json not found. Run fetch_configs.py first")
        return

    with open(meta_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    grouped = defaultdict(list)
    for cfg in data["configs"]:
        grouped[cfg["category"]].append(cfg)

    # Исправлено: используем тройные кавычки для многострочных строк
    readme = """# VPN configs

> Auto-update every 3 hours | Last: """ + data["updated"] + """
> Working sources: """ + str(data["success"]) + """ / """ + str(data["total_sources"]) + """

---

## Apps

| App | Link | Supports |
|-----|------|----------|
| **Nekobox** | [nekobox.one](https://nekobox.one) | VLESS, VMess, Trojan, SS, Reality |
| **V2RayNG** | [getv2rayng.com](https://getv2rayng.com) | VLESS, VMess, Trojan, SS |
| **Happ VPN** | [happ.su](https://happ.su) | VLESS, Trojan, TOR Bridges |

---

"""

    category_names = {
        "nekobox": "Nekobox Configs",
        "v2ray": "V2RayNG Configs",
        "happ": "Happ VPN Configs"
    }

    for cat, configs in grouped.items():
        readme += "### " + category_names.get(cat, cat.upper()) + """

"""
        for cfg in configs:
            readme += """<details>
<summary><b>""" + cfg["name"] + """</b> — """ + str(cfg["count"]) + """ configs, """ + str(cfg["size_kb"]) + """ KB, """ + cfg["updated"] + """</summary>

| Parameter | Value |
|-----------|-------|
| File | """ + cfg["filename"] + """ |
| Source | """ + cfg["url"] + """ |
| Configs | """ + str(cfg["count"]) + """ |
| Hash | """ + cfg["hash"] + """ |
| Download | [configs/""" + cfg["category"] + """/""" + cfg["filename"] + """](configs/""" + cfg["category"] + """/""" + cfg["filename"] + """) |

</details>

"""

    if data["errors"]:
        readme += "### Unavailable sources

"
        for err in data["errors"]:
            readme += "- " + err["name"] + " — " + err["error"][:80] + """
"""
        readme += """
> Will be retried on next update.

"""

    readme += """---

## How auto-update works

1. GitVerse Actions runs every 3 hours
2. Script downloads all sources
3. Parses and counts valid configs
4. Generates this README
5. Pushes changes to repo

## Add your source

1. Edit sources/urls.txt
2. Format: URL|CATEGORY|NAME
3. CATEGORY: nekobox | v2ray | happ

---

> Updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M UTC") + """
"""

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

    print("README.md generated successfully")


if __name__ == "__main__":
    generate_readme()
