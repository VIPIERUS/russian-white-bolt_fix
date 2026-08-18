#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт скачивания и парсинга конфигураций
Запускается в CI/CD каждые 3 часа
"""

import os
import re
import time
import json
import base64
import hashlib
import requests
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

# Настройки
TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
OUTPUT_DIR = Path("configs")
SOURCES_FILE = Path("sources/urls.txt")

# Токен GitVerse из окружения
GITVERSE_TOKEN = os.environ.get("GITVERSE_TOKEN", "")

# Приложения
APPS = {
    "nekobox": {"name": "Nekobox", "icon": "nekobox", "url": "https://nekobox.one", "ext": ".txt"},
    "v2ray":   {"name": "V2RayNG", "icon": "v2ray",   "url": "https://getv2rayng.com", "ext": ".txt"},
    "happ":    {"name": "Happ VPN", "icon": "happ",   "url": "https://happ.su", "ext": ".txt"},
}

# Протоколы для подсчёта
PROTOCOLS = {
    'vless': r'^vless://',
    'vmess': r'^vmess://',
    'trojan': r'^trojan://',
    'ss': r'^ss://',
    'ssr': r'^ssr://',
    'tuic': r'^tuic://',
    'hysteria': r'^hysteria://',
    'hy2': r'^hy2://',
    'wireguard': r'^wg://',
    'bridge': r'^bridge\s*=|^obfs4|^meek',
    'ip': r'^\d+\.\d+\.\d+\.\d+',
}


def count_configs_detailed(content: str) -> dict:
    """
    Подробный подсчёт конфигов по протоколам
    Возвращает словарь с общим количеством и количеством по каждому протоколу
    """
    if not content.strip():
        return {"total": 0, "protocols": {}}
    
    result = {"total": 0, "protocols": defaultdict(int)}
    
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        
        matched = False
        for proto, pattern in PROTOCOLS.items():
            if re.match(pattern, line, re.I):
                result["protocols"][proto] += 1
                result["total"] += 1
                matched = True
                break
        
        # Если не подошло ни одному паттерну, но строка не пустая
        # возможно это TOR мост или что-то похожее
        if not matched and len(line) > 5:
            # Проверяем, похоже ли на TOR мост
            if any(x in line.lower() for x in ['bridge', 'obfs4', 'meek', 'tor']):
                result["protocols"]["tor_bridge"] += 1
                result["total"] += 1
            elif '://' in line or '.' in line:
                # Возможно это IP или другой конфиг
                result["protocols"]["other"] += 1
                result["total"] += 1
    
    return result


def fetch_url(url: str) -> tuple:
    """Скачивает файл, возвращает (content, stats, error)"""
    try:
        headers = {"User-Agent": USER_AGENT}
        if "gitverse.ru" in url and GITVERSE_TOKEN:
            headers["Authorization"] = f"Bearer {GITVERSE_TOKEN}"

        resp = requests.get(url, headers=headers, timeout=TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
        content = resp.text.strip()

        # Если контент не похож на конфиги, пробуем декодировать base64
        if content and not any(c in content for c in ['://', 'bridge', 'obfs']):
            try:
                decoded = base64.b64decode(content).decode('utf-8', errors='ignore')
                if decoded.strip():
                    content = decoded
            except Exception:
                pass

        stats = count_configs_detailed(content)
        return content, stats, ""
    except Exception as e:
        return "", {"total": 0, "protocols": {}}, str(e)


def save_config(name: str, category: str, content: str, stats: dict, url: str) -> dict:
    """Сохраняет конфиг и возвращает метаданные"""
    app_info = APPS.get(category, APPS["nekobox"])
    output_path = OUTPUT_DIR / category
    output_path.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r'[^\w\-_.]', '_', name)[:50]
    filename = f"{safe_name}{app_info['ext']}"
    filepath = output_path / filename

    # Сортируем протоколы для красивого вывода
    protocols_str = ', '.join([f"{k}: {v}" for k, v in sorted(stats["protocols"].items())])
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {name}\n")
        f.write(f"# Source: {url}\n")
        f.write(f"# Updated: {datetime.now(timezone.utc).isoformat()}\n")
        f.write(f"# Total: {stats['total']}\n")
        f.write(f"# Protocols: {protocols_str}\n\n")
        f.write(content)

    file_hash = hashlib.md5(content.encode()).hexdigest()[:8]
    return {
        "name": name,
        "category": category,
        "filename": filename,
        "count": stats["total"],
        "protocols": dict(stats["protocols"]),
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

    if not SOURCES_FILE.exists():
        print(f"ERROR: {SOURCES_FILE} not found!")
        return 1

    results = []
    errors = []
    total_links = 0
    total_configs = 0
    total_protocols = defaultdict(int)

    with open(SOURCES_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('|')
            if len(parts) < 3:
                print(f"Warning: skipping invalid line: {line}")
                continue
            url, category, name = parts[0], parts[1].lower(), parts[2]
            total_links += 1

            print(f"Downloading ({total_links}): {name}")
            content, stats, error = fetch_url(url)

            if error:
                errors.append({"name": name, "url": url, "error": error})
                print(f"  ❌ Error: {error}")
                continue

            meta = save_config(name, category, content, stats, url)
            results.append(meta)
            
            # Суммируем общую статистику
            total_configs += stats["total"]
            for proto, count in stats["protocols"].items():
                total_protocols[proto] += count
            
            print(f"  ✅ OK: {stats['total']} configs ({', '.join([f'{k}:{v}' for k, v in stats['protocols'].items()])})")
            time.sleep(1)

    # Сохраняем метаданные
    metadata_path = OUTPUT_DIR / "metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump({
            "updated": datetime.now(timezone.utc).isoformat(),
            "total_sources": len(results) + len(errors),
            "success": len(results),
            "failed": len(errors),
            "total_configs": total_configs,
            "total_protocols": dict(total_protocols),
            "configs": results,
            "errors": errors
        }, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*50}")
    print(f"SUMMARY:")
    print(f"  Total links processed: {total_links}")
    print(f"  Success: {len(results)}")
    print(f"  Failed: {len(errors)}")
    print(f"  Total configs: {total_configs}")
    print(f"  Protocols: {', '.join([f'{k}: {v}' for k, v in sorted(total_protocols.items())])}")
    print(f"{'='*50}")
    
    return 0


if __name__ == "__main__":
    exit(main())
