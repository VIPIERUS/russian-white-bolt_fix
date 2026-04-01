#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт скачивания и парсинга конфигураций
Запускается в CI/CD каждые 3 часа
"""

import re
import time
import json
import hashlib
import requests
from datetime import datetime, timezone
from pathlib import Path

# Настройки
TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
OUTPUT_DIR = Path("configs")
SOURCES_FILE = Path("sources/urls.txt")

# Приложения
APPS = {
    "nekobox": {"name": "Nekobox", "icon": "nekobox", "url": "https://nekobox.one", "ext": ".txt"},
    "v2ray":   {"name": "V2RayNG", "icon": "v2ray",   "url": "https://getv2rayng.com", "ext": ".txt"},
    "happ":    {"name": "Happ VPN", "icon": "happ",   "url": "https://happ.su", "ext": ".txt"},
}


def count_configs(content: str) -> int:
    """Считает количество валидных конфигураций в файле"""
    if not content.strip():
        return 0
    patterns = [
        r'^vless://', r'^vmess://', r'^trojan://', r'^ss://', r'^ssr://',
        r'^tuic://', r'^hysteria://', r'^hy2://', r'^\d+\.\d+\.\d+\.\d+',
        r'^bridge\s*=', r'^obfs4', r'^meek'
    ]
    count = 0
    for line in content.splitlines():
        line = line.strip()
        if any(re.match(p, line, re.I) for p in patterns):
            count += 1
    return count if count > 0 else (1 if content.strip() else 0)


def fetch_url(url: str) -> tuple:
    """Скачивает файл, возвращает (content, config_count, error)"""
    try:
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(url, headers=headers, timeout=TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
        content = resp.text.strip()

        if content and not any(c in content for c in ['://', 'bridge', 'obfs']):
            import base64
            try:
                decoded = base64.b64decode(content).decode('utf-8', errors='ignore')
                if decoded.strip():
                    content = decoded
            except Exception:
                pass

        count = count_configs(content)
        return content, count, ""
    except Exception as e:
        return "", 0, str(e)


def save_config(name: str, category: str, content: str, count: int, url: str) -> dict:
    """Сохраняет конфиг и возвращает метаданные"""
    app_info = APPS.get(category, APPS["nekobox"])
    output_path = OUTPUT_DIR / category
    output_path.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r'[^\w\-_.]', '_', name)[:50]
    filename = f"{safe_name}{app_info['ext']}"
    filepath = output_path / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {name}\n")
        f.write(f"# Source: {url}\n")
        f.write(f"# Updated: {datetime.now(timezone.utc).isoformat()}\n")
        f.write(f"# Count: {count}\n\n")
        f.write(content)

    file_hash = hashlib.md5(content.encode()).hexdigest()[:8]
    return {
        "name": name,
        "category": category,
        "filename": filename,
        "count": count,
        "url": url,
        "app": app_info["name"],
        "app_icon": app_info["icon"],
        "app_url": app_info["url"],
        "size_kb": round(len(content.encode()) / 1024, 1),
        "hash": file_hash,
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    }


def main():
    print(f"Starting update: {datetime.now(timezone.utc).isoformat()}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    errors = []

    with open(SOURCES_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('|')
            if len(parts) < 3:
                continue
            url, category, name = parts[0], parts[1].lower(), parts[2]

            print(f"Downloading: {name} ...")
            content, count, error = fetch_url(url)

            if error:
                errors.append({"name": name, "url": url, "error": error})
                print(f"Warning (skipping): {error}")
                continue

            meta = save_config(name, category, content, count, url)
            results.append(meta)
            print(f"OK {name}: {count} configs, {meta['size_kb']} KB")
            time.sleep(1)

    # Сохраняем метаданные для README
    metadata_path = Path("configs") / "metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump({
            "updated": datetime.now(timezone.utc).isoformat(),
            "total_sources": len(results) + len(errors),
            "success": len(results),
            "failed": len(errors),
            "configs": results,
            "errors": errors
        }, f, ensure_ascii=False, indent=2)

    print(f"\nDone: {len(results)} success, {len(errors)} warnings (skipped)")
    # Всегда возвращаем 0 — частичный успех не должен ронять CI
    return 0


if __name__ == "__main__":
    exit(main())
