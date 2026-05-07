import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import json
import os

# ---------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 275900930

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ---------------------------------------------------
# MEMORIA USUARIOS
# ---------------------------------------------------

usuarios_atendidos = set()

# ---------------------------------------------------
# BASE DE DATOS JSON
# ---------------------------------------------------

DB_FILE = "usuarios.json"

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({}, f)

def load_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

def update_user(user_id, data):
    db = load_db()
    if str(user_id) not in db:
        db[str(user_id)] = {}
    db[str(user_id)].update(data)
    save_db(db)

def get_user(user_id):
    db = load_db()
    return db.get(str(user_id), {})

# ---------------------------------------------------
# KEYBOARD
# ---------------------------------------------------

def kb(buttons):
    markup = InlineKeyboardMarkup()
    for row in buttons:
        markup.row(*row)
    return markup

def notify_admin(text):
    try:
        bot.send_message(ADMIN_ID, text)
    except:
        pass

# ---------------------------------------------------
# /START
# ---------------------------------------------------

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    bot.send_message(
        chat_id,
        "👋 <b>Bienvenido</b>\n\n¿Eres un cliente nuevo o ya eres cliente?",
        reply_markup=kb([
            [InlineKeyboardButton("🆕 Nuevo cliente", callback_data="nuevo_cliente")],
            [InlineKeyboardButton("👤 Ya soy cliente", callback_data="antiguo_cliente")]
        ])
    )

# ---------------------------------------------------
# RESPUESTA AUTOMÁTICA (ANTES DE START / SOLO 1 VEZ)
# ---------------------------------------------------

@bot.message_handler(func=lambda m: True)
def auto_respuesta(message):
    user_id = message.chat.id

    # si ya fue atendido, no hacer nada
    if user_id in usuarios_atendidos:
        return

    usuarios_atendidos.add(user_id)

    bot.send_message(
        user_id,
        "Hola, soy Spidez.\n\n"
        "Puedes hablar con mi asistente aquí 👉 @asispidezbot\n\n"
        "Si ya eres cliente, escribe /start."
    )

# ---------------------------------------------------
# CALLBACKS (TU BOT ORIGINAL)
# ---------------------------------------------------

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    data = call.data
    chat_id = call.message.chat.id
    user = call.from_user
    user_tag = f"@{user.username}" if user.username else user.first_name

    if data == "start_menu":
        start(call.message)
        return

    if data == "nuevo_cliente":
        bot.send_message(
            chat_id,
            "Perfecto 👌\n\nElige una opción:",
            reply_markup=kb([
                [InlineKeyboardButton("ℹ Información y Precios", callback_data="info_precios")],
                [InlineKeyboardButton("🛒 Adquirir servicio", callback_data="adquirir")],
                [InlineKeyboardButton("🆘 Ayuda con la instalación", callback_data="ayuda_instalacion")],
                [InlineKeyboardButton("🎁 Quiero prueba gratis", callback_data="prueba_gratis")],
                [InlineKeyboardButton("💬 Hablar con Spidez", url="https://t.me/manager_spidez")],
                [InlineKeyboardButton("🔙 Volver atrás", callback_data="start_menu")]
            ])
        )
        return

    if data == "antiguo_cliente":
        bot.send_message(
            chat_id,
            "Bienvenido de nuevo 👋\n¿Qué necesitas?",
            reply_markup=kb([
                [InlineKeyboardButton("🔄 Renovar", callback_data="renovar")],
                [InlineKeyboardButton("⚠️ Tengo problemas con mi enlace", callback_data="problema_enlace")],
                [InlineKeyboardButton("💬 Hablar con Spidez", url="https://t.me/manager_spidez")],
                [InlineKeyboardButton("🔙 Volver atrás", callback_data="start_menu")]
            ])
        )
        return

    if data == "info_precios":
        bot.send_message(
            chat_id,
            "📌 <b>Información del servicio</b>\n\n"
            "• Servicio estable 24/7\n"
            "• Compatible con todos los dispositivos\n"
            "• Soporte rápido\n\n"
            "💰 <b>Precios</b>\n"
            "1 dispositivo → 45€\n"
            "2 dispositivos → 75€\n"
            "3 dispositivos → 100€\n"
            "Más de 3 → Hablar con @manager_spidez",
            reply_markup=kb([
                [InlineKeyboardButton("🔙 Volver atrás", callback_data="nuevo_cliente")]
            ])
        )
        return

    if data == "adquirir":
        bot.send_message(
            chat_id,
            "🛒 <b>Elige dispositivos:</b>",
            reply_markup=kb([
                [InlineKeyboardButton("1 dispositivo", callback_data="pagar_1")],
                [InlineKeyboardButton("2 dispositivos", callback_data="pagar_2")],
                [InlineKeyboardButton("3 dispositivos", callback_data="pagar_3")],
                [InlineKeyboardButton("Más de 3", callback_data="pagar_mas_3")],
                [InlineKeyboardButton("🔙 Volver atrás", callback_data="nuevo_cliente")]
            ])
        )
        return

    if data.startswith("pago_"):
        metodo = data.replace("pago_", "")

        notify_admin(
            f"📩 Nuevo pago\n👤 {user_tag}\n💳 {metodo}"
        )

        bot.send_message(
            chat_id,
            f"Perfecto 👍 te contactaremos por <b>{metodo}</b>.",
            reply_markup=kb([
                [InlineKeyboardButton("🔙 Volver atrás", callback_data="adquirir")]
            ])
        )
        return

# ---------------------------------------------------
# START BOT
# ---------------------------------------------------

bot.delete_webhook()
bot.infinity_polling()