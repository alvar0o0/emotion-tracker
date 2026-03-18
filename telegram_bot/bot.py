import os
import requests
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables from the root directory
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Emotion mapping
EMOJI_TO_EMOTION = {
    "😊": "alegria",
    "😢": "tristeza",
    "😠": "enojo",
    "😲": "sorpresa",
    "😨": "miedo",
}

# Conversation states
EMOTION, LEVEL = range(2)

# Backend API URL
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/log")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks for an emoji."""
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    await update.message.reply_text(
        "Hola! Envíame un emoji para registrar tu emoción."
    )
    return EMOTION

async def emotion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected emoji and asks for a level."""
    user = update.message.from_user
    user_emoji = update.message.text
    if user_emoji not in EMOJI_TO_EMOTION:
        logger.warning("User %s sent an invalid emoji: %s", user.first_name, user_emoji)
        await update.message.reply_text("Por favor, envíame un emoji válido.")
        return EMOTION

    context.user_data["emotion"] = EMOJI_TO_EMOTION[user_emoji]
    logger.info("Emotion selected by %s: %s", user.first_name, context.user_data["emotion"])
    reply_keyboard = [["1", "2", "3", "4", "5"]]

    await update.message.reply_text(
        f"Qué nivel de {context.user_data['emotion']} sientes? (1-5)",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Nivel?"
        ),
    )
    return LEVEL

async def level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the level and sends the data to the API."""
    user = update.message.from_user
    level = update.message.text
    emotion = context.user_data["emotion"]

    logger.info("Level selected by %s for %s: %s", user.first_name, emotion, level)

    try:
        response = requests.post(API_URL, json={"emotion": emotion, "level": int(level)})
        if response.status_code == 200:
            logger.info("Emotion successfully registered for user %s", user.first_name)
            await update.message.reply_text(
                "Emoción registrada!", reply_markup=ReplyKeyboardRemove()
            )
        else:
            logger.error("Error from API for user %s: %s", user.first_name, response.text)
            await update.message.reply_text(
                "Hubo un error al registrar tu emoción.", reply_markup=ReplyKeyboardRemove()
            )
    except requests.exceptions.RequestException as e:
        logger.error("Connection error with backend: %s", e)
        await update.message.reply_text(
            "No se pudo conectar con el backend.", reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Registro de emoción cancelado.", reply_markup=ReplyKeyboardRemove()
    )
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
        entry_points=[CommandHandler("start", start)],
        states={
            EMOTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, emotion)],
            LEVEL: [MessageHandler(filters.Regex("^[1-5]$"), level)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    
    logger.info("¡El bot de Telegram está funcionando! Esperando mensajes...")
    application.run_polling()

if __name__ == "__main__":
    main()
