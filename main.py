#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import random
import requests
from datetime import datetime

BOT_TOKEN = os.environ['TG_BOT_TOKEN']
API = f"https://api.telegram.org/bot{BOT_TOKEN}"

SMALL_SUB_URL   = "https://raw.githubusercontent.com/Ilyacom4ik/free-v2ray-2026/refs/heads/main/subscriptions/FreeCFGHub1.txt"
BIG_SUB_URL     = "https://raw.githubusercontent.com/Ilyacom4ik/vpn-keys/refs/heads/main/allkeysFreeCFGHub.txt"
KEYS_SOURCE_URL = "https://raw.githubusercontent.com/Ilyacom4ik/vpn-keys/refs/heads/main/allkeysFreeCFGHub.txt"

PROXY_RU_URL  = "https://raw.githubusercontent.com/Ilyacom4ik/TGPROXY/refs/heads/main/proxy_ru.txt"
PROXY_EU_URL  = "https://raw.githubusercontent.com/Ilyacom4ik/TGPROXY/refs/heads/main/proxy_eu.txt"
PROXY_ALL_URL = "https://raw.githubusercontent.com/Ilyacom4ik/TGPROXY/refs/heads/main/proxy_all.txt"

SUPPORT_URL  = "https://pay.cloudtips.ru/p/2486fa1a"
CHANNEL_URL  = "https://t.me/FreeCFGHub"

LTE_KEYS_COUNT  = 5
FULL_KEYS_COUNT = 7

STATS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stats.json')

# ═══════════════════════════════════════════════════════
#                     СТАТИСТИКА
# ═══════════════════════════════════════════════════════

def load_stats():
    try:
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            "keys_lte": 0,
            "keys_full": 0,
            "sub_small": 0,
            "sub_big": 0,
            "support_clicks": 0,
            "unique_users": []
        }

def save_stats(stats):
    try:
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка сохранения stats: {e}", flush=True)

def increment_stat(key, user_id=None):
    stats = load_stats()
    if key in stats:
        stats[key] += 1
    if user_id and user_id not in stats["unique_users"]:
        stats["unique_users"].append(user_id)
    save_stats(stats)

def get_stats_text():
    stats = load_stats()
    return (
        f"📊 <b>Статистика FreeCFGHub бота</b>\n\n"
        f"🔑 LTE ключей выдано: <b>{stats.get('keys_lte', 0)}</b> раз\n"
        f"🔑 Full ключей выдано: <b>{stats.get('keys_full', 0)}</b> раз\n"
        f"📦 Небольших подписок: <b>{stats.get('sub_small', 0)}</b> раз\n"
        f"🗂 Больших подписок: <b>{stats.get('sub_big', 0)}</b> раз\n"
        f"💳 Нажали поддержать: <b>{stats.get('support_clicks', 0)}</b> раз\n\n"
        f"👥 Уникальных пользователей: <b>{len(stats.get('unique_users', []))}</b>\n\n"
        f"📢 {CHANNEL_URL}"
    )

# ═══════════════════════════════════════════════════════
#                     ЛОГГЕР
# ═══════════════════════════════════════════════════════

def get_user_info(user):
    user_id    = user.get('id', '?')
    first_name = user.get('first_name', '')
    last_name  = user.get('last_name', '')
    username   = user.get('username', '')
    name       = f"{first_name} {last_name}".strip()
    if name and username:
        full_info = f"{name} (@{username})"
    elif name:
        full_info = name
    elif username:
        full_info = f"@{username}"
    else:
        full_info = f"user_{user_id}"
    return f"{full_info} [{user_id}]"

def log_action(user, action, details=""):
    timestamp  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_info  = get_user_info(user)
    log_entry  = f"[{timestamp}] 👤 {user_info} ➜ {action}"
    if details:
        log_entry += f" | {details}"
    print(log_entry, flush=True)

# ═══════════════════════════════════════════════════════
#                     ТЕКСТЫ
# ═══════════════════════════════════════════════════════

def text_welcome(name):
    return (
        f"Привет, {name} 👋\n\n"
        "🆓 Тут ты получишь ключи и подписки для разных клиентов таких как:\n"
        "<b>Hiddify, V2rayTun (NG, BOX), Nekobox, Happ и др.</b>\n\n"
        "📁 <b>Как получить?</b>\n"
        "1️⃣ Выбираешь подписку либо ключи\n"
        "2️⃣ Получаешь то или другое\n"
        "3️⃣ Копируешь выданное\n"
        "4️⃣ Вставляешь в любой клиент\n"
        "5️⃣ Пользуешься ✅\n\n"
        "❤️ Пожалуйста, поддержите канал — это мотивирует создателя "
        "выпускать обновления чаще и делать всё качественно."
    )

TEXT_SUB_MENU = (
    "🔶 <b>Выберите тип подписки</b>\n\n"
    "❗️ Внимание: большая подписка может вызвать лаги на слабых устройствах."
)

TEXT_KEYS_MENU = (
    "🔷 <b>Выберите тип ключа</b>\n\n"
    "• <b>LTE 🏳️</b> — при белых списках\n"
    "• <b>Full 🏴</b> — при обычном использовании\n\n"
    "❗️ Не используйте <b>LTE 🏳️</b> на Wi-Fi"
)

TEXT_HELP = (
    "📜 <b>ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ FreeCFGHub</b>\n\n"
    "<b>1. ОПРЕДЕЛЕНИЯ</b>\n"
    "1.1. Проект FreeCFGHub — некоммерческий канал, предоставляющий информацию "
    "о технологиях оптимизации сетевого трафика и ускорении доступа к цифровым сервисам.\n"
    "1.2. «Конфигурации» — наборы технических параметров, улучшающих качество соединения. "
    "Проект не является VPN-сервисом или прокси в юридическом смысле.\n"
    "1.3. Все материалы предоставляются в ознакомительных и образовательных целях.\n\n"
    "<b>2. ЦЕЛИ ПРОЕКТА</b>\n"
    "2.1. Помочь пользователям улучшить стабильность и скорость интернет-соединения.\n"
    "2.2. Проект не пропагандирует нарушение законодательства РФ и других стран.\n"
    "2.3. FreeCFGHub не является рекламой средств обхода блокировок.\n\n"
    "<b>3. ОТВЕТСТВЕННОСТЬ ПОЛЬЗОВАТЕЛЯ</b>\n"
    "3.1. Пользователь самостоятельно несёт ответственность за использование информации "
    "в соответствии с законами своего региона.\n"
    "3.2. Администрация не несёт ответственности за последствия использования конфигураций.\n"
    "3.3. Пользователь обязуется использовать конфигурации только для легальных целей.\n\n"
    "<b>4. ОТСУТСТВИЕ ГАРАНТИЙ</b>\n"
    "4.1. Все материалы предоставляются «как есть» (AS IS) без каких-либо гарантий.\n"
    "4.2. Работоспособность конфигураций не гарантируется.\n\n"
    "<b>5. АВТОРСКИЕ ПРАВА</b>\n"
    "5.1. Материалы Проекта являются собственностью администрации FreeCFGHub.\n"
    "5.2. Запрещено копирование, распространение или коммерческое использование "
    "без письменного согласия.\n\n"
    "<b>6. КОНФИДЕНЦИАЛЬНОСТЬ</b>\n"
    "6.1. Проект не собирает и не хранит персональные данные пользователей.\n"
    "6.2. Применяется политика конфиденциальности Telegram.\n\n"
    "<b>7. ЗАПРЕТ НА НЕЗАКОННЫЕ ДЕЙСТВИЯ</b>\n"
    "Запрещено использовать конфигурации для:\n"
    "• Распространения экстремистских материалов\n"
    "• Мошеннических действий\n"
    "• Организации DDoS-атак\n"
    "• Любой иной деятельности, запрещённой законодательством РФ\n\n"
    "<b>8. ИЗМЕНЕНИЕ УСЛОВИЙ</b>\n"
    "8.1. Администрация вправе изменять условия Соглашения без уведомления.\n\n"
    "<b>9. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ</b>\n"
    "9.1. Использование материалов означает полное согласие с настоящим Соглашением.\n"
    f"📢 Канал: {CHANNEL_URL}"
)

TEXT_STATUS_LOADING = "⏳ Проверяю..."

# ═══════════════════════════════════════════════════════
#                  TELEGRAM API HELPERS
# ═══════════════════════════════════════════════════════

def get_updates(offset=None):
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    try:
        r = requests.get(f"{API}/getUpdates", params=params, timeout=35)
        return r.json().get("result", [])
    except Exception as e:
        print(f"Ошибка get_updates: {e}", flush=True)
        return []

def send_message(chat_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        data["reply_markup"] = reply_markup
    try:
        requests.post(f"{API}/sendMessage", json=data, timeout=10)
    except Exception as e:
        print(f"Ошибка send_message: {e}", flush=True)

def edit_message(chat_id, message_id, text, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        data["reply_markup"] = reply_markup
    try:
        requests.post(f"{API}/editMessageText", json=data, timeout=10)
    except Exception as e:
        print(f"Ошибка edit_message: {e}", flush=True)

def answer_callback(callback_id, text=""):
    try:
        requests.post(f"{API}/answerCallbackQuery", json={
            "callback_query_id": callback_id,
            "text": text
        }, timeout=10)
    except Exception as e:
        print(f"Ошибка answer_callback: {e}", flush=True)

def set_bot_commands():
    commands = [
        {"command": "start",  "description": "🏠 Главное меню"},
        {"command": "sub",    "description": "📁 Получить подписку"},
        {"command": "keys",   "description": "🔑 Получить ключи"},
        {"command": "status", "description": "📡 Статус"},
        {"command": "proxy",  "description": "🌍 Прокси для Telegram"},
        {"command": "stats",  "description": "📊 Статистика"},
        {"command": "help",   "description": "ℹ️ Справка"},
    ]
    requests.post(f"{API}/setMyCommands", json={"commands": commands}, timeout=10)
    print("✅ Команды меню установлены", flush=True)

# ═══════════════════════════════════════════════════════
#                  КЛАВИАТУРЫ
# ═══════════════════════════════════════════════════════

def kb_main():
    return {
        "inline_keyboard": [
            [{"text": "📁 Получить подписку",    "callback_data": "menu_sub"}],
            [{"text": "🔑 Получить ключи",       "callback_data": "menu_keys"}],
            [{"text": "🌍 Прокси для Telegram",  "callback_data": "menu_proxy"}],
            [{"text": "💳 Поддержать канал",     "url": SUPPORT_URL}],
            [{"text": "ℹ️ Справка (ВАЖНО❗️)",   "callback_data": "menu_help"}],
        ]
    }

def kb_subscriptions():
    return {
        "inline_keyboard": [
            [{"text": "📦 Небольшая подписка (для слабых устройств)", "callback_data": "sub_small"}],
            [{"text": "🗂 Большая подписка (много ключей)",           "callback_data": "sub_big"}],
            [{"text": "◀️ Назад", "callback_data": "back_main"}],
        ]
    }

def kb_keys():
    return {
        "inline_keyboard": [
            [
                {"text": "LTE 🏳️", "callback_data": "keys_lte"},
                {"text": "Full 🏴", "callback_data": "keys_full"},
            ],
            [{"text": "◀️ Назад", "callback_data": "back_main"}],
        ]
    }

def kb_proxy_countries():
    return {
        "inline_keyboard": [
            [{"text": "🇷🇺 Россия",    "callback_data": "proxy_ru"}],
            [{"text": "🇪🇺 Европа",    "callback_data": "proxy_eu"}],
            [{"text": "🌍 Все (RU+EU)", "callback_data": "proxy_all"}],
            [{"text": "◀️ Назад",       "callback_data": "back_main"}],
        ]
    }

def kb_back():
    return {
        "inline_keyboard": [
            [{"text": "🏠 В главное меню", "callback_data": "back_main"}]
        ]
    }

# ═══════════════════════════════════════════════════════
#               ЗАГРУЗКА И ПАРСИНГ КЛЮЧЕЙ
# ═══════════════════════════════════════════════════════

def fetch_proxies_from_url(url):
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            proxies = []
            for line in r.text.splitlines():
                line = line.strip()
                if line.startswith("tg://proxy?"):
                    proxies.append(line)
            return proxies
        return []
    except Exception as e:
        print(f"Ошибка загрузки прокси: {e}", flush=True)
        return []

def fetch_and_parse_keys():
    try:
        r = requests.get(KEYS_SOURCE_URL, timeout=15)
        if r.status_code != 200:
            return None, f"Ошибка загрузки: {r.status_code}"
        lte_keys  = []
        full_keys = []
        for line in r.text.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if not re.match(r'^(vless|vmess|trojan|ss|tuic|hysteria2)://', line):
                continue
            if re.search(r'\bLTE\b', line, re.IGNORECASE):
                lte_keys.append(line)
            else:
                full_keys.append(line)
        print(f"DEBUG: LTE={len(lte_keys)}, Full={len(full_keys)}", flush=True)
        return {"lte": lte_keys, "full": full_keys}, None
    except Exception as e:
        return None, str(e)

def get_random_keys(keys_list, count):
    if not keys_list:
        return []
    return random.sample(keys_list, min(count, len(keys_list)))

def get_status_text():
    keys_data, error = fetch_and_parse_keys()
    if error:
        return f"❌ Ошибка: {error}"
    return (
        f"📊 <b>Статус подписки</b>\n\n"
        f"🏳️ LTE ключей: {len(keys_data.get('lte', []))}\n"
        f"🏴 Full ключей: {len(keys_data.get('full', []))}\n\n"
        f"🔄 Обновляется автоматически\n\n"
        f"📢 {CHANNEL_URL}"
    )

# ═══════════════════════════════════════════════════════
#                  ОБРАБОТКА СООБЩЕНИЙ
# ═══════════════════════════════════════════════════════

def handle_message(msg):
    chat_id = msg.get("chat", {}).get("id")
    text    = msg.get("text", "")
    user    = msg.get("from", {})
    if not chat_id:
        return

    user_id = user.get("id")
    name    = user.get("first_name") or "друг"

    if text == "/start":
        log_action(user, "🚀 ЗАПУСТИЛ БОТА")
        increment_stat("unique_users_track", user_id)
        send_message(chat_id, text_welcome(name), reply_markup=kb_main())

    elif text == "/sub":
        log_action(user, "📁 ОТКРЫЛ МЕНЮ ПОДПИСОК")
        send_message(chat_id, TEXT_SUB_MENU, reply_markup=kb_subscriptions())

    elif text == "/keys":
        log_action(user, "🔑 ОТКРЫЛ МЕНЮ КЛЮЧЕЙ")
        send_message(chat_id, TEXT_KEYS_MENU, reply_markup=kb_keys())

    elif text == "/status":
        log_action(user, "📡 ЗАПРОСИЛ СТАТУС")
        send_message(chat_id, TEXT_STATUS_LOADING)
        send_message(chat_id, get_status_text())

    elif text == "/proxy":
        log_action(user, "🌍 ОТКРЫЛ МЕНЮ ПРОКСИ")
        send_message(chat_id, "🌍 Выберите страну прокси:", reply_markup=kb_proxy_countries())

    elif text == "/stats":
        log_action(user, "📊 ЗАПРОСИЛ СТАТИСТИКУ")
        send_message(chat_id, get_stats_text())

    elif text in ("/help", "/info"):
        log_action(user, "ℹ️ ОТКРЫЛ СПРАВКУ")
        send_message(chat_id, TEXT_HELP, reply_markup=kb_back())

# ═══════════════════════════════════════════════════════
#                  ОБРАБОТКА CALLBACK
# ═══════════════════════════════════════════════════════

def handle_callback(cb):
    chat_id    = cb["message"]["chat"]["id"]
    message_id = cb["message"]["message_id"]
    data       = cb.get("data", "")
    user       = cb.get("from", {})
    user_id    = user.get("id")
    name       = user.get("first_name") or "друг"

    answer_callback(cb["id"])

    if data == "back_main":
        log_action(user, "🏠 ВЕРНУЛСЯ В ГЛАВНОЕ МЕНЮ")
        edit_message(chat_id, message_id, text_welcome(name), reply_markup=kb_main())

    elif data == "menu_sub":
        log_action(user, "📁 ОТКРЫЛ МЕНЮ ПОДПИСОК")
        edit_message(chat_id, message_id, TEXT_SUB_MENU, reply_markup=kb_subscriptions())

    elif data == "sub_small":
        log_action(user, "📦 ВЫБРАЛ НЕБОЛЬШУЮ ПОДПИСКУ")
        increment_stat("sub_small", user_id)
        text = (
            "📦 <b>Небольшая подписка</b>\n\n"
            "Скопируй ссылку ниже и вставь в поле <b>«Подписка»</b> в своём клиенте:\n\n"
            f"<code>{SMALL_SUB_URL}</code>\n\n"
            "✅ Ссылка обновляется автоматически."
        )
        edit_message(chat_id, message_id, text, reply_markup=kb_back())

    elif data == "sub_big":
        log_action(user, "🗂 ВЫБРАЛ БОЛЬШУЮ ПОДПИСКУ")
        increment_stat("sub_big", user_id)
        text = (
            "🗂 <b>Большая подписка</b>\n\n"
            "Скопируй ссылку ниже и вставь в поле <b>«Подписка»</b> в своём клиенте:\n\n"
            f"<code>{BIG_SUB_URL}</code>\n\n"
            "⚠️ Много серверов — возможны лаги на слабых устройствах.\n"
            "✅ Ссылка обновляется автоматически."
        )
        edit_message(chat_id, message_id, text, reply_markup=kb_back())

    elif data == "menu_keys":
        log_action(user, "🔑 ОТКРЫЛ МЕНЮ КЛЮЧЕЙ")
        edit_message(chat_id, message_id, TEXT_KEYS_MENU, reply_markup=kb_keys())

    elif data in ("keys_lte", "keys_full"):
        key_type = "lte" if data == "keys_lte" else "full"
        count    = LTE_KEYS_COUNT if key_type == "lte" else FULL_KEYS_COUNT
        label    = "LTE 🏳️" if key_type == "lte" else "Full 🏴"
        warn     = "\n❗️ Не используй на Wi-Fi!" if key_type == "lte" else ""
        stat_key = "keys_lte" if key_type == "lte" else "keys_full"

        log_action(user, f"🔑 ЗАПРОСИЛ КЛЮЧИ {label}")
        increment_stat(stat_key, user_id)

        edit_message(chat_id, message_id, f"⏳ Загружаю {label} ключи...")

        keys_data, error = fetch_and_parse_keys()
        if error:
            edit_message(chat_id, message_id,
                         f"❌ Не удалось загрузить ключи: {error}", reply_markup=kb_back())
            return

        keys_list = keys_data.get(key_type, [])
        if not keys_list:
            edit_message(chat_id, message_id,
                         "😔 Ключи временно недоступны. Загляни позже!", reply_markup=kb_back())
            return

        selected   = get_random_keys(keys_list, count)
        keys_block = "\n\n".join(f"<code>{k}</code>" for k in selected)

        edit_message(
            chat_id, message_id,
            f"🔑 <b>{label} — {len(selected)} шт.</b>{warn}\n\n"
            f"{keys_block}\n\n"
            f"📋 Нажми на ключ чтобы скопировать, вставь в клиент.\n"
            f"📢 {CHANNEL_URL}",
            reply_markup=kb_back()
        )

    elif data.startswith("proxy_"):
        country = data.split("_")[1]
        if country == "ru":
            url   = PROXY_RU_URL
            label = "🇷🇺 Россия"
        elif country == "eu":
            url   = PROXY_EU_URL
            label = "🇪🇺 Европа"
        else:
            url   = PROXY_ALL_URL
            label = "🌍 Все страны"

        log_action(user, f"🌍 ЗАПРОСИЛ ПРОКСИ {label}")
        edit_message(chat_id, message_id, f"⏳ Загружаю прокси ({label})...")

        proxies = fetch_proxies_from_url(url)
        if not proxies:
            edit_message(chat_id, message_id,
                         f"❌ Прокси для {label} временно недоступны\n\nПопробуй позже.",
                         reply_markup=kb_proxy_countries())
            return

        proxies  = proxies[:5]
        keyboard = []
        for i, proxy in enumerate(proxies, 1):
            keyboard.append([{"text": f"🔵 Подключиться #{i}", "url": proxy}])
        keyboard.append([{"text": "◀️ Назад", "callback_data": "menu_proxy"}])

        edit_message(
            chat_id, message_id,
            f"🌍 <b>MTProto прокси для Telegram</b>\n\n"
            f"📍 <b>Регион:</b> {label}\n"
            f"📦 <b>Доступно прокси:</b> {len(proxies)}\n\n"
            f"📌 Нажми на кнопку, чтобы подключиться\n\n"
            f"📢 {CHANNEL_URL}",
            reply_markup={"inline_keyboard": keyboard}
        )

    elif data == "menu_proxy":
        log_action(user, "🌍 ОТКРЫЛ МЕНЮ ПРОКСИ")
        edit_message(chat_id, message_id, "🌍 Выберите страну прокси:", reply_markup=kb_proxy_countries())

    elif data == "menu_help":
        log_action(user, "ℹ️ ОТКРЫЛ СПРАВКУ")
        edit_message(chat_id, message_id, TEXT_HELP, reply_markup=kb_back())

# ═══════════════════════════════════════════════════════
#                       MAIN LOOP
# ═══════════════════════════════════════════════════════

def main():
    print("🤖 Бот FreeCFGHub запущен", flush=True)
    print("=" * 60, flush=True)
    set_bot_commands()

    offset = None
    while True:
        updates = get_updates(offset)
        for update in updates:
            offset = update["update_id"] + 1
            try:
                if "message" in update:
                    handle_message(update["message"])
                elif "callback_query" in update:
                    handle_callback(update["callback_query"])
            except Exception as e:
                print(f"Ошибка обработки update: {e}", flush=True)

if __name__ == "__main__":
    main()  
