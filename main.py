import logging
import os
import sys

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import filters
from telegram.ext import MessageHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

load_dotenv()
API_TOKEN = os.getenv("TG_BOT_API_TOKEN")
ROOTERS = os.getenv("ROOTERS").split(",")

CHATS = {}
FORWARDS = {}


async def register_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Register chat id
    """
    try:
        message_parts = update.message.text.split(" ")
        chat_alias = (
            update.message.from_user.name
            if len(message_parts) < 2
            else message_parts[1]
        )
        CHATS[chat_alias] = update.message.chat_id
        await context.bot.send_message(
            update.message.chat_id, f"Have saved {chat_alias}"
        )
    except Exception:
        logger.exception(f"Could register chat alias {update.message.text}")
        await context.bot.send_message(
            update.message.chat_id,
            f"Could not register chat alias {update.message.text}",
        )


async def set_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Set forwarding rule
    """
    try:
        if update.message.from_user.name in ROOTERS:
            parts = update.message.text.split(" ")
            if len(parts) == 3:
                tag = parts[1]
                receivers = parts[2]
                FORWARDS[tag] = [r.strip() for r in receivers.split(",")]
            else:
                await context.bot.send_message(
                    update.message.chat_id,
                    f"""Redirect should command should be:
`/redirect #tag @Person0,Chat1,etc...`
Have received: {update.message.text}
                    """,
                )
    except Exception:
        logger.exception(f"Could set redirect {update.message.text}")
        await context.bot.send_message(
            update.message.chat_id,
            f"Could not set redirect {update.message.text}",
        )


async def try_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Try to forward the message if necessary
    """
    try:
        if update.message.text:
            message_text = update.message.text.strip()
            if message_text.startswith("#"):
                tag = message_text.split("\n")[0]
                tag = tag.strip()
                if tag in FORWARDS:
                    receivers = FORWARDS[tag]
                    for receiver in receivers:
                        if receiver in CHATS:
                            await context.bot.forward_message(
                                CHATS[receiver],
                                from_chat_id=update.message.chat_id,
                                message_id=update.message.message_id,
                                disable_notification=False,
                            )
                        else:
                            await context.bot.send_message(
                                update.message.chat_id,
                                f"{update.message.text}: unknown {receiver}",
                            )
    except Exception:
        logger.exception(f"Could not forward to {update.message.id}")
        await context.bot.send_message(
            update.message.chat_id, f"Error forwarding {update.message.text}"
        )


def main() -> None:
    """Run the bot."""
    try:
        # Create the Application and pass it your bot's token
        application = Application.builder().token(API_TOKEN).build()
        # Register chat
        application.add_handler(CommandHandler("reg", callback=register_chat))
        # Register forwarding rules
        application.add_handler(CommandHandler("fwd", callback=set_forward))
        # Try to forward any message that is not a command
        application.add_handler(
            MessageHandler(filters.Regex(r"#\w+.*"), callback=try_forward)
        )
        # Print alive
        logger.info("Running IrRedirector TG Bot | To stop press Ctrl+C")
        # Run the bot until the user presses Ctrl-C
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception:
        logger.exception("Tragic fail")


if __name__ == "__main__":
    main()
