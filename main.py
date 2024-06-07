import logging

from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import MessageHandler

logger = logging.getLogger(__name__)
API_TOKEN = "7325411920:AAHvwpIZ4IjbYr4lHfTw_zAesHCVTWTj2-8"
CHATS = {}
FORWARDS = {}


async def register_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Register chat id
    """
    CHATS[update.message.from_user.name] = update.message.chat_id


async def set_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Set forwarding rule
    """
    if update.message.from_user.name in ("@IrenDeuxIren", "@rin5er"):
        parts = update.message.text.split(" ")
        if len(parts) == 3:
            tag = parts[1]
            receivers = parts[2]
            FORWARDS[tag] = receivers.split(",")
        else:
            await context.bot.send_message(
                update.message.chat_id,
                f"""Redirect should command should be:
                `/redirect #tag @Forward1,@Forward2,@Etc`
                Have received: {update.message.text}
                """,
            )


async def try_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Try to forward the message if necessary
    """
    if update.message.text:
        message_text = update.message.text.strip()
        if message_text.startswith("#"):
            tag = message_text.split("\n")[0]
            if tag in FORWARDS:
                receivers = FORWARDS[tag]
                for receiver in receivers:
                    if receiver in CHATS:
                        try:
                            await context.bot.forward_message(
                                CHATS[receiver],
                                from_chat_id=update.message.chat_id,
                                message_id=update.message.message_id,
                                disable_notification=False,
                            )
                        except Exception:
                            logger.exception(
                                f"Could not forward to {receiver}"
                            )


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(API_TOKEN).build()
    # Register chat
    application.add_handler(CommandHandler("start", callback=register_chat))
    # Register forwarding rules
    application.add_handler(CommandHandler("redirect", callback=set_forward))
    # Try to forward any message that is not a command
    application.add_handler(MessageHandler(filters=None, callback=try_forward))
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
