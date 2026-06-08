#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
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
        {"command": "premium", "description": "💎 Премиум подписка"},
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
        "💎 <b>Премиум подписка</b> — стабильные конфигурации с приоритетной поддержкой.\n\n"
        "📁 Команды:\n"
        "/premium — выбор тарифа\n"
        "/info — документы и контакты\n"
        "/help — пользовательское соглашение"
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

# ═══════════════════════════════════════════════════════
#                     КЛАВИАТУРЫ
# ═══════════════════════════════════════════════════════

def kb_main():
    return {
        "inline_keyboard": [
            [{"text": "💎 Премиум подписка", "callback_data": "menu_premium"}],
            [{"text": "ℹ️ Информация", "callback_data": "menu_info"}],
            [{"text": "📜 Справка", "callback_data": "menu_help"}],
        ]
    }

def kb_tariffs():
    buttons = []
    for key, tariff in TARIFFS.items():
        buttons.append([{"text": f"💎 {tariff['name']} — {tariff['price']} ₽", "callback_data": f"tariff_{key}"}])
    buttons.append([{"text": "◀️ Назад", "callback_data": "back_main"}])
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
    elif text == "/premium":
        send_message(chat_id, TEXT_PREMIUM_MENU, reply_markup=kb_tariffs())
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
    elif data == "menu_premium":
        edit_message(chat_id, message_id, TEXT_PREMIUM_MENU, reply_markup=kb_tariffs())
    elif data == "menu_info":
        edit_message(chat_id, message_id, TEXT_INFO, reply_markup=kb_back())
    elif data == "menu_help":
        edit_message(chat_id, message_id, TEXT_HELP, reply_markup=kb_back())
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
    elif data == "back_premium":
        edit_message(chat_id, message_id, TEXT_PREMIUM_MENU, reply_markup=kb_tariffs())

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
