import os
import sys
import requests
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
)

# Ensure the root directory is on the path so we can import shared
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from shared.constants import EKMAN_EMOTIONS, get_emotion_display_name

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables from the root directory
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

# Conversation states
EMOTION, LEVEL = range(2)

# Backend API URL
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/log")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and shows emotion buttons."""
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)

    keyboard = []
    for emotion_key in EKMAN_EMOTIONS:
        display_name = get_emotion_display_name(emotion_key)
        keyboard.append([InlineKeyboardButton(display_name, callback_data=emotion_key)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "¡Hola! ¿Cómo te sientes ahora mismo? Elige una opción:",
        reply_markup=reply_markup
    )
    return EMOTION

async def emotion_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected emotion and asks for a level."""
    query = update.callback_query
    await query.answer()

    emotion_key = query.data
    context.user_data["emotion"] = emotion_key

    display_name = get_emotion_display_name(emotion_key)
    logger.info("Emotion selected: %s", emotion_key)

    keyboard = [
        [
            InlineKeyboardButton("1", callback_data="1"),
            InlineKeyboardButton("2", callback_data="2"),
            InlineKeyboardButton("3", callback_data="3"),
            InlineKeyboardButton("4", callback_data="4"),
            InlineKeyboardButton("5", callback_data="5"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"Has seleccionado {display_name}.\n¿Qué nivel de intensidad sientes? (1-5)",
        reply_markup=reply_markup,
    )
    return LEVEL

async def level_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the level and sends the data to the API."""
    query = update.callback_query
    await query.answer()

    level = int(query.data)
    emotion = context.user_data["emotion"]
    user_name = query.from_user.first_name

    logger.info("Level selected for %s: %s", emotion, level)

    try:
        response = requests.post(API_URL, json={"emotion": emotion, "level": level})
        if response.status_code == 200:
            logger.info("Emotion successfully registered")
            await query.edit_message_text("¡Emoción registrada con éxito!")
        else:
            logger.error("Error from API: %s", response.text)
            await query.edit_message_text("Hubo un error al registrar tu emoción en el servidor.")
    except requests.exceptions.RequestException as e:
        logger.error("Connection error with backend: %s", e)
        await query.edit_message_text("No se pudo conectar con el servidor backend.")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text("Registro de emoción cancelado.")
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    # Get the token from an environment variable
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.error("TELEGRAM_TOKEN environment variable not set.")
        return

    application = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("registrar", start),
            CommandHandler("emocion", start),
        ],
        states={
            EMOTION: [CallbackQueryHandler(emotion_selected)],
            LEVEL: [CallbackQueryHandler(level_selected)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    
    logger.info("¡El bot de Telegram está funcionando! Esperando mensajes...")
    application.run_polling()

if __name__ == "__main__":
    main()
