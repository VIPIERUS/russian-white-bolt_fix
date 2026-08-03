#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор красивой HTML-страницы из README.md
Использует Markdown -> HTML с кастомными стилями
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

# Пути
README_PATH = Path("README.md")
INDEX_PATH = Path("index.html")
VPNMIRRORS_PATH = Path("VPNMIRRORS")

# Стили для красивой страницы
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
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 14px;
        border-radius: 8px;
        overflow: hidden;
    }
    th {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        color: #00d4ff;
        padding: 14px 12px;
        text-align: left;
        font-weight: 600;
        border-bottom: 2px solid #00d4ff;
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
    }
    .badge {
        display: inline-block;
        background: #1a1a2e;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        border: 1px solid #333;
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
    summary {
        cursor: pointer;
        color: #00d4ff;
        font-weight: bold;
        font-size: 16px;
    }
    summary:hover { color: #44ff88; }
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
    @media (max-width: 768px) {
        .container { padding: 15px; }
        table { font-size: 12px; }
        td, th { padding: 8px 6px; }
        .stats-grid { grid-template-columns: repeat(2, 1fr); }
        h1 { font-size: 1.8em; }
    }
    /* Анимация загрузки */
    .glow-text { 
        color: #00d4ff; 
        text-shadow: 0 0 20px rgba(0,212,255,0.3);
    }
</style>
"""

def parse_markdown_to_html(content: str) -> str:
    """Простой парсер Markdown -> HTML (без внешних библиотек)"""
    lines = content.split('\n')
    html_lines = []
    in_code_block = False
    in_list = False
    in_table = False
    table_rows = []
    
    for line in lines:
        line = line.rstrip()
        
        # Кодовые блоки
        if line.startswith('```'):
            in_code_block = not in_code_block
            if in_code_block:
                html_lines.append('<pre><code>')
            else:
                html_lines.append('</code></pre>')
            continue
        
        if in_code_block:
            html_lines.append(line)
            continue
        
        # Пустые строки
        if not line.strip():
            html_lines.append('')
            continue
        
        # Заголовки
        if line.startswith('# '):
            html_lines.append(f'<h1>{line[2:]}</h1>')
        elif line.startswith('## '):
            html_lines.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('### '):
            html_lines.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('#### '):
            html_lines.append(f'<h4>{line[5:]}</h4>')
        
        # Таблицы
        elif '|' in line and '---' not in line:
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if not in_table:
                in_table = True
                table_rows = [cells]
                html_lines.append('<table><thead><tr>')
                html_lines.append(''.join(f'<th>{c}</th>' for c in cells))
                html_lines.append('</tr></thead><tbody>')
            else:
                html_lines.append('<tr>')
                html_lines.append(''.join(f'<td>{c}</td>' for c in cells))
                html_lines.append('</tr>')
        
        elif line.startswith('|---'):
            continue
        
        else:
            if in_table:
                in_table = False
                html_lines.append('</tbody></table>')
                continue
            
            # Списки
            if line.startswith('- ') or line.startswith('* '):
                html_lines.append(f'<li>{line[2:]}</li>')
                continue
            
            # Обычный текст
            line = line.replace('`', '<code>').replace('`', '</code>', 1)  # упрощённо
            html_lines.append(f'<p>{line}</p>')
    
    if in_table:
        html_lines.append('</tbody></table>')
    
    return '\n'.join(html_lines)

def generate_html():
    """Генерирует index.html из README.md"""
    print("📝 Генерация index.html...")
    
    # Читаем README
    if not README_PATH.exists():
        print("⚠️ README.md не найден!")
        return False
    
    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Собираем статистику
    stats = {
        'files': 0,
        'configs': 0,
        'sources': 0
    }
    
    # Парсим метаданные
    metadata_path = VPNMIRRORS_PATH / "metadata.json"
    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
            stats['sources'] = meta.get('stats', {}).get('success', 0)
            stats['configs'] = meta.get('stats', {}).get('total_keys', 0)
    
    # Считаем файлы
    if VPNMIRRORS_PATH.exists():
        for _ in VPNMIRRORS_PATH.rglob('*.txt'):
            stats['files'] += 1
    
    # Создаём HTML-страницу
    html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VPN White-Lists | Обновляемые конфиги</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🔒</text></svg>">
    {CSS_STYLES}
</head>
<body>
    <div class="container">
        <!-- Шапка с логотипом и статистикой -->
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:20px;">
            <div>
                <h1 style="border:none; padding:0; margin:0;">🔒 VPN White-Lists</h1>
                <p style="color:#888; margin-top:4px;">Автоматически обновляемые белые списки для обхода блокировок</p>
            </div>
            <div style="text-align:right;">
                <span class="badge">🔄 Обновлено: {datetime.now().strftime('%H:%M MSK')}</span>
            </div>
        </div>
        
        <!-- Статистика -->
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-number">{stats['files']}</div><div class="stat-label">📁 Файлов</div></div>
            <div class="stat-card"><div class="stat-number">{stats['configs']}</div><div class="stat-label">🔗 Конфигураций</div></div>
            <div class="stat-card"><div class="stat-number">{stats['sources']}</div><div class="stat-label">✅ Рабочих источников</div></div>
            <div class="stat-card"><div class="stat-number">{datetime.now().strftime('%d.%m.%Y')}</div><div class="stat-label">📅 Последнее обновление</div></div>
        </div>
        
        <!-- Содержимое README -->
        {parse_markdown_to_html(content)}
        
        <!-- Футер -->
        <div class="footer">
            <p>🤖 Автоматизировано с любовью для свободного интернета</p>
            <p style="font-size:12px; color:#444;">
                <a href="https://gitverse.ru/RUVIPIEN/russian-white-bolt_fix">Исходный код</a> &bull; 
                Обновляется каждые 3 часа &bull; 
                <a href="#top">⬆ Наверх</a>
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    # Сохраняем
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ index.html создан! Размер: {len(html_content)} символов")
    return True

if __name__ == "__main__":
    generate_html()