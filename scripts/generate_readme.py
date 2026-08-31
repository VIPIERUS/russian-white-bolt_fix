#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор README.md для VPN White-Lists
Использует GitVerse API для прямых ссылок на файлы + превью иконок VPN
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path

# Конфигурация
REPO_OWNER = "RUVIPIEN"
REPO_NAME = "russian-white-bolt"
BRANCH = "master"

# Категории и их описания + соответствие файлам фото
CATEGORIES = {
    'nekobox': {
        'icon': '📦',
        'name': 'Nekoray / Nekobox',
        'photo': 'Nekoray.png',
        'description': 'Продвинутый клиент с поддержкой VLESS, VMess, Reality, White Lists и CIDR'
    },
    'v2ray': {
        'icon': '🚀',
        'name': 'V2RayNG / V2RayN',
        'photo': 'V2RayNG.png',
        'description': 'Популярный клиент для VLESS, VMess, Trojan, Shadowsocks'
    },
    'happ': {
        'icon': '🔒',
        'name': 'Happ VPN',
        'photo': 'Happ.png',
        'description': 'Простой VPN с поддержкой VLESS, Trojan и TOR Bridges'
    },
    'singbox': {
        'icon': '📱',
        'name': 'Sing-box',
        'photo': 'Sing-box.png',
        'description': 'Универсальная платформа проксирования'
    },
    'clash': {
        'icon': '⚔️',
        'name': 'Clash / ClashMeta',
        'photo': 'Clash.png',
        'description': 'Rule-based tunnel с продвинутой маршрутизацией'
    },
    'tor': {
        'icon': '🧅',
        'name': 'TOR Bridges',
        'photo': None,
        'description': 'Мосты для обхода блокировок TOR'
    }
}

# Прямые ссылки на скачивание с Mail.ru Cloud
DOWNLOAD_LINKS = {
    'nekobox': {
        'windows': 'https://cloud.mail.ru/public/4S6V/b7MpS2Mq2',
        'android': None,  # Нет отдельной ссылки на nekoray.apk
        'mac': None
    },
    'v2ray': {
        'windows': 'https://cloud.mail.ru/public/sgNP/F46KfPDQb',
        'android': 'https://cloud.mail.ru/public/Qt13/dcrEunZXz',
        'mac': 'https://cloud.mail.ru/public/FHHR/3cEDNRdBQ'
    },
    'happ': {
        'windows': None,
        'android': 'https://cloud.mail.ru/public/oNx1/p9ABSSc35',
        'mac': None
    },
    'singbox': {
        'windows': 'https://cloud.mail.ru/public/mN76/xdt4SSKd3',
        'android': 'https://cloud.mail.ru/public/8iNb/TVsDyCQHt',
        'mac': None
    },
    'clash': {
        'windows': 'https://cloud.mail.ru/public/LyPS/KhTPz3N9S',
        'android': 'https://cloud.mail.ru/public/VRSa/PQwpQ5QY4',
        'mac': 'https://cloud.mail.ru/public/rLZc/X6jDeNXiw'
    }
}

def generate_api_url(file_path: str) -> str:
    """Генерирует правильную API-ссылку GitVerse для скачивания файла"""
    clean_path = file_path.lstrip('./')
    return f"https://gitverse.ru/api/repos/{REPO_OWNER}/{REPO_NAME}/raw/branch/{BRANCH}/{clean_path}"

def generate_photo_url(photo_filename: str) -> str:
    """Генерирует ссылку на фото в папке foto/"""
    return f"https://gitverse.ru/api/repos/{REPO_OWNER}/{REPO_NAME}/raw/branch/{BRANCH}/foto/{photo_filename}"

def format_size(size_bytes: int) -> str:
    """Форматирует размер файла"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

def format_number(num: int) -> str:
    """Форматирует число с пробелами"""
    return f"{num:,}".replace(",", " ")

def format_file_name(filename: str) -> str:
    """Преобразует имя файла в читаемое название"""
    name = re.sub(r'_[a-f0-9]{6}$', '', filename)
    name = name.replace('_', ' ')
    return name.title()

def parse_protocols(protocols_str: str) -> dict:
    """Парсит строку протоколов"""
    protocols = {}
    if not protocols_str:
        return protocols
    matches = re.findall(r'(\w+):\s*(\d+)', protocols_str)
    for proto, count in matches:
        protocols[proto] = int(count)
    return protocols

def format_protocols_badge(protocols: dict) -> str:
    """Форматирует бейджи протоколов"""
    if not protocols:
        return "`Configs: 0`"
    badges = []
    priority = ['VLESS', 'VMess', 'Trojan', 'SS', 'Hysteria', 'Other']
    for proto in priority:
        if proto in protocols:
            badges.append(f"`{proto}: {protocols[proto]}`")
    for proto, count in protocols.items():
        if proto not in priority:
            badges.append(f"`{proto}: {count}`")
    return " ".join(badges)

def load_metadata() -> dict:
    """Загружает метаданные"""
    metadata_path = Path("VPNMIRRORS/metadata.json")
    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def scan_vpn_files() -> dict:
    """Сканирует директорию VPNMIRRORS"""
    files_by_category = {}
    base_path = Path("VPNMIRRORS")
    
    if not base_path.exists():
        return files_by_category
    
    for category_dir in base_path.iterdir():
        if category_dir.is_dir() and category_dir.name != "__pycache__":
            category = category_dir.name
            files_by_category[category] = []
            
            for file_path in category_dir.glob("*.txt"):
                if file_path.name == "metadata.json":
                    continue
                    
                stat = file_path.stat()
                file_info = {
                    'filename': file_path.name,
                    'name': format_file_name(file_path.stem),
                    'path': str(file_path),
                    'size': stat.st_size,
                    'size_formatted': format_size(stat.st_size),
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M UTC'),
                    'protocols': {},
                    'total_configs': 0
                }
                files_by_category[category].append(file_info)
    
    for category in files_by_category:
        files_by_category[category].sort(key=lambda x: x['filename'])
    
    return files_by_category

def merge_with_metadata(files_by_category: dict, metadata: dict) -> dict:
    """Объединяет с метаданными"""
    for config in metadata.get('configs', []):
        category = config.get('category')
        filename = config.get('filename')
        
        if category in files_by_category:
            for file_info in files_by_category[category]:
                if file_info['filename'] == filename:
                    file_info['protocols'] = config.get('counts', {})
                    file_info['total_configs'] = config.get('counts', {}).get('total', 0)
                    break
    
    return files_by_category

def count_total_configs(files_by_category: dict) -> int:
    """Подсчитывает общее количество конфигураций"""
    return sum(
        f.get('total_configs', 0) 
        for files in files_by_category.values() 
        for f in files
    )

def generate_download_links_section(category: str) -> str:
    """Генерирует секцию с кнопками скачивания для платформ"""
    links = DOWNLOAD_LINKS.get(category, {})
    if not any(links.values()):
        return ""
    
    buttons = []
    
    # Windows
    if links.get('windows'):
        buttons.append(f"[💻 Windows]({links['windows']})")
    
    # Android
    if links.get('android'):
        buttons.append(f"[📱 Android]({links['android']})")
    
    # macOS
    if links.get('mac'):
        buttons.append(f"[🍎 macOS]({links['mac']})")
    
    if not buttons:
        return ""
    
    return "<br>" + " • ".join(buttons)

def generate_vpn_preview_section() -> list:
    """Генерирует секцию с иконками-превью VPN приложений"""
    lines = [
        "## 📱 VPN Приложения",
        "",
        "> Выберите приложение для вашей платформы и импортируйте конфигурации из таблиц ниже",
        "> **Нажмите на иконку 👁️ чтобы увидеть скриншот приложения**",
        "",
        "| Приложение | Платформы | Описание | Сайт | Скачать |",
        "|------------|-----------|----------|------|---------|"
    ]
    
    vpn_apps = [
        {
            'key': 'nekobox',
            'platforms': '💻 Windows 📱 Android',
            'download': 'https://nekobox.one'
        },
        {
            'key': 'v2ray', 
            'platforms': '📱 Android 💻 Windows 🍎 iOS',
            'download': 'https://getv2rayng.com'
        },
        {
            'key': 'happ',
            'platforms': '📱 Android 🍎 iOS', 
            'download': 'https://happ.su'
        },
        {
            'key': 'singbox',
            'platforms': '📱 Android 🍎 iOS 💻 Windows 🖥️ macOS 🐧 Linux',
            'download': 'https://sing-box.sagernet.org'
        },
        {
            'key': 'clash',
            'platforms': '💻 Windows 🖥️ macOS 🐧 Linux 📱 Android',
            'download': 'https://github.com/MetaCubeX/Clash.Meta'
        }
    ]
    
    for app in vpn_apps:
        cat_info = CATEGORIES.get(app['key'], {})
        name = cat_info.get('name', app['key'])
        description = cat_info.get('description', '')
        photo = cat_info.get('photo')
        
        # Генерируем ссылку на фото если есть
        if photo:
            photo_url = generate_photo_url(photo)
            preview_badge = f"[👁️]({photo_url})"
        else:
            preview_badge = "—"
        
        # Генерируем кнопки скачивания
        download_links = generate_download_links_section(app['key'])
        
        lines.append(
            f"| {cat_info.get('icon', '📱')} **{name}** {preview_badge} | "
            f"{app['platforms']} | {description} | "
            f"[🌐 Сайт]({app['download']}) | "
            f"{download_links if download_links else '—'} |"
        )
    
    return lines

def generate_readme(files_by_category: dict, metadata: dict) -> str:
    """Генерирует содержимое README.md"""
    
    total_files = sum(len(files) for files in files_by_category.values())
    total_configs = count_total_configs(files_by_category)
    total_sources = metadata.get('total_sources', 0)
    working_sources = metadata.get('success', 0)
    failed_sources = metadata.get('errors', [])
    update_time = datetime.now().strftime('%Y-%m-%d %H:%M MSK')
    
    lines = [
        "# 🌐 VPN White-Lists для России",
        "",
        "<div align=\"center\">",
        "",
        "![Auto Update](https://img.shields.io/badge/Auto%20Update-Every%203%20Hours-brightgreen?style=for-the-badge)",
        f"![Configs](https://img.shields.io/badge/Configs-{total_configs}-blue?style=for-the-badge)",
        f"![Sources](https://img.shields.io/badge/Sources-{working_sources}%2F{total_sources}-orange?style=for-the-badge)",
        "",
        "</div>",
        "",
        "## 📊 Информация",
        "",
        "| Параметр | Значение |",
        "|----------|----------|",
        f"| 🕐 **Последнее обновление** | `{update_time}` |",
        f"| 📁 **Всего файлов** | `{total_files}` |",
        f"| 🔗 **Всего конфигураций** | `{format_number(total_configs)}` |",
        f"| ✅ **Рабочих источников** | `{working_sources}` |",
        f"| ❌ **Недоступных источников** | `{len(failed_sources)}` |",
        "",
        "---",
        ""
    ]
    
    # === VPN ПРИЛОЖЕНИЯ С ПРЕВЬЮ ===
    lines.extend(generate_vpn_preview_section())
    
    lines.extend([
        "",
        "---",
        "",
        "## 🚀 Быстрый старт",
        "",
        "1. **Выберите приложение** из таблицы выше и установите его",
        "2. **Нажмите на 👁️ иконку** чтобы посмотреть скриншот приложения",
        "3. **Нажмите на кнопку скачивания** (Windows/Android/macOS) чтобы загрузить файл",
        "4. **Найдите нужный конфиг** в разделах ниже",
        "5. **Нажмите на ссылку \"⬇️ Скачать\"**",
        "6. **Импортируйте** ссылку или файл в ваше VPN приложение",
        "",
        "> 💡 **Совет:** Конфигурации обновляются автоматически каждые 3 часа!",
        "",
        "---",
        "",
        "## 📂 Конфигурации по категориям",
        ""
    ])
    
    # === ТАБЛИЦЫ ПО КАТЕГОРИЯМ ===
    for category_key, cat_info in CATEGORIES.items():
        if category_key not in files_by_category or not files_by_category[category_key]:
            continue
            
        files = files_by_category[category_key]
        cat_total_configs = sum(f.get('total_configs', 0) for f in files)
        
        # Добавляем ссылку на фото в заголовок категории если есть
        photo = cat_info.get('photo')
        if photo:
            photo_url = generate_photo_url(photo)
            photo_link = f" [👁️]({photo_url})"
        else:
            photo_link = ""
        
        # Добавляем ссылки на скачивание в заголовок категории
        download_links = generate_download_links_section(category_key)
        if download_links:
            download_header = f"<br>💾 **Скачать:**{download_links}"
        else:
            download_header = ""
        
        lines.extend([
            f"### {cat_info['icon']} {cat_info['name']}{photo_link}{download_header}",
            "",
            f"> {cat_info['description']}",
            "",
            f"**Файлов:** `{len(files)}` | **Конфигураций:** `{format_number(cat_total_configs)}`",
            "",
            "| № | Название | Конфиги | Размер | Обновлено | Ссылка |",
            "|---|----------|---------|--------|-----------|--------|"
        ])
        
        for idx, file_info in enumerate(files, 1):
            protocols = file_info.get('protocols', {})
            protocols_badge = format_protocols_badge(protocols)
            total = file_info.get('total_configs', 0)
            download_url = generate_api_url(file_info['path'])
            
            lines.append(
                f"| {idx} | **{file_info['name']}**<br>{protocols_badge} | "
                f"`{format_number(total)}` | `{file_info['size_formatted']}` | "
                f"`{file_info['modified']}` | [⬇️ Скачать]({download_url}) |"
            )
        
        lines.append("")
    
    # === БЫСТРЫЙ ДОСТУП ===
    lines.extend([
        "---",
        "",
        "## 📋 Все файлы (быстрый доступ)",
        "",
        "<details>",
        "<summary>🔽 Нажмите чтобы развернуть список всех файлов</summary>",
        "",
        "```"
    ])
    
    for category_key in sorted(files_by_category.keys()):
        files = files_by_category[category_key]
        if not files:
            continue
            
        cat_info = CATEGORIES.get(category_key, {'name': category_key, 'icon': '📁'})
        lines.append(f"")
        lines.append(f"📁 {cat_info['name']}/")
        
        for file_info in files:
            download_url = generate_api_url(file_info['path'])
            lines.append(f"  ├── {file_info['filename']}")
            lines.append(f"  │   └── {download_url}")
    
        lines.extend([
        "```",
        "</details>",
        ""
    ])
    
    
    # === ИНФОРМАЦИЯ О БЛОКИРОВКАХ ===
    lines.extend([
        "---",
        "",
        "## 🚫 Как обходить CIDR и SNI блокировки",
        "",
        "### 📍 CIDR-блокировка (по IP-адресам)",
        "",
        "**Как блокируют:**  ",
        "Роскомнадзор добавляет целые диапазоны IP-адресов в реестр блокировок. Трафик на эти IP обрывается провайдером.",
        "",
        "**Как обходим:**  ",
        "В конфигах используются **white CIDR**-списки — разрешённые («чистые») диапазоны IP. VPN направляет трафик только через эти белые подсети, обходя заблокированные адреса.",
        "",
        "---",
        "",
        "### 🔠 SNI-блокировка (по имени сервера)",
        "",
        "**Как блокируют:**  ",
        "Провайдер видит **SNI** (Server Name Indication) — имя сайта в открытом виде при подключении (например, `youtube.com`). Если имя в чёрном списке — соединение разрывается.",
        "",
        "**Как обходим:**  ",
        "Используются **white SNI**-списки и технологии **Reality / uTLS**. Они маскируют настоящее имя сайта или подменяют его на «чистое», чтобы провайдер не мог определить цель.",
        "",
        "> 💡 **Простыми словами:**  ",
        "> - **CIDR** — блокировка по «адресу дома»  ",
        "> - **SNI** — блокировка по «названию на табличке»  ",
        "> - **White-списки** позволяют обходить обе блокировки, направляя трафик через разрешённые IP и домены.",
        "",
        "---",
        "",
        "## 🔄 Автоматическое обновление",
        "",
        "Этот репозиторий автоматически обновляется каждые **3 часа** через GitVerse CI/CD.",
        "",
        "### 📅 Расписание обновлений:",
        "- `00:00 MSK` - Ночное обновление",
        "- `03:00 MSK` - Раннее утро",
        "- `06:00 MSK` - Утро",
        "- `09:00 MSK` - Позднее утро",
        "- `12:00 MSK` - День",
        "- `15:00 MSK` - После обеда",
        "- `18:00 MSK` - Вечер",
        "- `21:00 MSK` - Поздний вечер",
        "",
        "---",
        "",
        "## 📝 Как добавить источник",
        "",
        "1. Отредактируйте файл `sources/urls.txt`",
        "2. Добавьте строку в формате: `URL|CATEGORY|NAME`",
        "3. Доступные категории: `nekobox`, `v2ray`, `happ`, `singbox`, `clash`, `tor`",
        "4. Создайте Pull Request или запушьте изменения",
        "",
        "**Пример:**",
        "```",
        "https://example.com/config.txt|v2ray|My Config",
        "```",
        "",
        "---",
        "",
        "<div align=\"center\">",
        "",
        "**🤖 Автоматизировано с любовью для свободного интернета**",
        "",
        f"*Последнее обновление: {datetime.now().strftime('%Y-%m-%d %H:%M:%S MSK')}*",
        "",
        "</div>"
    ])
    
    return '\n'.join(lines)

def main():
    """Основная функция"""
    print("📝 Генерация README.md...")
    
    metadata = load_metadata()
    print(f"📊 Загружено метаданных: {metadata.get('total_sources', 0)} источников")
    
    files_by_category = scan_vpn_files()
    total_files = sum(len(files) for files in files_by_category.values())
    print(f"📁 Найдено файлов: {total_files}")
    
    files_by_category = merge_with_metadata(files_by_category, metadata)
    
    readme_content = generate_readme(files_by_category, metadata)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✅ README.md успешно сгенерирован!")
    print(f"🔗 API-ссылки: https://gitverse.ru/api/repos/...")
    print(f"📸 Фото-превью: https://gitverse.ru/api/repos/.../foto/...")
    print(f"💾 Добавлены прямые ссылки на скачивание с Mail.ru Cloud")

if __name__ == "__main__":
    main()
