#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import random
import requests

# ═══════════════════════════════════════════════════════
#                     НАСТРОЙКИ
# ═══════════════════════════════════════════════════════

BOT_TOKEN = os.environ['TG_BOT_TOKEN']
API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Тарифы
TARIFFS = {
    "1_month": {"name": "1 месяц", "price": 120, "description": "✅ Доступ к премиум‑серверам\n✅ Высокая стабильность\n✅ Приоритетная поддержка\n✅ Обновления 2 раза в день"},
    "3_months": {"name": "3 месяца", "price": 320, "description": "✅ Доступ к премиум‑серверам\n✅ Высокая стабильность\n✅ Приоритетная поддержка\n✅ Обновления 2 раза в день\n✅ Экономия 40₽"},
    "6_months": {"name": "6 месяцев", "price": 650, "description": "✅ Доступ к премиум‑серверам\n✅ Высокая стабильность\n✅ Приоритетная поддержка\n✅ Обновления 2 раза в день\n✅ Экономия 70₽"},
    "1_year": {"name": "1 год", "price": 999, "description": "✅ Доступ к премиум‑серверам\n✅ Высокая стабильность\n✅ Приоритетная поддержка\n✅ Обновления 2 раза в день\n✅ Максимальная экономия"},
}

# Ссылки на документы
PRIVACY_URL = "https://telegra.ph/Politika-konfidencialnosti-FreeCFGHub-06-03"
TERMS_URL = "https://telegra.ph/Polzovatelskoe-soglashenie-FreeCFGHub-06-03"
CHANNEL_URL = "https://t.me/FreeCFGHub"

# Подписки и ключи
SMALL_SUB_URL = "https://raw.githubusercontent.com/Ilyacom4ik/free-v2ray-2026/refs/heads/main/subscriptions/FreeCFGHub1.txt"
BIG_SUB_URL = "https://raw.githubusercontent.com/Ilyacom4ik/vpn-keys/refs/heads/main/allkeysFreeCFGHub.txt"
KEYS_SOURCE_URL = "https://raw.githubusercontent.com/Ilyacom4ik/vpn-keys/refs/heads/main/allkeysFreeCFGHub.txt"

LITE_KEYS_COUNT = 5
FULL_KEYS_COUNT = 7

# ═══════════════════════════════════════════════════════
#                     ФУНКЦИИ
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
        {"command": "start", "description": "🏠 Главное меню"},
        {"command": "sub", "description": "📁 Получить подписку"},
        {"command": "keys", "description": "🔑 Получить ключи"},
        {"command": "premium", "description": "💎 Премиум подписка"},
        {"command": "status", "description": "📡 Статус"},
        {"command": "info", "description": "ℹ️ Информация"},
        {"command": "help", "description": "📜 Справка"},
    ]
    requests.post(f"{API}/setMyCommands", json={"commands": commands}, timeout=10)
    print("✅ Команды меню установлены", flush=True)

# ═══════════════════════════════════════════════════════
#                       ТЕКСТЫ
# ═══════════════════════════════════════════════════════

def text_welcome(name):
    return (
        f"Привет, {name} 👋\n\n"
        "🆓 Здесь ты получишь конфигурации для разных клиентов.\n\n"
        "📁 <b>Как получить?</b>\n"
        "1️⃣ Выбираешь подписку либо ключи\n"
        "2️⃣ Получаешь то или другое\n"
        "3️⃣ Копируешь выданное\n"
        "4️⃣ Вставляешь в любой клиент\n"
        "5️⃣ Пользуешься ✅"
    )

TEXT_SUB_MENU = (
    "🔶 <b>Выберите тип подписки</b>\n\n"
    "❗️ Внимание: большая подписка может вызвать лаги на слабых устройствах."
)

TEXT_KEYS_MENU = (
    "🔷 <b>Выберите тип ключа</b>\n\n"
    "• <b>Lite</b>\n"
    "• <b>Full</b>\n\n"
)

TEXT_PREMIUM_MENU = (
    "💎 <b>Премиум подписка</b>\n\n"
    "Выберите срок:"
)

TEXT_INFO = (
    "ℹ️ <b>Информация о проекте FreeCFGHub</b>\n\n"
    "📜 <b>Документы:</b>\n"
    f"• <a href='{PRIVACY_URL}'>Политика конфиденциальности</a>\n"
    f"• <a href='{TERMS_URL}'>Пользовательское соглашение</a>\n\n"
    "📞 <b>Поддержка:</b>\n"
    "• Telegram: @ilyacom4ik\n"
    "• Email: freecfghub@gmail.com\n\n"
    f"📢 {CHANNEL_URL}"
)

TEXT_HELP = (
    "📜 <b>ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ FreeCFGHub</b>\n\n"
    "<b>1. ОПРЕДЕЛЕНИЯ</b>\n"
    "1.1. Проект FreeCFGHub — канал, предоставляющий информацию "
    "о технологиях оптимизации сетевого трафика.\n"
    "1.2. «Конфигурации» — наборы технических параметров для настройки приложений.\n"
    "1.3. Все материалы предоставляются в ознакомительных и образовательных целях.\n\n"
    "<b>2. ЦЕЛИ ПРОЕКТА</b>\n"
    "2.1. Помочь пользователям улучшить стабильность и скорость интернет-соединения.\n"
    "2.2. Проект не пропагандирует нарушение законодательства РФ и других стран.\n\n"
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
    f"📢 Канал: {CHANNEL_URL}"
)

TEXT_STATUS_LOADING = "⏳ Проверяю..."

# ═══════════════════════════════════════════════════════
#                 ЗАГРУЗКА КЛЮЧЕЙ
# ═══════════════════════════════════════════════════════

def fetch_and_parse_keys():
    try:
        r = requests.get(KEYS_SOURCE_URL, timeout=15)
        if r.status_code != 200:
            return None, f"Ошибка загрузки: {r.status_code}"
        lite_keys = []
        full_keys = []
        for line in r.text.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if not re.match(r'^(vless|vmess|trojan|ss|tuic|hysteria2)://', line):
                continue
            if re.search(r'\bLite\b', line, re.IGNORECASE):
                lite_keys.append(line)
            else:
                full_keys.append(line)
        return {"lite": lite_keys, "full": full_keys}, None
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
        f"Lite: {len(keys_data.get('lite', []))}\n"
        f"Full: {len(keys_data.get('full', []))}\n\n"
        f"🔄 Обновляется автоматически\n\n"
        f"📢 {CHANNEL_URL}"
    )

# ═══════════════════════════════════════════════════════
#                     КЛАВИАТУРЫ
# ═══════════════════════════════════════════════════════

def kb_main():
    return {
        "inline_keyboard": [
            [{"text": "📁 Получить подписку", "callback_data": "menu_sub"}],
            [{"text": "🔑 Получить ключи", "callback_data": "menu_keys"}],
            [{"text": "💎 Премиум подписка", "callback_data": "menu_premium"}],
            [{"text": "ℹ️ Информация", "callback_data": "menu_info"}],
            [{"text": "📜 Справка", "callback_data": "menu_help"}],
        ]
    }

def kb_subscriptions():
    return {
        "inline_keyboard": [
            [{"text": "📦 Небольшая подписка", "callback_data": "sub_small"}],
            [{"text": "🗂 Большая подписка", "callback_data": "sub_big"}],
            [{"text": "◀️ Назад", "callback_data": "back_main"}],
        ]
    }

def kb_keys():
    return {
        "inline_keyboard": [
            [{"text": "Lite", "callback_data": "keys_lite"}, {"text": "Full", "callback_data": "keys_full"}],
            [{"text": "◀️ Назад", "callback_data": "back_main"}],
        ]
    }

def kb_tariffs():
    buttons = []
    for key, tariff in TARIFFS.items():
        buttons.append([{"text": f"💎 {tariff['name']} — {tariff['price']} ₽", "callback_data": f"tariff_{key}"}])
    buttons.append([{"text": "◀️ Назад", "callback_data": "back_premium"}])
    return {"inline_keyboard": buttons}

def kb_back():
    return {"inline_keyboard": [[{"text": "🏠 В главное меню", "callback_data": "back_main"}]]}

def kb_back_to_premium():
    return {"inline_keyboard": [[{"text": "◀️ Назад к тарифам", "callback_data": "back_premium"}]]}

# ═══════════════════════════════════════════════════════
#                    ОБРАБОТКА
# ═══════════════════════════════════════════════════════

def handle_message(msg):
    chat_id = msg.get("chat", {}).get("id")
    text = msg.get("text", "")
    name = msg.get("from", {}).get("first_name") or "друг"

    if not chat_id:
        return

    if text == "/start":
        send_message(chat_id, text_welcome(name), reply_markup=kb_main())
    elif text == "/sub":
        send_message(chat_id, TEXT_SUB_MENU, reply_markup=kb_subscriptions())
    elif text == "/keys":
        send_message(chat_id, TEXT_KEYS_MENU, reply_markup=kb_keys())
    elif text == "/premium":
        send_message(chat_id, TEXT_PREMIUM_MENU, reply_markup=kb_tariffs())
    elif text == "/status":
        send_message(chat_id, TEXT_STATUS_LOADING)
        send_message(chat_id, get_status_text())
    elif text == "/info":
        send_message(chat_id, TEXT_INFO, reply_markup=kb_back())
    elif text == "/help":
        send_message(chat_id, TEXT_HELP, reply_markup=kb_back())

def handle_callback(cb):
    chat_id = cb["message"]["chat"]["id"]
    message_id = cb["message"]["message_id"]
    data = cb.get("data", "")
    name = cb.get("from", {}).get("first_name") or "друг"

    answer_callback(cb["id"])

    if data == "back_main":
        edit_message(chat_id, message_id, text_welcome(name), reply_markup=kb_main())
    elif data == "back_premium":
        edit_message(chat_id, message_id, TEXT_PREMIUM_MENU, reply_markup=kb_tariffs())
    elif data == "menu_sub":
        edit_message(chat_id, message_id, TEXT_SUB_MENU, reply_markup=kb_subscriptions())
    elif data == "sub_small":
        edit_message(chat_id, message_id,
            f"📦 <b>Небольшая подписка</b>\n\n<code>{SMALL_SUB_URL}</code>",
            reply_markup=kb_back())
    elif data == "sub_big":
        edit_message(chat_id, message_id,
            f"🗂 <b>Большая подписка</b>\n\n<code>{BIG_SUB_URL}</code>",
            reply_markup=kb_back())
    elif data == "menu_keys":
        edit_message(chat_id, message_id, TEXT_KEYS_MENU, reply_markup=kb_keys())
    elif data in ("keys_lite", "keys_full"):
        key_type = "lite" if data == "keys_lite" else "full"
        count = LITE_KEYS_COUNT if key_type == "lite" else FULL_KEYS_COUNT
        label = "Lite" if key_type == "lite" else "Full"
        edit_message(chat_id, message_id, f"⏳ Загружаю...")
        keys_data, error = fetch_and_parse_keys()
        if error:
            edit_message(chat_id, message_id, f"❌ {error}", reply_markup=kb_back())
            return
        keys = keys_data.get(key_type, [])
        if not keys:
            edit_message(chat_id, message_id, "😔 Ключи временно недоступны", reply_markup=kb_back())
            return
        selected = get_random_keys(keys, count)
        keys_block = "\n\n".join(f"<code>{k}</code>" for k in selected)
        edit_message(chat_id, message_id,
            f"🔑 <b>{label} — {len(selected)} шт.</b>\n\n{keys_block}\n\n📢 {CHANNEL_URL}",
            reply_markup=kb_back())
    elif data == "menu_premium":
        edit_message(chat_id, message_id, TEXT_PREMIUM_MENU, reply_markup=kb_tariffs())
    elif data.startswith("tariff_"):
        tariff_key = data.split("_", 1)[1]
        tariff = TARIFFS.get(tariff_key)
        if tariff:
            edit_message(chat_id, message_id,
                f"💎 <b>Премиум подписка: {tariff['name']}</b>\n\n"
                f"💰 Стоимость: {tariff['price']} ₽\n\n"
                f"📋 <b>Что входит:</b>\n{tariff['description']}\n\n"
                "📞 Для покупки: @ilyacom4ik\n\n"
                "После оплаты вы получите персональную ссылку",
                reply_markup=kb_back_to_premium())
        else:
            edit_message(chat_id, message_id, "❌ Ошибка: тариф не найден", reply_markup=kb_back())
    elif data == "menu_info":
        edit_message(chat_id, message_id, TEXT_INFO, reply_markup=kb_back())
    elif data == "menu_help":
        edit_message(chat_id, message_id, TEXT_HELP, reply_markup=kb_back())

# ═══════════════════════════════════════════════════════
#                        MAIN
# ═══════════════════════════════════════════════════════

def main():
    print("🤖 Бот FreeCFGHub запущен", flush=True)
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
                print(f"Ошибка: {e}", flush=True)

if __name__ == "__main__":
    main()
