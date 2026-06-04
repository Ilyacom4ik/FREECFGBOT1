#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import uuid
import random
import threading
import requests
from flask import Flask, request, Response, abort

# ═══════════════════════════════════════════════════════
#                     НАСТРОЙКИ
# ═══════════════════════════════════════════════════════

BOT_TOKEN        = os.environ['TG_BOT_TOKEN']
PLATEGA_MERCHANT = os.environ['PLATEGA_MERCHANT_ID']   # X-MerchantId
PLATEGA_SECRET   = os.environ['PLATEGA_SECRET']        # X-Secret

# Публичный HTTPS-адрес этого сервера (без слэша в конце)
# Пример: https://mybot.example.com
SERVER_URL       = os.environ['SERVER_URL']

# Цена подписки в рублях
PREMIUM_PRICE    = int(os.environ.get('PREMIUM_PRICE', '99'))

API              = f"https://api.telegram.org/bot{BOT_TOKEN}"
PLATEGA_API      = "https://app.platega.io"

SMALL_SUB_URL    = "https://raw.githubusercontent.com/Ilyacom4ik/free-v2ray-2026/refs/heads/main/subscriptions/FreeCFGHub1.txt"
BIG_SUB_URL      = "https://raw.githubusercontent.com/Ilyacom4ik/vpn-keys/refs/heads/main/allkeysFreeCFGHub.txt"
KEYS_SOURCE_URL  = "https://raw.githubusercontent.com/Ilyacom4ik/vpn-keys/refs/heads/main/allkeysFreeCFGHub.txt"

# Премиум-подписка — реальный URL, который будет проксироваться
PREMIUM_SUB_REAL_URL = "https://raw.githubusercontent.com/Ilyacom4ik/vpn-keys/refs/heads/main/allkeysFreeCFGHub.txt"

CHANNEL_URL      = "https://t.me/FreeCFGHub"
DATABASE_FILE    = "database.txt"

LITE_KEYS_COUNT  = 5
FULL_KEYS_COUNT  = 7

# Токены доступа: { token: tg_user_id }
premium_tokens: dict[str, int] = {}

# Ожидающие оплаты: { transaction_id: tg_user_id }
pending_payments: dict[str, int] = {}

# ═══════════════════════════════════════════════════════
#                    DATABASE
# ═══════════════════════════════════════════════════════

def db_add_user(user_id: int):
    """Записать TG ID в database.txt если ещё нет."""
    uid = str(user_id)
    existing = db_load()
    if uid not in existing:
        with open(DATABASE_FILE, "a", encoding="utf-8") as f:
            f.write(uid + "\n")
        print(f"✅ Новый покупатель добавлен в БД: {uid}", flush=True)

def db_load() -> set:
    if not os.path.exists(DATABASE_FILE):
        return set()
    with open(DATABASE_FILE, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}

def db_has_user(user_id: int) -> bool:
    return str(user_id) in db_load()

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
        "5️⃣ Пользуешься ✅"
    )

TEXT_SUB_MENU = (
    "🔶 <b>Выберите тип подписки</b>\n\n"
    "❗️ Внимание: большая подписка может вызвать лаги на слабых устройствах."
)

TEXT_KEYS_MENU = (
    "🔷 <b>Выберите тип ключа</b>\n\n"
    "• <b>Lite 🏳️</b> — при белых списках\n"
    "• <b>Full 🏴</b> — при обычном использовании\n\n"
    "❗️ Не используйте <b>Lite 🏳️</b> на Wi-Fi"
)

TEXT_PREMIUM_INFO = (
    "💎 <b>Премиум подписка</b>\n\n"
    f"Стоимость: <b>{PREMIUM_PRICE} ₽</b>\n\n"
    "Что входит:\n"
    "• Стабильная подписка с большим пулом серверов\n"
    "• Персональная ссылка — вставляешь один раз в клиент\n"
    "• Ссылка работает только в VPN-клиенте (Hiddify, V2rayTun и др.)\n\n"
    "👇 Нажми <b>Оплатить</b> для получения ссылки на оплату."
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
    "4.2. Работоспособность конфигураций не гарантируется — они могут устаревать "
    "или блокироваться третьими лицами.\n\n"

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
    "8.1. Администрация вправе изменять условия Соглашения без уведомления.\n"
    "8.2. Актуальная версия — в закреплённом сообщении канала.\n\n"

    "<b>9. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ</b>\n"
    "9.1. Использование материалов означает полное согласие с настоящим Соглашением.\n"
    "9.2. Если вы не согласны — прекратите использование материалов FreeCFGHub.\n"
    "9.3. Соглашение регулируется законодательством Российской Федерации.\n\n"
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
        {"command": "start",   "description": "🏠 Главное меню"},
        {"command": "sub",     "description": "📁 Получить подписку"},
        {"command": "keys",    "description": "🔑 Получить ключи"},
        {"command": "premium", "description": "💎 Премиум подписка"},
        {"command": "status",  "description": "📡 Статус"},
        {"command": "help",    "description": "ℹ️ Справка"},
    ]
    requests.post(f"{API}/setMyCommands", json={"commands": commands}, timeout=10)
    print("✅ Команды меню установлены", flush=True)

# ═══════════════════════════════════════════════════════
#                  КЛАВИАТУРЫ
# ═══════════════════════════════════════════════════════

def kb_main():
    return {
        "inline_keyboard": [
            [{"text": "📁 Получить подписку", "callback_data": "menu_sub"}],
            [{"text": "🔑 Получить ключи",    "callback_data": "menu_keys"}],
            [{"text": "💎 Премиум подписка",  "callback_data": "menu_premium"}],
            [{"text": "ℹ️ Справка (ВАЖНО❗️)", "callback_data": "menu_help"}],
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
                {"text": "Lite 🏳️", "callback_data": "keys_lite"},
                {"text": "Full 🏴",  "callback_data": "keys_full"},
            ],
            [{"text": "◀️ Назад", "callback_data": "back_main"}],
        ]
    }

def kb_premium(pay_url: str):
    return {
        "inline_keyboard": [
            [{"text": f"💳 Оплатить {PREMIUM_PRICE} ₽", "url": pay_url}],
            [{"text": "◀️ Назад", "callback_data": "back_main"}],
        ]
    }

def kb_back():
    return {
        "inline_keyboard": [
            [{"text": "🏠 В главное меню", "callback_data": "back_main"}]
        ]
    }

# ═══════════════════════════════════════════════════════
#                  PLATEGA ОПЛАТА
# ═══════════════════════════════════════════════════════

def create_payment(user_id: int) -> tuple[str | None, str | None]:
    """Создать платёж, вернуть (redirect_url, transaction_id) или (None, None)."""
    try:
        resp = requests.post(
            f"{PLATEGA_API}/api/transactions",
            headers={
                "X-MerchantId": PLATEGA_MERCHANT,
                "X-Secret":     PLATEGA_SECRET,
                "Content-Type": "application/json",
            },
            json={
                "paymentDetails": {
                    "amount":   PREMIUM_PRICE,
                    "currency": "RUB",
                },
                "description": f"Премиум подписка FreeCFGHub | TG:{user_id}",
                "return":      f"{SERVER_URL}/payment/success",
                "failedUrl":   f"{SERVER_URL}/payment/failed",
                "payload":     str(user_id),
            },
            timeout=15,
        )
        data = resp.json()
        print(f"Platega response: {data}", flush=True)
        tx_id    = data.get("transactionId")
        redirect = data.get("redirect")
        if tx_id and redirect:
            pending_payments[tx_id] = user_id
            return redirect, tx_id
        return None, None
    except Exception as e:
        print(f"Ошибка create_payment: {e}", flush=True)
        return None, None

# ═══════════════════════════════════════════════════════
#               ЗАГРУЗКА И ПАРСИНГ КЛЮЧЕЙ
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
            elif re.search(r'\bFull\b', line, re.IGNORECASE):
                full_keys.append(line)
            else:
                full_keys.append(line)

        print(f"DEBUG: Lite={len(lite_keys)}, Full={len(full_keys)}", flush=True)
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
        f"🏳️ Lite ключей: {len(keys_data.get('lite', []))}\n"
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
    if not chat_id:
        return

    name = msg.get("from", {}).get("first_name") or "друг"

    if text == "/start":
        send_message(chat_id, text_welcome(name), reply_markup=kb_main())

    elif text in ("/sub",):
        send_message(chat_id, TEXT_SUB_MENU, reply_markup=kb_subscriptions())

    elif text == "/keys":
        send_message(chat_id, TEXT_KEYS_MENU, reply_markup=kb_keys())

    elif text in ("/premium",):
        _send_premium(chat_id, msg.get("message_id"))

    elif text == "/status":
        send_message(chat_id, TEXT_STATUS_LOADING)
        send_message(chat_id, get_status_text())

    elif text in ("/help", "/info"):
        send_message(chat_id, TEXT_HELP, reply_markup=kb_back())


def _send_premium(chat_id, message_id=None):
    """Создать платёж и отправить/отредактировать сообщение с кнопкой оплаты."""
    pay_url, tx_id = create_payment(chat_id)
    if not pay_url:
        txt = "❌ Не удалось создать ссылку на оплату. Попробуй позже."
        if message_id:
            edit_message(chat_id, message_id, txt, reply_markup=kb_back())
        else:
            send_message(chat_id, txt, reply_markup=kb_back())
        return

    txt = (
        TEXT_PREMIUM_INFO +
        f"\n\n🆔 ID транзакции: <code>{tx_id}</code>"
    )
    if message_id:
        edit_message(chat_id, message_id, txt, reply_markup=kb_premium(pay_url))
    else:
        send_message(chat_id, txt, reply_markup=kb_premium(pay_url))

# ═══════════════════════════════════════════════════════
#                  ОБРАБОТКА CALLBACK
# ═══════════════════════════════════════════════════════

def handle_callback(cb):
    chat_id    = cb["message"]["chat"]["id"]
    message_id = cb["message"]["message_id"]
    data       = cb.get("data", "")
    from_user  = cb.get("from", {})
    name       = from_user.get("first_name") or "друг"

    answer_callback(cb["id"])

    if data == "back_main":
        edit_message(chat_id, message_id, text_welcome(name), reply_markup=kb_main())

    elif data == "menu_sub":
        edit_message(chat_id, message_id, TEXT_SUB_MENU, reply_markup=kb_subscriptions())

    elif data == "sub_small":
        text = (
            "📦 <b>Небольшая подписка</b>\n\n"
            "Скопируй ссылку ниже и вставь в поле <b>«Подписка»</b> в своём клиенте "
            "(Hiddify, V2rayTun, Nekobox и др.):\n\n"
            f"<code>{SMALL_SUB_URL}</code>\n\n"
            "✅ Ссылка обновляется автоматически — добавь один раз и пользуйся."
        )
        edit_message(chat_id, message_id, text, reply_markup=kb_back())

    elif data == "sub_big":
        text = (
            "🗂 <b>Большая подписка</b>\n\n"
            "Скопируй ссылку ниже и вставь в поле <b>«Подписка»</b> в своём клиенте:\n\n"
            f"<code>{BIG_SUB_URL}</code>\n\n"
            "⚠️ Много серверов — возможны лаги на слабых устройствах.\n"
            "✅ Ссылка обновляется автоматически."
        )
        edit_message(chat_id, message_id, text, reply_markup=kb_back())

    elif data == "menu_keys":
        edit_message(chat_id, message_id, TEXT_KEYS_MENU, reply_markup=kb_keys())

    elif data in ("keys_lite", "keys_full"):
        key_type = "lite" if data == "keys_lite" else "full"
        count    = LITE_KEYS_COUNT if key_type == "lite" else FULL_KEYS_COUNT
        label    = "Lite 🏳️" if key_type == "lite" else "Full 🏴"
        warn     = "\n❗️ Не используй на Wi-Fi!" if key_type == "lite" else ""

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

    elif data == "menu_premium":
        _send_premium(chat_id, message_id)

    elif data == "menu_help":
        edit_message(chat_id, message_id, TEXT_HELP, reply_markup=kb_back())

# ═══════════════════════════════════════════════════════
#           FLASK — WEBHOOK PLATEGA + ПРОКСИ
# ═══════════════════════════════════════════════════════

app = Flask(__name__)

# VPN-клиенты которые будут в User-Agent (проверяем подстроки)
VPN_CLIENT_AGENTS = [
    "hiddify", "v2raytun", "v2rayng", "nekobox", "clash",
    "sing-box", "xray", "v2fly", "shadowrocket", "quantumult",
    "surge", "stash", "loon", "streisand", "v2box",
]

def is_vpn_client(ua: str) -> bool:
    ua_lower = ua.lower()
    return any(agent in ua_lower for agent in VPN_CLIENT_AGENTS)


@app.route("/sub/<token>", methods=["GET"])
def proxy_sub(token: str):
    """
    Прокси-эндпоинт для премиум подписки.
    При открытии в браузере — 403.
    При запросе из VPN-клиента — отдаёт содержимое реального URL.
    """
    ua = request.headers.get("User-Agent", "")

    if not is_vpn_client(ua):
        # Открытие в браузере — ничего не показываем
        abort(403)

    if token not in premium_tokens:
        abort(404)

    try:
        r = requests.get(PREMIUM_SUB_REAL_URL, timeout=15)
        return Response(
            r.content,
            status=200,
            headers={
                "Content-Type": r.headers.get("Content-Type", "text/plain; charset=utf-8"),
                "Content-Disposition": "inline",
            }
        )
    except Exception as e:
        print(f"Ошибка прокси: {e}", flush=True)
        abort(502)


@app.route("/payment/callback", methods=["POST"])
def payment_callback():
    """Platega webhook — вызывается при смене статуса платежа."""
    # Проверяем заголовки авторизации от Platega
    merchant = request.headers.get("X-MerchantId", "")
    secret   = request.headers.get("X-Secret", "")

    if merchant != PLATEGA_MERCHANT or secret != PLATEGA_SECRET:
        print("⚠️ Callback: неверная авторизация", flush=True)
        abort(403)

    data   = request.get_json(silent=True) or {}
    status = data.get("status")
    tx_id  = data.get("id")

    print(f"📩 Platega callback: tx={tx_id} status={status}", flush=True)

    if status == "CONFIRMED" and tx_id:
        user_id = pending_payments.pop(tx_id, None)

        # Также пробуем достать user_id из payload если нет в pending
        if not user_id:
            try:
                user_id = int(data.get("payload", "0"))
            except (ValueError, TypeError):
                user_id = None

        if user_id:
            db_add_user(user_id)
            _deliver_premium(user_id)

    return "", 200


@app.route("/payment/success")
def payment_success():
    return "<h2>✅ Оплата прошла! Вернитесь в Telegram — бот уже выслал вашу подписку.</h2>", 200


@app.route("/payment/failed")
def payment_failed():
    return "<h2>❌ Оплата не прошла. Вернитесь в Telegram и попробуйте ещё раз.</h2>", 200


def _deliver_premium(user_id: int):
    """Выдать покупателю его персональную прокси-ссылку."""
    token = str(uuid.uuid4()).replace("-", "")
    premium_tokens[token] = user_id

    sub_link = f"{SERVER_URL}/sub/{token}"

    send_message(
        user_id,
        "🎉 <b>Оплата подтверждена!</b>\n\n"
        "💎 Твоя персональная ссылка на подписку:\n\n"
        f"<code>{sub_link}</code>\n\n"
        "📋 Скопируй её и вставь в поле <b>«Подписка»</b> в своём клиенте "
        "(Hiddify, V2rayTun, Nekobox и др.).\n\n"
        "⚠️ Ссылка работает <b>только в VPN-клиенте</b>. "
        "При открытии в браузере — страница недоступна.\n\n"
        f"📢 {CHANNEL_URL}",
        reply_markup=kb_back()
    )
    print(f"💎 Премиум выдан: user={user_id} token={token}", flush=True)


def run_flask():
    app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)

# ═══════════════════════════════════════════════════════
#                       MAIN LOOP
# ═══════════════════════════════════════════════════════

def main():
    print("🤖 Бот FreeCFGHub запущен", flush=True)
    set_bot_commands()

    # Запускаем Flask в фоновом потоке
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("🌐 Flask-сервер запущен на порту 8080", flush=True)

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
