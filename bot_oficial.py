import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import json
import os
import re

# ---------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------

TOKEN = "8630544894:AAF10utQEeGONlKNIEg6EKxOxL46rlIWxxA"
ADMIN_ID = 275900930

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

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
# FUNCIONES BASE
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
    update_user(chat_id, {"esperando_usuario": False})
    bot.send_message(
        chat_id,
        "👋 <b>Bienvenido</b>\n\n¿Eres un cliente nuevo o ya eres cliente?",
        reply_markup=kb([
            [InlineKeyboardButton("🆕 Nuevo cliente", callback_data="nuevo_cliente")],
            [InlineKeyboardButton("👤 Ya soy cliente", callback_data="antiguo_cliente")],
            [InlineKeyboardButton("🔄 Empezar de nuevo", callback_data="start_menu")]
        ])
    )

# ---------------------------------------------------
# CALLBACKS
# ---------------------------------------------------

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    data = call.data
    chat_id = call.message.chat.id
    user = call.from_user
    user_tag = f"@{user.username}" if user.username else user.first_name

    # -----------------------------------------------
    # VOLVER AL MENÚ PRINCIPAL
    # -----------------------------------------------
    if data == "start_menu":
        update_user(chat_id, {"esperando_usuario": False})
        start(call.message)
        return

    # -----------------------------------------------
    # NUEVO CLIENTE
    # -----------------------------------------------
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
                [InlineKeyboardButton("🔄 Empezar de nuevo", callback_data="start_menu")]
            ])
        )
        return

    # -----------------------------------------------
    # YA SOY CLIENTE
    # -----------------------------------------------
    if data == "antiguo_cliente":
        bot.send_message(
            chat_id,
            "Bienvenido de nuevo 👋\n¿Qué necesitas?",
            reply_markup=kb([
                [InlineKeyboardButton("🔄 Renovar", callback_data="renovar")],
                [InlineKeyboardButton("⚠️ Tengo problemas con mi enlace", callback_data="problema_enlace")],
                [InlineKeyboardButton("💬 Hablar con Spidez", url="https://t.me/manager_spidez")],
                [InlineKeyboardButton("🔄 Empezar de nuevo", callback_data="start_menu")]
            ])
        )
        return

    # -----------------------------------------------
    # INFORMACIÓN + PRECIOS
    # -----------------------------------------------
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
                [InlineKeyboardButton("🔄 Empezar de nuevo", callback_data="start_menu")]
            ])
        )
        return

    # -----------------------------------------------
    # ADQUIRIR SERVICIO
    # -----------------------------------------------
    if data == "adquirir":
        bot.send_message(
            chat_id,
            "🛒 <b>Elige cuántos dispositivos quieres adquirir:</b>",
            reply_markup=kb([
                [InlineKeyboardButton("1 dispositivo", callback_data="pagar_1")],
                [InlineKeyboardButton("2 dispositivos", callback_data="pagar_2")],
                [InlineKeyboardButton("3 dispositivos", callback_data="pagar_3")],
                [InlineKeyboardButton("Más de 3", callback_data="pagar_mas_3")],
                [InlineKeyboardButton("🔄 Empezar de nuevo", callback_data="start_menu")]
            ])
        )
        return

    # -----------------------------------------------
    # AYUDA INSTALACIÓN
    # -----------------------------------------------
    if data == "ayuda_instalacion":
        update_user(chat_id, {"pidio_ayuda": True})
        notify_admin(f"🆘 Solicitan ayuda con la instalación\n👤 {user_tag}\n🆔 {chat_id}")
        bot.send_message(
            chat_id,
            "🆘 <b>Ayuda con la instalación</b>\n\nHabla con un asistente:",
            reply_markup=kb([
                [InlineKeyboardButton("👤 Hablar con Spidez", url="https://t.me/manager_spidez")],
                [InlineKeyboardButton("🔄 Empezar de nuevo", callback_data="start_menu")]
            ])
        )
        return

    # -----------------------------------------------
    # PRUEBA GRATIS
    # -----------------------------------------------
    if data == "prueba_gratis":
        update_user(chat_id, {"prueba_gratis": True})
        notify_admin(f"🎁 Solicitan prueba gratis\n👤 {user_tag}\n🆔 {chat_id}")
        bot.send_message(
            chat_id,
            "🎁 <b>Prueba gratis solicitada</b>\n\nUn asistente te contactará en breve.",
            reply_markup=kb([
                [InlineKeyboardButton("🔄 Empezar de nuevo", callback_data="start_menu")]
            ])
        )
        return

    # -----------------------------------------------
    # RENOVAR
    # -----------------------------------------------
    if data == "renovar":
        bot.send_message(
            chat_id,
            "🔄 <b>Renovaciones</b>\n\nElige cuántos dispositivos quieres renovar:",
            reply_markup=kb([
                [InlineKeyboardButton("1 dispositivo", callback_data="pagar_1")],
                [InlineKeyboardButton("2 dispositivos", callback_data="pagar_2")],
                [InlineKeyboardButton("3 dispositivos", callback_data="pagar_3")],
                [InlineKeyboardButton("🔄 Empezar de nuevo", callback_data="start_menu")]
            ])
        )
        return

    # -----------------------------------------------
    # PROBLEMA CON ENLACE
    # -----------------------------------------------
    if data == "problema_enlace":
        update_user(chat_id, {"esperando_usuario": True})
        bot.send_message(
            chat_id,
            "Escribe tu usuario para verificarlo.\n\n"
            "ℹ <b>Ayuda:</b>\n"
            "Tu usuario está en el enlace del chat con @manager_spidez.\n"
            "Es lo que aparece después de <b>username=</b> y antes de <b>&</b>.",
            reply_markup=kb([
                [InlineKeyboardButton("❓ No sé cuál es mi usuario", callback_data="no_se_usuario")],
                [InlineKeyboardButton("🔄 Empezar de nuevo", callback_data="start_menu")]
            ])
        )
        return

    # -----------------------------------------------
    # NO SÉ MI USUARIO
    # -----------------------------------------------
    if data == "no_se_usuario":
        bot.send_message(
            chat_id,
            "Aquí tienes un ejemplo real:\n\n"
            "🔗 <code>http://dominio.<b>cambio</b>.xyz:80/xmltv.php?username=<b>usuario123</b>&password=Jk92LmQ8R</code>\n\n"
            "📌 <b>Explicación:</b>\n"
            "• <b>Dominio:</b> desde el inicio hasta <b>:80</b>\n"
            "• <b>Usuario:</b> lo que aparece después de <b>username=</b> y antes de <b>&</b>\n"
            "• <b>Contraseña:</b> lo que aparece después de <b>password=</b>\n\n"
            "Para ver tu usuario real, revisa tu conversación con Spidez.",
            reply_markup=kb([
                [InlineKeyboardButton("🔄 Empezar de nuevo", callback_data="start_menu")]
            ])
        )
        return

    # -----------------------------------------------
    # MÁS DE 3 DISPOSITIVOS
    # -----------------------------------------------
    if data == "pagar_mas_3":
        notify_admin(
            f"📩 Cliente quiere pagar MÁS DE 3 dispositivos\n"
            f"👤 {user_tag}\n🆔 {chat_id}"
        )
        bot.send_message(
            chat_id,
            "Para más de 3 dispositivos, debes hablar con un asistente:",
            reply_markup=kb([
                [InlineKeyboardButton("👤 Hablar con Spidez", url="https://t.me/manager_spidez")],
                [InlineKeyboardButton("🔄 Empezar de nuevo", callback_data="start_menu")]
            ])
        )
        return

    # -----------------------------------------------
    # SELECCIÓN DE DISPOSITIVOS
    # -----------------------------------------------
    if data in ["pagar_1", "pagar_2", "pagar_3"]:
        dispositivos = data.split("_")[1]

        update_user(chat_id, {"dispositivos": dispositivos})

        bot.send_message(
            chat_id,
            f"Has elegido <b>{dispositivos} dispositivo(s)</b>.\n\n"
            "Selecciona tu método de pago:",
            reply_markup=kb([
                [InlineKeyboardButton("💳 Bizum", callback_data="pago_bizum")],
                [InlineKeyboardButton("🪙 Crypto", callback_data="pago_crypto")],
                [InlineKeyboardButton("🎟 Paysafecard", callback_data="pago_paysafecard")],
                [InlineKeyboardButton("💸 PayPal", callback_data="pago_paypal")],
                [InlineKeyboardButton("🔄 Empezar de nuevo", callback_data="start_menu")]
            ])
        )
        return

    # -----------------------------------------------
    # MÉTODOS DE PAGO
    # -----------------------------------------------
    if data.startswith("pago_"):
        metodo = data.replace("pago_", "")
        user_data = get_user(chat_id)
        dispositivos = user_data.get("dispositivos", "No guardado")

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")

        update_user(chat_id, {
            "metodo_pago": metodo,
            "fecha_compra": fecha_actual
        })

        notify_admin(
            f"📩 Nuevo pago recibido\n"
            f"👤 {user_tag}\n"
            f"🆔 {chat_id}\n"
            f"📱 Dispositivos: {dispositivos}\n"
            f"💳 Método: {metodo.capitalize()}\n"
            f"📅 Fecha: {fecha_actual}"
        )

        bot.send_message(
            chat_id,
            f"Perfecto, un asistente te contactará para completar el pago por <b>{metodo.capitalize()}</b>.",
            reply_markup=kb([
                [InlineKeyboardButton("🔄 Empezar de nuevo", callback_data="start_menu")]
            ])
        )
        return

# ---------------------------------------------------
# HANDLER DE MENSAJES (VERIFICACIÓN DE USUARIO)
# ---------------------------------------------------

@bot.message_handler(func=lambda m: True)
def verificar_usuario(message):
    chat_id = message.chat.id
    texto = message.text.strip()

    user_data = get_user(chat_id)

    # -------------------------------------------
    # VERIFICAR USUARIO (NO VUELVE A /START)
    # -------------------------------------------
    if user_data.get("esperando_usuario"):

        usuario = texto.strip()

        # Verificar patrón alec + números
        if not re.fullmatch(r"alec\d+", usuario):

            bot.send_message(
                chat_id,
                "❌ <b>Ese usuario no es válido.</b>",
                reply_markup=kb([
                    [InlineKeyboardButton("❓ No sé cuál es mi usuario", callback_data="no_se_usuario")],
                    [InlineKeyboardButton("🔄 Empezar de nuevo", callback_data="start_menu")]
                ])
            )

            notify_admin(
                f"⚠️ Usuario INCORRECTO enviado por cliente\n"
                f"👤 @{message.from_user.username}\n"
                f"🆔 {chat_id}\n"
                f"❗ Usuario escrito: {usuario}"
            )

            # SEGUIR ESPERANDO USUARIO
            update_user(chat_id, {"esperando_usuario": True})
            return

        # Usuario válido → cerrar modo
        update_user(chat_id, {"esperando_usuario": False})

        bot.send_message(
            chat_id,
            f"✅ Tu usuario <b>{usuario}</b> está verificado.\n\n"
            "Aquí tienes un ejemplo para comparar tu enlace:\n\n"
            "🔗 <code>http://dominio.<b>cambio</b>.xyz:80/xmltv.php?username=<b>usuario123</b>&password=Jk92LmQ8R</code>\n\n"
            "📌 <b>IMPORTANTE</b>\n"
            "Debes cambiar el dominio de tu enlace y usar SIEMPRE <b>okfkte</b>.\n"
            "Solo cambia el dominio, deja tu usuario y contraseña tal como los tienes.",
            reply_markup=kb([
                [InlineKeyboardButton("🔄 Empezar de nuevo", callback_data="start_menu")]
            ])
        )
        return

    # -------------------------------------------
    # SI NO ESTÁ EN NINGÚN MODO
    # -------------------------------------------
    bot.reply_to(message, "Pulsa /start para comenzar.")

# ---------------------------------------------------
# RUN
# ---------------------------------------------------

print("Bot oficial ejecutándose...")
bot.infinity_polling()
