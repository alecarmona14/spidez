import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
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
# HELPERS
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
        "👋 <b>Bienvenido</b>\n\n"
        "¿Eres un cliente nuevo o ya eres cliente?",
        reply_markup=kb([
            [InlineKeyboardButton("🆕 Nuevo cliente", callback_data="nuevo_cliente")],
            [InlineKeyboardButton("👤 Ya soy cliente", callback_data="antiguo_cliente")]
        ])
    )

# ---------------------------------------------------
# AUTO RESPUESTA SOLO 1 VEZ
# ---------------------------------------------------

@bot.message_handler(func=lambda m: True)
def auto_respuesta(message):

    user_id = message.chat.id

    # Ignorar grupos
    if message.chat.type != "private":
        return

    # Solo responder una vez
    if user_id in usuarios_atendidos:
        return

    usuarios_atendidos.add(user_id)

    bot.send_message(
        user_id,
        "Hola, soy Spidez 👋\n\n"
        "Puedes hablar con mi asistente aquí 👉 @asispidezbot\n\n"
        "Si ya eres cliente y necesitas ayuda, escribe /start."
    )

# ---------------------------------------------------
# CALLBACKS
# ---------------------------------------------------

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):

    # quitar loading infinito
    bot.answer_callback_query(call.id)

    data = call.data
    chat_id = call.message.chat.id

    user = call.from_user
    user_tag = f"@{user.username}" if user.username else user.first_name

    # ---------------------------------------------------
    # MENÚ PRINCIPAL
    # ---------------------------------------------------

    if data == "start_menu":
        start(call.message)
        return

    # ---------------------------------------------------
    # NUEVO CLIENTE
    # ---------------------------------------------------

    if data == "nuevo_cliente":

        bot.send_message(
            chat_id,
            "👌 <b>Perfecto</b>\n\n"
            "Selecciona una opción:",
            reply_markup=kb([
                [InlineKeyboardButton("ℹ Información y precios", callback_data="info_precios")],
                [InlineKeyboardButton("🛒 Adquirir servicio", callback_data="adquirir")],
                [InlineKeyboardButton("🆘 Ayuda instalación", callback_data="ayuda_instalacion")],
                [InlineKeyboardButton("🎁 Solicitar prueba gratis", callback_data="prueba_gratis")],
                [InlineKeyboardButton("💬 Hablar con Spidez", url="https://t.me/manager_spidez")],
                [InlineKeyboardButton("🔙 Volver atrás", callback_data="start_menu")]
            ])
        )

        return

    # ---------------------------------------------------
    # INFORMACIÓN
    # ---------------------------------------------------

    if data == "info_precios":

        bot.send_message(
            chat_id,
            "📌 <b>INFORMACIÓN DEL SERVICIO</b>\n\n"
            "✅ Servicio estable 24/7\n"
            "✅ Compatible con Smart TV, Fire TV, Android, iPhone, PC y más\n"
            "✅ Deportes, eventos y contenido premium\n"
            "✅ Soporte rápido\n\n"
            "💰 <b>PRECIOS</b>\n\n"
            "📺 1 dispositivo → 45€\n"
            "📺 2 dispositivos → 75€\n"
            "📺 3 dispositivos → 100€\n\n"
            "Para más dispositivos contactar con soporte.",
            reply_markup=kb([
                [InlineKeyboardButton("🔙 Volver atrás", callback_data="nuevo_cliente")]
            ])
        )

        return

    # ---------------------------------------------------
    # ADQUIRIR
    # ---------------------------------------------------

    if data == "adquirir":

        bot.send_message(
            chat_id,
            "🛒 <b>Selecciona el plan:</b>",
            reply_markup=kb([
                [InlineKeyboardButton("1 dispositivo", callback_data="pagar_1")],
                [InlineKeyboardButton("2 dispositivos", callback_data="pagar_2")],
                [InlineKeyboardButton("3 dispositivos", callback_data="pagar_3")],
                [InlineKeyboardButton("Más de 3 dispositivos", callback_data="pagar_mas_3")],
                [InlineKeyboardButton("🔙 Volver atrás", callback_data="nuevo_cliente")]
            ])
        )

        return

    # ---------------------------------------------------
    # PLANES
    # ---------------------------------------------------

    if data.startswith("pagar_"):

        plan = data.replace("pagar_", "")

        update_user(chat_id, {
            "plan": plan
        })

        bot.send_message(
            chat_id,
            "💳 <b>Selecciona método de pago:</b>",
            reply_markup=kb([
                [InlineKeyboardButton("💸 Bizum", callback_data="pago_bizum")],
                [InlineKeyboardButton("💳 PayPal", callback_data="pago_paypal")],
                [InlineKeyboardButton("🪙 Criptomonedas", callback_data="pago_crypto")],
                [InlineKeyboardButton("🔙 Volver atrás", callback_data="adquirir")]
            ])
        )

        return

    # ---------------------------------------------------
    # PAGOS
    # ---------------------------------------------------

    if data.startswith("pago_"):

        metodo = data.replace("pago_", "")

        user_data = get_user(chat_id)
        plan = user_data.get("plan", "No especificado")

        notify_admin(
            "📩 <b>NUEVO PEDIDO</b>\n\n"
            f"👤 Usuario: {user_tag}\n"
            f"📺 Plan: {plan}\n"
            f"💳 Pago: {metodo}"
        )

        bot.send_message(
            chat_id,
            "✅ <b>Solicitud enviada correctamente</b>\n\n"
            f"Método seleccionado: <b>{metodo}</b>\n\n"
            "Spidez te contactará pronto para finalizar el pedido.",
            reply_markup=kb([
                [InlineKeyboardButton("🏠 Menú principal", callback_data="start_menu")]
            ])
        )

        return

    # ---------------------------------------------------
    # AYUDA INSTALACIÓN
    # ---------------------------------------------------

    if data == "ayuda_instalacion":

        notify_admin(
            f"🆘 Solicitud ayuda instalación\n👤 {user_tag}"
        )

        bot.send_message(
            chat_id,
            "🆘 <b>Ayuda con instalación</b>\n\n"
            "Pulsa abajo para hablar directamente con soporte.",
            reply_markup=kb([
                [InlineKeyboardButton("💬 Abrir soporte", url="https://t.me/manager_spidez")],
                [InlineKeyboardButton("🔙 Volver atrás", callback_data="nuevo_cliente")]
            ])
        )

        return

    # ---------------------------------------------------
    # PRUEBA GRATIS
    # ---------------------------------------------------

    if data == "prueba_gratis":

        notify_admin(
            f"🎁 Solicitud de prueba gratis\n👤 {user_tag}"
        )

        bot.send_message(
            chat_id,
            "🎁 <b>Solicitud enviada</b>\n\n"
            "Spidez revisará tu solicitud y te contactará pronto.",
            reply_markup=kb([
                [InlineKeyboardButton("🏠 Menú principal", callback_data="start_menu")]
            ])
        )

        return

    # ---------------------------------------------------
    # CLIENTE ANTIGUO
    # ---------------------------------------------------

    if data == "antiguo_cliente":

        bot.send_message(
            chat_id,
            "👋 <b>Bienvenido de nuevo</b>\n\n"
            "¿Qué necesitas?",
            reply_markup=kb([
                [InlineKeyboardButton("🔄 Renovar servicio", callback_data="renovar")],
                [InlineKeyboardButton("⚠️ Tengo problemas", callback_data="problema_enlace")],
                [InlineKeyboardButton("💬 Hablar con Spidez", url="https://t.me/manager_spidez")],
                [InlineKeyboardButton("🔙 Volver atrás", callback_data="start_menu")]
            ])
        )

        return

    # ---------------------------------------------------
    # RENOVAR
    # ---------------------------------------------------

    if data == "renovar":

        notify_admin(
            f"🔄 Solicitud renovación\n👤 {user_tag}"
        )

        bot.send_message(
            chat_id,
            "🔄 <b>Solicitud enviada</b>\n\n"
            "Spidez te contactará pronto para renovar tu servicio.",
            reply_markup=kb([
                [InlineKeyboardButton("🏠 Menú principal", callback_data="start_menu")]
            ])
        )

        return

    # ---------------------------------------------------
    # PROBLEMAS
    # ---------------------------------------------------

    if data == "problema_enlace":

        notify_admin(
            f"⚠️ Problema reportado\n👤 {user_tag}"
        )

        bot.send_message(
            chat_id,
            "⚠️ <b>Incidencia enviada</b>\n\n"
            "Nuestro soporte revisará tu problema lo antes posible.",
            reply_markup=kb([
                [InlineKeyboardButton("💬 Hablar con soporte", url="https://t.me/manager_spidez")],
                [InlineKeyboardButton("🏠 Menú principal", callback_data="start_menu")]
            ])
        )

        return

# ---------------------------------------------------
# INICIAR BOT
# ---------------------------------------------------

print("BOT INICIADO")

bot.delete_webhook()
bot.infinity_polling(skip_pending=True)