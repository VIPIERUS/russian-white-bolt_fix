#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт скачивания и парсинга VPN конфигураций
Запускается в CI/CD каждые 3 часа
Сохраняет файлы в папку VPNMIRRORS/ и создает метаданные
"""

import re
import time
import json
import hashlib
import base64
import requests
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

# Настройки
TIMEOUT = 15  # ← Уменьшил с 45 до 15 для быстрого перехода
MAX_RETRIES = 2  # ← Уменьшил с 3 до 2 для скорости
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
OUTPUT_DIR = Path("VPNMIRRORS")
SOURCES_FILE = Path("sources/urls.txt")
METADATA_FILE = Path("VPNMIRRORS/metadata.json")

# Приложения VPN с иконками и ссылками
APPS = {
    "nekobox": {
        "name": "Nekoray / Nekobox",
        "icon": "📦",
        "platforms": ["Windows", "Android"],
        "url": "https://nekobox.one",
        "description": "VLESS, VMess, Reality, White Lists, CIDR",
        "ext": ".txt"
    },
    "v2ray": {
        "name": "V2RayNG / V2RayN",
        "icon": "🚀",
        "platforms": ["Android", "Windows", "iOS"],
        "url": "https://getv2rayng.com",
        "description": "VLESS, VMess, Trojan, Shadowsocks",
        "ext": ".txt"
    },
    "happ": {
        "name": "Happ VPN",
        "icon": "🔒",
        "platforms": ["Android", "iOS"],
        "url": "https://happ.su",
        "description": "VLESS, Trojan, TOR Bridges",
        "ext": ".txt"
    },
    "singbox": {
        "name": "Sing-box",
        "icon": "📱",
        "platforms": ["Android", "iOS", "Windows", "macOS", "Linux"],
        "url": "https://sing-box.sagernet.org",
        "description": "Universal proxy platform",
        "ext": ".json"
    },
    "clash": {
        "name": "Clash / ClashMeta",
        "icon": "⚔️",
        "platforms": ["Windows", "macOS", "Linux", "Android"],
        "url": "https://github.com/MetaCubeX/Clash.Meta",
        "description": "Rule-based tunnel",
        "ext": ".yaml"
    },
    "tor": {
        "name": "TOR Browser",
        "icon": "🧅",
        "platforms": ["Windows", "macOS", "Linux", "Android"],
        "url": "https://torproject.org",
        "description": "TOR Bridges and Snowflake",
        "ext": ".txt"
    }
}


def count_configs(content: str) -> dict:
    """
    Считает количество различных типов конфигураций в файле
    Более точный подсчет с лучшей поддержкой форматов
    """
    if not content or not content.strip():
        return {
            "total": 0, 
            "vless": 0, 
            "vmess": 0, 
            "trojan": 0, 
            "ss": 0, 
            "ssr": 0, 
            "hysteria": 0, 
            "tuic": 0,
            "tor": 0,
            "other": 0
        }
    
    patterns = {
        "vless": r'^vless://',
        "vmess": r'^vmess://',
        "trojan": r'^trojan://|^trojan\+ssl://|^trojan\+ws://',
        "ss": r'^ss://|^ss\+tls://',
        "ssr": r'^ssr://',
        "hysteria": r'^hysteria://|^hy2://',
        "tuic": r'^tuic://',
        "tor": r'^(bridge|obfs4|meek|snowflake|wss-diffie-hellman)',
    }
    
    counts = {k: 0 for k in patterns.keys()}
    counts["other"] = 0
    
    lines = content.splitlines()
    for line in lines:
        line = line.strip()
        
        # Пропускаем пустые строки и комментарии
        if not line or line.startswith('#') or line.startswith('//'):
            continue
        
        matched = False
        for proto, pattern in patterns.items():
            if re.match(pattern, line, re.I):
                counts[proto] += 1
                matched = True
                break
        
        if not matched:
            # Дополнительная проверка на base64 или другие форматы
            if line.startswith('ss://') or line.startswith('vmess://'):
                # Уже проверили выше
                pass
            elif re.match(r'^[A-Za-z0-9+/=\-_]{20,}$', line):
                # Возможно base64 конфиг
                counts["other"] += 1
            elif '://' in line and any(x in line for x in ['vless', 'vmess', 'trojan', 'ss', 'ssr']):
                # Могут быть альтернативные порты
                counts["other"] += 1
    
    counts["total"] = sum(counts.values())
    return counts


def decode_base64_content(content: str) -> str:
    """Пытается декодировать base64 содержимое"""
    if not content:
        return content
    
    content_stripped = content.strip()
    if not content_stripped:
        return content
    
    # Если уже содержит протоколы, не декодируем
    if any(proto in content_stripped for proto in ['vless://', 'vmess://', 'trojan://', 'ss://', 'bridge', 'obfs4']):
        return content
    
    # Пробуем декодировать
    try:
        cleaned = re.sub(r'\s+', '', content_stripped)
        if re.match(r'^[A-Za-z0-9+/]*={0,2}$', cleaned):
            decoded = base64.b64decode(cleaned).decode('utf-8', errors='ignore')
            if decoded.strip() and any(proto in decoded for proto in ['vless://', 'vmess://', 'trojan://', 'ss://']):
                return decoded
    except Exception:
        pass
    
    return content


def fetch_url(url: str, retries: int = MAX_RETRIES) -> tuple:
    """
    Скачивает файл с повторами при ошибке, возвращает (content, error)
    ⚡ Быстро переходит к следующему источнику при ошибке
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/plain,text/html,application/json,*/*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    
    for attempt in range(retries):
        try:
            resp = requests.get(
                url, 
                headers=headers, 
                timeout=TIMEOUT,  # ← Быстрый таймаут
                allow_redirects=True,
                verify=True
            )
            resp.raise_for_status()
            content = resp.text.strip()
            
            # Пытаемся декодировать base64
            content = decode_base64_content(content)
            
            return content, ""
            
        except requests.exceptions.Timeout:
            if attempt < retries - 1:
                time.sleep(0.5)  # ← Меньше задержка
                continue
            return "", "Timeout"  # ← Короче сообщение
            
        except requests.exceptions.ConnectionError:
            if attempt < retries - 1:
                time.sleep(0.5)
                continue
            return "", "Connection error"
            
        except requests.exceptions.HTTPError as e:
            # Для 404, 403 — не пробуем еще раз
            if e.response.status_code in [404, 403, 410]:
                return "", f"HTTP {e.response.status_code}"
            if attempt < retries - 1:
                time.sleep(0.5)
                continue
            return "", f"HTTP {e.response.status_code}"
            
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                time.sleep(0.5)
                continue
            return "", "Network error"
            
        except Exception as e:
            return "", "Unknown error"
    
    return "", "Max retries exceeded"


def generate_filename(name: str, category: str, url: str) -> str:
    """Генерирует безопасное имя файла"""
    # Добавляем хеш от URL для уникальности
    url_hash = hashlib.md5(url.encode()).hexdigest()[:6]
    
    # Очищаем имя
    safe_name = re.sub(r'[^\w\-_.\s]', '_', name).strip()
    safe_name = re.sub(r'\s+', '_', safe_name)
    safe_name = safe_name[:40]
    
    app_info = APPS.get(category, APPS["v2ray"])
    return f"{safe_name}_{url_hash}{app_info['ext']}"


def save_config(name: str, category: str, content: str, url: str) -> dict:
    """Сохраняет конфиг в VPNMIRRORS/ и возвращает метаданные"""
    app_info = APPS.get(category, APPS["v2ray"])
    
    # Создаем папку для категории
    category_dir = OUTPUT_DIR / category
    category_dir.mkdir(parents=True, exist_ok=True)
    
    # Генерируем имя файла
    filename = generate_filename(name, category, url)
    filepath = category_dir / filename
    
    # Подсчитываем конфигурации
    config_counts = count_configs(content)
    
    # Формируем заголовок файла
    header = f"""# {name}
# Source: {url}
# Category: {app_info['name']}
# Updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
# Total configs: {config_counts['total']}
# Protocols: VLESS={config_counts['vless']}, VMess={config_counts['vmess']}, Trojan={config_counts['trojan']}, SS={config_counts['ss']}, Other={config_counts['other']}
# ================================================================

"""
    
    # Сохраняем файл
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(header)
        f.write(content)
    
    # Вычисляем хеш содержимого
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
    
    return {
        "name": name,
        "category": category,
        "filename": filename,
        "filepath": str(filepath),
        "counts": config_counts,
        "url": url,
        "app_name": app_info["name"],
        "app_icon": app_info["icon"],
        "app_url": app_info["url"],
        "platforms": app_info["platforms"],
        "size_kb": round(len(content.encode()) / 1024, 2),
        "hash": content_hash,
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "updated_msk": datetime.now(timezone.utc).astimezone(datetime.now().astimezone().tzinfo).strftime("%Y-%m-%d %H:%M MSK")
    }


def parse_sources_file() -> list:
    """Парсит файл sources/urls.txt"""
    sources = []
    
    if not SOURCES_FILE.exists():
        print(f"Warning: {SOURCES_FILE} not found!")
        return sources
    
    with open(SOURCES_FILE, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Пропускаем пустые строки и комментарии
            if not line or line.startswith('#'):
                continue
            
            # Формат: URL|CATEGORY|NAME
            parts = line.split('|')
            if len(parts) < 3:
                print(f"Warning: Invalid format at line {line_num}: {line}")
                continue
            
            url = parts[0].strip()
            category = parts[1].strip().lower()
            name = parts[2].strip()
            
            # Валидация URL
            if not url.startswith(('http://', 'https://')):
                print(f"Warning: Invalid URL at line {line_num}: {url}")
                continue
            
            # Поддерживаемые категории
            if category not in APPS:
                print(f"Warning: Unknown category '{category}' at line {line_num}, using 'v2ray'")
                category = "v2ray"
            
            sources.append({
                "url": url,
                "category": category,
                "name": name,
                "line_num": line_num
            })
    
    return sources


def main():
    print("=" * 60)
    print("VPN Config Fetcher for GitVerse")
    print(f"Started: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)
    
    # Создаем выходную директорию
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Парсим источники
    sources = parse_sources_file()
    print(f"\nLoaded {len(sources)} sources from {SOURCES_FILE}")
    
    results = []
    errors = []
    skipped = []
    
    for i, src in enumerate(sources, 1):
        print(f"\n[{i}/{len(sources)}] Downloading: {src['name']} ({src['category']})")
        print(f"  URL: {src['url'][:80]}...")
        
        content, error = fetch_url(src['url'])
        
        if error:
            errors.append({
                "name": src['name'],
                "url": src['url'],
                "category": src['category'],
                "error": error
            })
            print(f"  ❌ Error: {error}")
            continue
        
        if not content or not content.strip():
            skipped.append({
                "name": src['name'],
                "url": src['url'],
                "reason": "Empty content"
            })
            print(f"  ⚠️  Skipped: Empty content")
            continue
        
        # Сохраняем конфиг
        meta = save_config(src['name'], src['category'], content, src['url'])
        results.append(meta)
        
        counts = meta['counts']
        print(f"  ✅ Success: {counts['total']} configs (VLESS:{counts['vless']} VMess:{counts['vmess']} Trojan:{counts['trojan']})")
        print(f"     Saved: {meta['filename']} ({meta['size_kb']} KB)")
        
        # Минимальная задержка между запросами
        time.sleep(0.2)
    
    # Статистика
    total_configs = sum(r['counts']['total'] for r in results)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✅ Success: {len(results)} sources, {total_configs} configs")
    print(f"❌ Errors: {len(errors)} sources")
    print(f"⚠️  Skipped: {len(skipped)} sources")
    print("=" * 60)
    
    # Сохраняем метаданные
    metadata = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "updated_formatted": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "updated_msk": datetime.now().strftime("%Y-%m-%d %H:%M MSK"),
        "total_sources": len(sources),
        "success": len(results),
        "failed": len(errors),
        "skipped": len(skipped),
        "total_configs": total_configs,
        "configs": results,
        "errors": errors,
        "skipped_sources": skipped
    }
    
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"\nMetadata saved: {METADATA_FILE}")
    print(f"Finished: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # Всегда возвращаем 0 - частичный успех не должен ронять CI
    return 0


if __name__ == "__main__":
    exit(main())
