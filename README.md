# 🌐 VPN White-Lists для России

<div align="center">

![Auto Update](https://img.shields.io/badge/Auto%20Update-Every%203%20Hours-brightgreen?style=for-the-badge)
![Configs](https://img.shields.io/badge/Configs-0-blue?style=for-the-badge)
![Sources](https://img.shields.io/badge/Sources-0%2F0-orange?style=for-the-badge)

</div>

## 📊 Информация

| Параметр | Значение |
|----------|----------|
| 🕐 **Последнее обновление** | `2026-08-31 16:14 MSK` |
| 📁 **Всего файлов** | `0` |
| 🔗 **Всего конфигураций** | `0` |
| ✅ **Рабочих источников** | `0` |
| ❌ **Недоступных источников** | `0` |

---

## 📱 VPN Приложения

> Выберите приложение для вашей платформы и импортируйте конфигурации из таблиц ниже
> **Нажмите на иконку 👁️ чтобы увидеть скриншот приложения**

| Приложение | Платформы | Описание | Сайт | Скачать |
|------------|-----------|----------|------|---------|
| 📦 **Nekoray / Nekobox** [👁️](https://gitverse.ru/api/repos/RUVIPIEN/russian-white-bolt/raw/branch/master/foto/Nekoray.png) | 💻 Windows 📱 Android | Продвинутый клиент с поддержкой VLESS, VMess, Reality, White Lists и CIDR | [🌐 Сайт](https://nekobox.one) | <br>[💻 Windows](https://cloud.mail.ru/public/4S6V/b7MpS2Mq2) |
| 🚀 **V2RayNG / V2RayN** [👁️](https://gitverse.ru/api/repos/RUVIPIEN/russian-white-bolt/raw/branch/master/foto/V2RayNG.png) | 📱 Android 💻 Windows 🍎 iOS | Популярный клиент для VLESS, VMess, Trojan, Shadowsocks | [🌐 Сайт](https://getv2rayng.com) | <br>[💻 Windows](https://cloud.mail.ru/public/sgNP/F46KfPDQb) • [📱 Android](https://cloud.mail.ru/public/Qt13/dcrEunZXz) • [🍎 macOS](https://cloud.mail.ru/public/FHHR/3cEDNRdBQ) |
| 🔒 **Happ VPN** [👁️](https://gitverse.ru/api/repos/RUVIPIEN/russian-white-bolt/raw/branch/master/foto/Happ.png) | 📱 Android 🍎 iOS | Простой VPN с поддержкой VLESS, Trojan и TOR Bridges | [🌐 Сайт](https://happ.su) | <br>[📱 Android](https://cloud.mail.ru/public/oNx1/p9ABSSc35) |
| 📱 **Sing-box** [👁️](https://gitverse.ru/api/repos/RUVIPIEN/russian-white-bolt/raw/branch/master/foto/Sing-box.png) | 📱 Android 🍎 iOS 💻 Windows 🖥️ macOS 🐧 Linux | Универсальная платформа проксирования | [🌐 Сайт](https://sing-box.sagernet.org) | <br>[💻 Windows](https://cloud.mail.ru/public/mN76/xdt4SSKd3) • [📱 Android](https://cloud.mail.ru/public/8iNb/TVsDyCQHt) |
| ⚔️ **Clash / ClashMeta** [👁️](https://gitverse.ru/api/repos/RUVIPIEN/russian-white-bolt/raw/branch/master/foto/Clash.png) | 💻 Windows 🖥️ macOS 🐧 Linux 📱 Android | Rule-based tunnel с продвинутой маршрутизацией | [🌐 Сайт](https://github.com/MetaCubeX/Clash.Meta) | <br>[💻 Windows](https://cloud.mail.ru/public/LyPS/KhTPz3N9S) • [📱 Android](https://cloud.mail.ru/public/VRSa/PQwpQ5QY4) • [🍎 macOS](https://cloud.mail.ru/public/rLZc/X6jDeNXiw) |

---

## 🚀 Быстрый старт

1. **Выберите приложение** из таблицы выше и установите его
2. **Нажмите на 👁️ иконку** чтобы посмотреть скриншот приложения
3. **Нажмите на кнопку скачивания** (Windows/Android/macOS) чтобы загрузить файл
4. **Найдите нужный конфиг** в разделах ниже
5. **Нажмите на ссылку "⬇️ Скачать"**
6. **Импортируйте** ссылку или файл в ваше VPN приложение

> 💡 **Совет:** Конфигурации обновляются автоматически каждые 3 часа!

---

## 📂 Конфигурации по категориям

---

## 📋 Все файлы (быстрый доступ)

<details>
<summary>🔽 Нажмите чтобы развернуть список всех файлов</summary>

```
---

## 🚫 Как обходить CIDR и SNI блокировки

### 📍 CIDR-блокировка (по IP-адресам)

**Как блокируют:**  
Роскомнадзор добавляет целые диапазоны IP-адресов в реестр блокировок. Трафик на эти IP обрывается провайдером.

**Как обходим:**  
В конфигах используются **white CIDR**-списки — разрешённые («чистые») диапазоны IP. VPN направляет трафик только через эти белые подсети, обходя заблокированные адреса.

---

### 🔠 SNI-блокировка (по имени сервера)

**Как блокируют:**  
Провайдер видит **SNI** (Server Name Indication) — имя сайта в открытом виде при подключении (например, `youtube.com`). Если имя в чёрном списке — соединение разрывается.

**Как обходим:**  
Используются **white SNI**-списки и технологии **Reality / uTLS**. Они маскируют настоящее имя сайта или подменяют его на «чистое», чтобы провайдер не мог определить цель.

> 💡 **Простыми словами:**  
> - **CIDR** — блокировка по «адресу дома»  
> - **SNI** — блокировка по «названию на табличке»  
> - **White-списки** позволяют обходить обе блокировки, направляя трафик через разрешённые IP и домены.

---

## 🔄 Автоматическое обновление

Этот репозиторий автоматически обновляется каждые **3 часа** через GitVerse CI/CD.

### 📅 Расписание обновлений:
- `00:00 MSK` - Ночное обновление
- `03:00 MSK` - Раннее утро
- `06:00 MSK` - Утро
- `09:00 MSK` - Позднее утро
- `12:00 MSK` - День
- `15:00 MSK` - После обеда
- `18:00 MSK` - Вечер
- `21:00 MSK` - Поздний вечер

---

## 📝 Как добавить источник

1. Отредактируйте файл `sources/urls.txt`
2. Добавьте строку в формате: `URL|CATEGORY|NAME`
3. Доступные категории: `nekobox`, `v2ray`, `happ`, `singbox`, `clash`, `tor`
4. Создайте Pull Request или запушьте изменения

**Пример:**
```
https://example.com/config.txt|v2ray|My Config
```

---

<div align="center">

**🤖 Автоматизировано с любовью для свободного интернета**

*Последнее обновление: 2026-08-31 16:14:05 MSK*

</div>