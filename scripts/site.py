#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор сайта для GitVerse Pages
Автоматически создаёт index.html из README.md
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

# ==================== КОНФИГУРАЦИЯ ====================
README_PATH = Path("README.md")
INDEX_PATH = Path("index.html")
PAGES_CONFIG_PATH = Path(".gitverse/pages.yml")
VPNMIRRORS_PATH = Path("VPNMIRRORS")
REPO_NAME = "RUVIPIEN/russian-white-bolt_fix"
SITE_URL = f"https://{REPO_NAME.replace('/', '.')}.gitverse.ru"

# ==================== СТИЛИ ====================
CSS_STYLES = """
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background: #0a0a0f;
        color: #e0e0e0;
        line-height: 1.7;
        padding: 20px;
    }
    .container {
        max-width: 1200px;
        margin: 0 auto;
        background: #0f0f1a;
        padding: 30px;
        border-radius: 16px;
        border: 1px solid #1a1a2e;
        box-shadow: 0 0 60px rgba(0, 212, 255, 0.05);
    }
    h1 { color: #00d4ff; font-size: 2.4em; border-bottom: 2px solid #00d4ff; padding-bottom: 15px; margin-bottom: 25px; text-shadow: 0 0 30px rgba(0,212,255,0.2); }
    h2 { color: #00d4ff; margin-top: 40px; font-size: 1.8em; border-left: 4px solid #00d4ff; padding-left: 15px; }
    h3 { color: #44ff88; margin-top: 30px; font-size: 1.3em; }
    h4 { color: #ffaa44; margin-top: 20px; }
    a { color: #00d4ff; text-decoration: none; transition: all 0.3s; }
    a:hover { color: #44ff88; text-decoration: underline; }
    p { margin: 12px 0; }
    ul, ol { margin: 12px 0 12px 25px; }
    li { margin: 6px 0; }
    img { max-width: 100%; border-radius: 8px; border: 1px solid #1a1a2e; }
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 14px;
        border-radius: 8px;
        overflow: hidden;
        display: block;
        overflow-x: auto;
    }
    th {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        color: #00d4ff;
        padding: 14px 12px;
        text-align: left;
        font-weight: 600;
        border-bottom: 2px solid #00d4ff;
        white-space: nowrap;
    }
    td {
        padding: 12px;
        border-bottom: 1px solid #1a1a2e;
        vertical-align: middle;
    }
    tr:hover td { background: #1a1a2e; }
    code {
        background: #1a1a2e;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 13px;
        color: #44ff88;
        font-family: "Courier New", monospace;
        word-break: break-all;
    }
    pre {
        background: #0a0a12;
        padding: 15px;
        border-radius: 8px;
        overflow-x: auto;
        border: 1px solid #1a1a2e;
        font-size: 13px;
    }
    pre code {
        background: none;
        padding: 0;
        color: #e0e0e0;
    }
    .badge {
        display: inline-block;
        background: #1a1a2e;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        border: 1px solid #333;
        margin: 2px;
    }
    .download-btn {
        background: #00d4ff;
        color: #000 !important;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 13px;
        display: inline-block;
        transition: all 0.3s;
    }
    .download-btn:hover {
        background: #44ff88;
        text-decoration: none !important;
        transform: scale(1.05);
    }
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 15px;
        margin: 20px 0;
    }
    .stat-card {
        background: #1a1a2e;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #222;
    }
    .stat-number {
        font-size: 28px;
        font-weight: bold;
        color: #00d4ff;
    }
    .stat-label {
        color: #888;
        font-size: 13px;
        margin-top: 4px;
    }
    details {
        background: #111;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
        border: 1px solid #1a1a2e;
    }
    details > summary {
        cursor: pointer;
        color: #00d4ff;
        font-weight: bold;
        font-size: 16px;
        padding: 5px 0;
    }
    details > summary:hover { color: #44ff88; }
    details > *:not(summary) { 
        padding: 10px 0 0 10px; 
        border-left: 2px solid #1a1a2e;
        margin-left: 10px;
    }
    .footer {
        text-align: center;
        margin-top: 50px;
        padding-top: 25px;
        border-top: 1px solid #1a1a2e;
        color: #555;
        font-size: 14px;
    }
    .footer a { color: #666; }
    .footer a:hover { color: #00d4ff; }
    .icon { font-size: 1.2em; }
    .text-center { text-align: center; }
    .text-muted { color: #888; }
    .site-link {
        display: inline-block;
        background: linear-gradient(135deg, #00d4ff, #44ff88);
        color: #000 !important;
        padding: 8px 18px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 14px;
        transition: all 0.3s;
        border: none;
    }
    .site-link:hover {
        transform: scale(1.05);
        text-decoration: none !important;
        box-shadow: 0 0 30px rgba(0,212,255,0.3);
    }
    .repo-link {
        display: inline-block;
        background: #1a1a2e;
        padding: 8px 16px;
        border-radius: 8px;
        border: 1px solid #00d4ff;
        color: #00d4ff;
        font-size: 14px;
        transition: all 0.3s;
    }
    .repo-link:hover {
        background: #00d4ff;
        color: #000 !important;
        text-decoration: none;
    }
    @media (max-width: 768px) {
        .container { padding: 15px; }
        table { font-size: 12px; }
        td, th { padding: 8px 6px; }
        .stats-grid { grid-template-columns: repeat(2, 1fr); }
        h1 { font-size: 1.8em; }
        h2 { font-size: 1.4em; }
        .header-buttons { flex-direction: column; align-items: stretch; gap: 8px; }
    }
    .glow-text { color: #00d4ff; text-shadow: 0 0 20px rgba(0,212,255,0.3); }
</style>
"""

# ==================== ПАРСЕР MARKDOWN ====================

def parse_inline(text: str) -> str:
    """Обрабатывает inline-элементы"""
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}" loading="lazy">', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: f'<a href="{m.group(2)}" target="_blank">{m.group(1)}</a>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text

def parse_markdown_to_html(content: str) -> str:
    """Превращает Markdown в HTML"""
    lines = content.split('\n')
    html_parts = []
    in_code_block = False
    in_table = False
    in_list = False
    list_type = None
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.startswith('```'):
            in_code_block = not in_code_block
            if in_code_block:
                html_parts.append(f'<pre><code>')
            else:
                html_parts.append('</code></pre>')
            i += 1
            continue
        
        if in_code_block:
            html_parts.append(line)
            i += 1
            continue
        
        if not line.strip():
            if in_table:
                in_table = False
                html_parts.append('</tbody></table>')
            if in_list:
                in_list = False
                html_parts.append('</ul>' if list_type == 'ul' else '</ol>')
            html_parts.append('')
            i += 1
            continue
        
        if line.strip().startswith('<details') or line.strip().startswith('</details>') or \
           line.strip().startswith('<summary') or line.strip().startswith('</summary>'):
            html_parts.append(line)
            i += 1
            continue
        
        header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if header_match:
            level = len(header_match.group(1))
            text = parse_inline(header_match.group(2))
            html_parts.append(f'<h{level}>{text}</h{level}>')
            i += 1
            continue
        
        if '|' in line and not line.startswith('|---'):
            if not in_table:
                in_table = True
                cells = [c.strip() for c in line.split('|')[1:-1]]
                html_parts.append('<table><thead><tr>')
                for cell in cells:
                    html_parts.append(f'<th>{parse_inline(cell)}</th>')
                html_parts.append('</tr></thead><tbody>')
            else:
                if re.match(r'^\s*\|?\s*:?-{3,}:?\s*\|', line):
                    i += 1
                    continue
                cells = [c.strip() for c in line.split('|')[1:-1]]
                html_parts.append('<tr>')
                for cell in cells:
                    html_parts.append(f'<td>{parse_inline(cell)}</td>')
                html_parts.append('</tr>')
            i += 1
            continue
        elif in_table:
            in_table = False
            html_parts.append('</tbody></table>')
            continue
        
        ul_match = re.match(r'^[\-\*]\s+(.+)$', line)
        ol_match = re.match(r'^\d+\.\s+(.+)$', line)
        
        if ul_match or ol_match:
            if not in_list:
                in_list = True
                list_type = 'ul' if ul_match else 'ol'
                html_parts.append(f'<{list_type}>')
            text = parse_inline(ul_match.group(1) if ul_match else ol_match.group(1))
            html_parts.append(f'<li>{text}</li>')
            i += 1
            continue
        elif in_list:
            in_list = False
            html_parts.append('</ul>' if list_type == 'ul' else '</ol>')
            continue
        
        if re.match(r'^[\-\*_]{3,}$', line.strip()):
            html_parts.append('<hr>')
            i += 1
            continue
        
        html_parts.append(f'<p>{parse_inline(line)}</p>')
        i += 1
    
    if in_table:
        html_parts.append('</tbody></table>')
    if in_list:
        html_parts.append('</ul>' if list_type == 'ul' else '</ol>')
    
    return '\n'.join(html_parts)

# ==================== ОСНОВНАЯ ФУНКЦИЯ ====================

def ensure_pages_config():
    """Создаёт конфиг для GitVerse Pages если его нет"""
    PAGES_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not PAGES_CONFIG_PATH.exists():
        with open(PAGES_CONFIG_PATH, 'w', encoding='utf-8') as f:
            f.write("""# GitVerse Pages Configuration
enabled: true
source: ./
output: ./
""")
        print("✅ Создан .gitverse/pages.yml")
        return True
    return False

def generate_html():
    """Генерирует index.html из README.md"""
    print("🌐 Генерация сайта для GitVerse Pages...")
    
    # Создаём конфиг Pages
    ensure_pages_config()
    
    if not README_PATH.exists():
        print("⚠️ README.md не найден!")
        return False
    
    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Статистика
    stats = {'files': 0, 'configs': 0, 'sources': 0}
    
    if VPNMIRRORS_PATH.exists():
        for _ in VPNMIRRORS_PATH.rglob('*.txt'):
            stats['files'] += 1
    
    metadata_path = VPNMIRRORS_PATH / "metadata.json"
    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
            stats['sources'] = meta.get('stats', {}).get('success', 0)
            stats['configs'] = meta.get('stats', {}).get('total_keys', 0)
    
    parsed_content = parse_markdown_to_html(content)
    
    html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VPN White-Lists | Обновляемые конфиги</title>
    <meta name="description" content="Автоматически обновляемые белые списки для обхода блокировок в России. {stats['configs']} конфигураций, {stats['files']} файлов.">
    <meta property="og:title" content="VPN White-Lists для России">
    <meta property="og:description" content="Автоматически обновляемые белые списки. {stats['configs']} конфигураций.">
    <meta property="og:url" content="{SITE_URL}">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="canonical" href="{SITE_URL}">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🔒</text></svg>">
    {CSS_STYLES}
</head>
<body>
    <div class="container">
        <!-- Шапка -->
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:20px;">
            <div>
                <h1 style="border:none; padding:0; margin:0;">🔒 VPN White-Lists</h1>
                <p style="color:#888; margin-top:4px;">Автоматически обновляемые белые списки для обхода блокировок</p>
            </div>
            <div class="header-buttons" style="display:flex; gap:10px; flex-wrap:wrap;">
                <a href="{SITE_URL}" class="site-link" target="_blank">🌐 Открыть сайт</a>
                <a href="https://gitverse.ru/{REPO_NAME}" class="repo-link" target="_blank">📂 Репозиторий</a>
            </div>
        </div>
        
        <!-- Информация о сайте -->
        <div style="background: #1a1a2e; padding: 12px 18px; border-radius: 8px; margin-bottom: 20px; border-left: 3px solid #44ff88;">
            <p style="margin: 0; font-size: 14px; color: #888;">
                🌐 Сайт доступен по адресу: <a href="{SITE_URL}" style="font-weight: bold;">{SITE_URL}</a>
                <span style="color: #444; margin: 0 10px;">|</span>
                🔄 Обновлено: {datetime.now().strftime('%H:%M MSK')}
            </p>
        </div>
        
        <!-- Статистика -->
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-number">{stats['files']}</div><div class="stat-label">📁 Файлов</div></div>
            <div class="stat-card"><div class="stat-number">{stats['configs']}</div><div class="stat-label">🔗 Конфигураций</div></div>
            <div class="stat-card"><div class="stat-number">{stats['sources']}</div><div class="stat-label">✅ Рабочих источников</div></div>
            <div class="stat-card"><div class="stat-number">{datetime.now().strftime('%d.%m.%Y')}</div><div class="stat-label">📅 Последнее обновление</div></div>
        </div>
        
        <!-- Содержимое README -->
        {parsed_content}
        
        <!-- Футер -->
        <div class="footer">
            <p>🤖 Автоматизировано с любовью для свободного интернета</p>
            <p style="font-size:12px; color:#444;">
                <a href="https://gitverse.ru/{REPO_NAME}">📂 Исходный код</a> &bull; 
                <a href="{SITE_URL}">🌐 Сайт</a> &bull;
                <a href="https://gitverse.ru/{REPO_NAME}/blob/master/README.md">📄 README</a> &bull;
                Обновляется каждые 3 часа &bull; 
                <a href="#top">⬆ Наверх</a>
            </p>
            <p style="font-size:11px; color:#333; margin-top:5px;">
                📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S MSK')}
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ index.html создан! Размер: {len(html_content):,} символов")
    print(f"📁 Статистика: {stats['files']} файлов, {stats['configs']} конфигов")
    print(f"🌐 Сайт будет доступен по адресу: {SITE_URL}")
    print(f"📂 Репозиторий: https://gitverse.ru/{REPO_NAME}")
    return True

if __name__ == "__main__":
    generate_html()