#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор сайта для GitVerse Pages с интеграцией Config Generator V1.1
Страницы:
- / - главная (README)
- /checker - Config Generator V1.1 (Xray / V2Ray / Sing‑box)
- /about - информация об авторе
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# ==================== КОНФИГУРАЦИЯ ====================
README_PATH = Path("README.md")
VPNMIRRORS_PATH = Path("VPNMIRRORS")
REPO_NAME = "RUVIPIEN/russian-white-bolt_fix"
REPO_URL = f"https://gitverse.ru/{REPO_NAME}"
AUTHOR_REPO = "https://gitverse.ru/RUVIPIEN/"

# ==================== СТИЛИ ОБЩИЕ ====================
COMMON_CSS = """
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
        max-width: 1400px;
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
        gap: 10px;
        flex-wrap: wrap;
        padding: 12px 0;
        margin-bottom: 25px;
        border-bottom: 1px solid #1a1a2e;
        align-items: center;
    }
    .top-menu a {
        color: #888;
        text-decoration: none;
        font-size: 14px;
        transition: all 0.3s;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 500;
    }
    .top-menu a:hover {
        color: #00d4ff;
        background: #1a1a2e;
    }
    .top-menu a.active {
        color: #00d4ff;
        background: #1a1a2e;
    }
    .top-menu a.checker-btn {
        background: linear-gradient(135deg, #00d4ff, #44ff88);
        color: #000 !important;
        font-weight: 700;
        padding: 6px 18px;
        border-radius: 20px;
    }
    .top-menu a.checker-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
    }
    .top-menu a.about-btn {
        background: linear-gradient(135deg, #ff6b6b, #ffd93d);
        color: #000 !important;
        font-weight: 700;
        padding: 6px 18px;
        border-radius: 20px;
    }
    .top-menu a.about-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 0 30px rgba(255, 107, 107, 0.3);
    }
    .top-menu .menu-spacer { flex: 1; }
    .top-menu .repo-badge {
        color: #555;
        font-size: 12px;
        padding: 4px 12px;
        background: #1a1a2e;
        border-radius: 20px;
    }
    .top-menu .repo-badge a { color: #00d4ff; padding: 0; }
    .top-menu .repo-badge a:hover { background: none; color: #44ff88; }
    
    @media (max-width: 768px) {
        .container { padding: 15px; }
        .top-menu { gap: 6px; }
        .top-menu a { font-size: 12px; padding: 4px 10px; }
        .top-menu a.checker-btn, .top-menu a.about-btn { padding: 4px 14px; font-size: 12px; }
    }
    
    /* ===== ФУТЕР ===== */
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
    
    /* ===== ЛИЦЕНЗИЯ ===== */
    .license-box {
        margin-top: 30px;
        padding: 25px;
        background: #1a1a2e;
        border-radius: 12px;
        border-left: 4px solid #ffaa44;
    }
    .license-box h3 { color: #ffaa44; margin-top: 0; font-size: 1.3em; }
    .license-box p { color: #999; font-size: 14px; line-height: 1.8; }
    .license-box strong { color: #ccc; }
    .license-box .highlight { color: #44ff88; }
    
    /* ===== ОБ АВТОРЕ ===== */
    .about-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 25px;
        margin: 25px 0;
    }
    .about-card {
        background: #1a1a2e;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #222;
        transition: all 0.3s;
    }
    .about-card:hover {
        border-color: #00d4ff;
        transform: translateY(-3px);
        box-shadow: 0 10px 40px rgba(0, 212, 255, 0.05);
    }
    .about-card .icon { font-size: 2.5em; margin-bottom: 10px; }
    .about-card h3 { color: #00d4ff; font-size: 1.2em; margin-bottom: 8px; }
    .about-card p { color: #999; font-size: 14px; line-height: 1.6; }
    .about-card .tag {
        display: inline-block;
        background: #0a0a12;
        padding: 2px 12px;
        border-radius: 20px;
        font-size: 12px;
        color: #44ff88;
        border: 1px solid #1a1a2e;
        margin: 3px 3px 3px 0;
    }
    .about-card .repo-link {
        display: inline-block;
        margin-top: 10px;
        color: #00d4ff;
        font-size: 13px;
        text-decoration: none;
    }
    .about-card .repo-link:hover { color: #44ff88; text-decoration: underline; }
    
    @media (max-width: 768px) {
        .about-grid { grid-template-columns: 1fr; }
    }
</style>
"""

# ==================== HTML КОНСТРУКТОРЫ ====================

def get_menu(active_page='/'):
    """Генерирует меню с подсветкой активной страницы"""
    pages = {
        '/': '🏠 Главная',
        '/checker': '⚡ Чекер',
        '/about': '👤 Об авторе'
    }
    
    menu_html = '<div class="top-menu">\n'
    for url, label in pages.items():
        is_active = 'active' if url == active_page else ''
        if url == '/checker':
            is_active += ' checker-btn'
        elif url == '/about':
            is_active += ' about-btn'
        menu_html += f'    <a href="{url}" class="{is_active}">{label}</a>\n'
    
    menu_html += f'    <span class="menu-spacer"></span>\n'
    menu_html += f'    <span class="repo-badge">📂 <a href="{REPO_URL}" target="_blank">Репозиторий</a></span>\n'
    menu_html += '</div>\n'
    return menu_html

# ==================== АНАЛИЗ README ====================

def parse_inline(text: str) -> str:
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}" loading="lazy">', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: f'<a href="{m.group(2)}" target="_blank">{m.group(1)}</a>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text

def parse_markdown_to_html(content: str) -> str:
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
        
        html_parts.append(f'<p>{parse_inline(line)}</p>')
        i += 1
    
    if in_table:
        html_parts.append('</tbody></table>')
    if in_list:
        html_parts.append('</ul>' if list_type == 'ul' else '</ol>')
    
    return '\n'.join(html_parts)

# ==================== ЛИЦЕНЗИЯ ====================

def get_license_html():
    """Возвращает HTML-блок с лицензией и отказом от ответственности"""
    return f"""
    <div class="license-box">
        <h3>📄 Лицензия и отказ от ответственности</h3>
        <p>
            <strong>Источники:</strong> Все конфигурации собраны из открытых интернет-источников.
            Мы не являемся авторами этих конфигураций и не несём ответственности за их содержимое.
        </p>
        <p>
            <strong>Отказ от ответственности:</strong> Данный сайт и репозиторий созданы исключительно 
            в <strong>информационных и образовательных целях</strong>. Мы не пропагандируем и не поощряем 
            использование VPN в обход законодательства. Все материалы предоставлены <strong>"как есть"</strong> 
            без каких-либо гарантий.
        </p>
        <p>
            <strong>Авторские права:</strong> Все права на контент принадлежат их законным владельцам. 
            Если вы являетесь правообладателем и считаете, что ваш материал используется неправомерно, 
            свяжитесь с нами для его удаления.
        </p>
        <p style="margin-top:10px; color:#666; font-size:13px;">
            🔄 Последнее обновление: <span class="highlight">{datetime.now().strftime('%Y-%m-%d %H:%M:%S MSK')}</span>
        </p>
    </div>
    """

# ==================== ОБ АВТОРЕ ====================

def get_about_html():
    """Возвращает HTML-блок с информацией об авторе"""
    return """
    <div style="margin-bottom:25px;">
        <h2 style="color:#00d4ff; border-left:4px solid #00d4ff; padding-left:15px; margin-bottom:10px;">👤 Об авторе</h2>
        <p style="color:#888; font-size:16px;">Привет! Я <strong style="color:#00d4ff;">RUVIPIEN</strong> — создатель этого проекта и многих других.</p>
    </div>
    
    <div class="about-grid">
        <div class="about-card">
            <div class="icon">✍️</div>
            <h3>Писатель</h3>
            <p>Пишу стихи и прозу. Если вам нужен автор для текстов — обращайтесь!</p>
            <span class="tag">поэзия</span>
            <span class="tag">проза</span>
            <span class="tag">тексты</span>
        </div>
        
        <div class="about-card">
            <div class="icon">🎵</div>
            <h3>Музыкант</h3>
            <p>Обожаю слушать музыку 24/7. Вдохновляюсь разными жанрами — от классики до электроники.</p>
            <span class="tag">🎧 24/7</span>
            <span class="tag">меломан</span>
        </div>
        
        <div class="about-card">
            <div class="icon">🎨</div>
            <h3>Художник</h3>
            <p>Раньше много рисовал, сейчас не хватает практики. Но любовь к искусству осталась.</p>
            <span class="tag">графика</span>
            <span class="tag">живопись</span>
            <span class="tag">digital art</span>
        </div>
        
        <div class="about-card">
            <div class="icon">💻</div>
            <h3>Разработчик</h3>
            <p>Создаю мини-проекты на Python и других языках. ТВ, VPN, сборщики конфигов — моя стихия.</p>
            <span class="tag">Python</span>
            <span class="tag">Flask</span>
            <span class="tag">bash</span>
            <br>
            <a href="https://gitverse.ru/RUVIPIEN/" target="_blank" class="repo-link">📂 Все проекты →</a>
        </div>
    </div>
    
    <div style="background:#1a1a2e; padding:20px; border-radius:12px; border:1px solid #222; margin-top:10px;">
        <p style="color:#888; font-size:14px; text-align:center;">
            🌟 <strong style="color:#ffd93d;">"Творчество — это способ быть свободным"</strong> 🌟
        </p>
        <p style="color:#555; font-size:13px; text-align:center; margin-top:5px;">
            <a href="https://gitverse.ru/RUVIPIEN/" target="_blank" style="color:#00d4ff; text-decoration:none;">
                🔗 Мой репозиторий на GitVerse
            </a>
        </p>
    </div>
    """

# ==================== FLASK МАРШРУТЫ ====================

@app.route('/')
def index():
    """Главная страница с README"""
    if not README_PATH.exists():
        return "<h1>README.md не найден</h1>"
    
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
    
    stats_html = f"""
    <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:15px; margin:20px 0;">
        <div style="background:#1a1a2e; padding:15px; border-radius:8px; text-align:center; border:1px solid #222;">
            <div style="font-size:28px; font-weight:bold; color:#00d4ff;">{stats['files']}</div>
            <div style="color:#888; font-size:13px;">📁 Файлов</div>
        </div>
        <div style="background:#1a1a2e; padding:15px; border-radius:8px; text-align:center; border:1px solid #222;">
            <div style="font-size:28px; font-weight:bold; color:#00d4ff;">{stats['configs']}</div>
            <div style="color:#888; font-size:13px;">🔗 Конфигураций</div>
        </div>
        <div style="background:#1a1a2e; padding:15px; border-radius:8px; text-align:center; border:1px solid #222;">
            <div style="font-size:28px; font-weight:bold; color:#00d4ff;">{stats['sources']}</div>
            <div style="color:#888; font-size:13px;">✅ Источников</div>
        </div>
        <div style="background:#1a1a2e; padding:15px; border-radius:8px; text-align:center; border:1px solid #222;">
            <div style="font-size:28px; font-weight:bold; color:#44ff88;">{datetime.now().strftime('%d.%m')}</div>
            <div style="color:#888; font-size:13px;">📅 Обновлено</div>
        </div>
    </div>
    """
    
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VPN White-Lists | Обновляемые конфиги</title>
    {COMMON_CSS}
</head>
<body>
    <div class="container">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:10px;">
            <div>
                <h1 style="color:#00d4ff; border:none; padding:0; margin:0;">🔒 VPN White-Lists</h1>
                <p style="color:#888; margin-top:4px;">Автоматически обновляемые белые списки для обхода блокировок</p>
            </div>
        </div>
        
        {get_menu('/')}
        {stats_html}
        {parsed_content}
        {get_license_html()}
        
        <div class="footer">
            <p>🤖 Автоматизировано с любовью для свободного интернета</p>
            <p style="font-size:12px; color:#444;">
                <a href="{REPO_URL}">📂 Исходный код</a> &bull; 
                Обновляется каждые 3 часа &bull; 
                <a href="#top">⬆ Наверх</a>
            </p>
        </div>
    </div>
</body>
</html>"""
    return render_template_string(html)


@app.route('/checker')
def checker():
    """Страница с Config Generator V1.1"""
    checker_html_path = Path("checker.html")
    if checker_html_path.exists():
        with open(checker_html_path, 'r', encoding='utf-8') as f:
            checker_content = f.read()
    else:
        checker_content = get_checker_html()
    
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Config Generator V1.1 – Xray / V2Ray / Sing‑box</title>
    {COMMON_CSS}
    <style>
        .checker-wrapper {{
            margin-top: 10px;
        }}
        .checker-wrapper iframe {{
            width: 100%;
            min-height: 800px;
            border: none;
            border-radius: 12px;
            background: #0d1117;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:10px;">
            <div>
                <h1 style="color:#00d4ff; border:none; padding:0; margin:0;">⚡ Config Generator</h1>
                <p style="color:#888; margin-top:4px;">Xray · V2Ray · Sing‑box – VLESS / VMess / Trojan / Shadowsocks</p>
            </div>
        </div>
        
        {get_menu('/checker')}
        
        <div class="checker-wrapper">
            {checker_content}
        </div>
        
        <div class="footer">
            <p>⚡ Config Generator V1.1 — от <a href="https://github.com/SulgX" target="_blank">SulgX</a></p>
            <p style="font-size:12px; color:#444;">
                <a href="https://github.com/SulgX/ConfigGenerator" target="_blank">📖 README</a> &bull;
                <a href="/">🏠 На главную</a>
            </p>
        </div>
    </div>
</body>
</html>"""
    return render_template_string(html)


@app.route('/about')
def about():
    """Страница «Об авторе» с лицензией"""
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Об авторе | VPN White-Lists</title>
    {COMMON_CSS}
</head>
<body>
    <div class="container">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:10px;">
            <div>
                <h1 style="color:#00d4ff; border:none; padding:0; margin:0;">👤 Об авторе</h1>
                <p style="color:#888; margin-top:4px;">Кто стоит за этим проектом</p>
            </div>
        </div>
        
        {get_menu('/about')}
        
        {get_about_html()}
        
        <div style="margin-top:40px;">
            {get_license_html()}
        </div>
        
        <div class="footer">
            <p>🤖 Автоматизировано с любовью для свободного интернета</p>
            <p style="font-size:12px; color:#444;">
                <a href="{REPO_URL}">📂 Исходный код</a> &bull; 
                <a href="https://gitverse.ru/RUVIPIEN/" target="_blank">📦 Все проекты</a> &bull;
                <a href="/">🏠 На главную</a>
            </p>
        </div>
    </div>
</body>
</html>"""
    return render_template_string(html)


# ==================== ВСТРОЕННЫЙ CONFIG GENERATOR ====================

def get_checker_html():
    """Возвращает полный HTML Config Generator V1.1"""
    return """
    <div style="color:#888; text-align:center; padding:40px; background:#1a1a2e; border-radius:12px;">
        <h2 style="color:#00d4ff;">⚡ Config Generator V1.1</h2>
        <p style="margin:15px 0;">Загрузка Config Generator...</p>
        <p style="font-size:13px; color:#555;">Если вы видите это сообщение, значит файл <code>checker.html</code> не найден.</p>
        <p style="font-size:13px; color:#555;">Создайте его в корне проекта или используйте встроенную версию.</p>
        <button onclick="loadChecker()" class="btn btn-primary" style="margin-top:15px;">🔄 Загрузить чекер</button>
    </div>
    <script>
        function loadChecker() {
            fetch('/static/checker.html')
                .then(r => r.text())
                .then(html => {
                    document.querySelector('.checker-wrapper').innerHTML = html;
                })
                .catch(() => {
                    alert('Не удалось загрузить Config Generator');
                });
        }
        // Автозагрузка
        document.addEventListener('DOMContentLoaded', loadChecker);
    </script>
    """


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)