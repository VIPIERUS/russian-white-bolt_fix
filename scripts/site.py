#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор сайта для GitVerse Pages
Анализирует структуру README.md и создаёт красивый index.html
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
REPO_URL = f"https://gitverse.ru/{REPO_NAME}"

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
    /* ===== МЕНЮ ===== */
    .top-menu {
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
        padding: 12px 0;
        margin-bottom: 25px;
        border-bottom: 1px solid #1a1a2e;
    }
    .top-menu a {
        color: #888;
        text-decoration: none;
        font-size: 14px;
        transition: all 0.3s;
        padding: 4px 10px;
        border-radius: 6px;
    }
    .top-menu a:hover {
        color: #00d4ff;
        background: #1a1a2e;
    }
    .top-menu a.active {
        color: #00d4ff;
        background: #1a1a2e;
    }
    /* ===== ОСТАЛЬНЫЕ СТИЛИ ===== */
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
    /* ===== ФУТЕР С ЛИЦЕНЗИЕЙ ===== */
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
    .footer-license {
        font-size: 12px;
        color: #444;
        margin-top: 10px;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.6;
    }
    .footer-license strong { color: #666; }
    .update-badge {
        display: inline-block;
        background: #1a1a2e;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        border: 1px solid #44ff88;
        color: #44ff88;
        margin-left: 10px;
    }
    @media (max-width: 768px) {
        .container { padding: 15px; }
        table { font-size: 12px; }
        td, th { padding: 8px 6px; }
        .stats-grid { grid-template-columns: repeat(2, 1fr); }
        h1 { font-size: 1.8em; }
        h2 { font-size: 1.4em; }
        .top-menu { gap: 10px; }
        .top-menu a { font-size: 12px; padding: 4px 8px; }
    }
    .glow-text { color: #00d4ff; text-shadow: 0 0 20px rgba(0,212,255,0.3); }
</style>
"""

# ==================== АНАЛИЗ СТРУКТУРЫ README ====================

def parse_inline(text: str) -> str:
    """Обрабатывает inline-элементы: ссылки, изображения, код, жирный, курсив"""
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}" loading="lazy">', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: f'<a href="{m.group(2)}" target="_blank">{m.group(1)}</a>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text

def parse_markdown_to_html(content: str) -> str:
    """Анализирует структуру README и превращает в красивый HTML"""
    lines = content.split('\n')
    html_parts = []
    in_code_block = False
    in_table = False
    in_list = False
    list_type = None
    in_details = False
    details_stack = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # ===== КОДОВЫЕ БЛОКИ =====
        if line.startswith('```'):
            in_code_block = not in_code_block
            if in_code_block:
                lang = line[3:].strip()
                html_parts.append(f'<pre><code class="language-{lang}">')
            else:
                html_parts.append('</code></pre>')
            i += 1
            continue
        
        if in_code_block:
            html_parts.append(line)
            i += 1
            continue
        
        # ===== ПУСТЫЕ СТРОКИ =====
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
        
        # ===== СПОЙЛЕРЫ (details/summary) =====
        if line.strip().startswith('<details'):
            in_details = True
            details_stack.append('details')
            html_parts.append(line)
            i += 1
            continue
        if line.strip().startswith('</details>'):
            in_details = False
            if details_stack:
                details_stack.pop()
            html_parts.append(line)
            i += 1
            continue
        if line.strip().startswith('<summary'):
            html_parts.append(line)
            i += 1
            continue
        if line.strip().startswith('</summary>'):
            html_parts.append(line)
            i += 1
            continue
        
        # ===== ЗАГОЛОВКИ =====
        header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if header_match:
            level = len(header_match.group(1))
            text = parse_inline(header_match.group(2))
            html_parts.append(f'<h{level}>{text}</h{level}>')
            i += 1
            continue
        
        # ===== ТАБЛИЦЫ =====
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
        
        # ===== СПИСКИ =====
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
        
        # ===== ГОРИЗОНТАЛЬНАЯ ЛИНИЯ =====
        if re.match(r'^[\-\*_]{3,}$', line.strip()):
            html_parts.append('<hr>')
            i += 1
            continue
        
        # ===== ОБЫЧНЫЙ АБЗАЦ =====
        html_parts.append(f'<p>{parse_inline(line)}</p>')
        i += 1
    
    # Закрываем незакрытые элементы
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
    """Генерирует index.html из README.md с анализом структуры"""
    print("🌐 Генерация сайта с анализом структуры README...")
    
    # Создаём конфиг Pages
    ensure_pages_config()
    
    if not README_PATH.exists():
        print("⚠️ README.md не найден!")
        return False
    
    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # ===== АНАЛИЗИРУЕМ СТРУКТУРУ =====
    print("📊 Анализ структуры README.md...")
    
    # Собираем статистику
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
    
    # Находим все заголовки для меню
    headers = []
    for line in content.split('\n'):
        match = re.match(r'^(#{2,3})\s+(.+)$', line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            # Убираем эмодзи и спецсимволы для ID
            anchor = re.sub(r'[^a-zA-Z0-9]', '', title.lower())[:30]
            headers.append({'level': level, 'title': title, 'anchor': anchor})
    
    # Парсим содержимое
    parsed_content = parse_markdown_to_html(content)
    
    # ===== СОЗДАЁМ МЕНЮ =====
    menu_html = '<div class="top-menu">\n'
    menu_html += f'<a href="#top" class="active">🏠 Главная</a>\n'
    for h in headers[:8]:  # Ограничиваем меню 8 пунктами
        menu_html += f'<a href="#{h["anchor"]}">{h["title"]}</a>\n'
    menu_html += f'<a href="#license">📄 Лицензия</a>\n'
    menu_html += '</div>\n'
    
    # ===== ЛИЦЕНЗИЯ =====
    license_text = """
    <div id="license" style="margin-top: 30px; padding: 20px; background: #1a1a2e; border-radius: 8px; border-left: 3px solid #ffaa44;">
        <h3 style="color: #ffaa44; margin-top: 0;">📄 Лицензия и отказ от ответственности</h3>
        <p style="color: #888; font-size: 14px; line-height: 1.8;">
            <strong style="color: #aaa;">Источники:</strong> Все конфигурации собраны из открытых интернет-источников.
            Мы не являемся авторами этих конфигураций и не несём ответственности за их содержимое.
        </p>
        <p style="color: #888; font-size: 14px; line-height: 1.8;">
            <strong style="color: #aaa;">Отказ от ответственности:</strong> Данный сайт и репозиторий созданы исключительно 
            в <strong style="color: #aaa;">информационных и образовательных целях</strong>. Мы не пропагандируем и не поощряем 
            использование VPN в обход законодательства. Все материалы предоставлены "как есть" без каких-либо гарантий.
        </p>
        <p style="color: #888; font-size: 14px; line-height: 1.8;">
            <strong style="color: #aaa;">Авторские права:</strong> Все права на контент принадлежат их законным владельцам. 
            Если вы являетесь правообладателем и считаете, что ваш материал используется неправомерно, 
            свяжитесь с нами для его удаления.
        </p>
        <p style="color: #666; font-size: 13px; margin-top: 10px;">
            🔄 Последнее обновление: <span style="color: #44ff88;">{}</span>
        </p>
    </div>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S MSK'))
    
    # ===== ФОРМИРУЕМ HTML =====
    html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VPN White-Lists | Обновляемые конфиги</title>
    <meta name="description" content="Автоматически обновляемые белые списки для обхода блокировок в России. {stats['configs']} конфигураций, {stats['files']} файлов.">
    <meta property="og:title" content="VPN White-Lists для России">
    <meta property="og:description" content="Автоматически обновляемые белые списки. {stats['configs']} конфигураций.">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="canonical" href="{REPO_URL}">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🔒</text></svg>">
    {CSS_STYLES}
</head>
<body>
    <div class="container" id="top">
        <!-- Шапка -->
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:10px;">
            <div>
                <h1 style="border:none; padding:0; margin:0;">🔒 VPN White-Lists</h1>
                <p style="color:#888; margin-top:4px;">Автоматически обновляемые белые списки для обхода блокировок</p>
            </div>
            <div style="text-align:right;">
                <span class="badge">🔄 Обновлено: {datetime.now().strftime('%H:%M MSK')}</span>
                <br>
                <a href="{REPO_URL}" class="repo-link" target="_blank">📂 Репозиторий</a>
            </div>
        </div>
        
        <!-- Меню -->
        {menu_html}
        
        <!-- Статистика -->
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-number">{stats['files']}</div><div class="stat-label">📁 Файлов</div></div>
            <div class="stat-card"><div class="stat-number">{stats['configs']}</div><div class="stat-label">🔗 Конфигураций</div></div>
            <div class="stat-card"><div class="stat-number">{stats['sources']}</div><div class="stat-label">✅ Рабочих источников</div></div>
            <div class="stat-card"><div class="stat-number">{datetime.now().strftime('%d.%m.%Y')}</div><div class="stat-label">📅 Последнее обновление</div></div>
        </div>
        
        <!-- Содержимое README -->
        {parsed_content}
        
        <!-- Лицензия -->
        {license_text}
        
        <!-- Футер -->
        <div class="footer">
            <p>🤖 Автоматизировано с любовью для свободного интернета</p>
            <p style="font-size:12px; color:#444;">
                <a href="{REPO_URL}">📂 Исходный код</a> &bull; 
                <a href="{REPO_URL}/blob/master/README.md">📄 README</a> &bull;
                Обновляется каждые 3 часа &bull; 
                <a href="#top">⬆ Наверх</a>
            </p>
            <div class="footer-license">
                <strong>⚠️ Важно:</strong> Все материалы предоставлены "как есть" для информационных целей.
                Использование VPN может регулироваться законодательством вашей страны.
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ index.html создан! Размер: {len(html_content):,} символов")
    print(f"📁 Статистика: {stats['files']} файлов, {stats['configs']} конфигов")
    print(f"📊 Найдено заголовков для меню: {len(headers)}")
    print(f"📂 Репозиторий: {REPO_URL}")
    return True

if __name__ == "__main__":
    generate_html()