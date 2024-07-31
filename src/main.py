from buttons import post_init
from callbacks import API_TOKEN
from callbacks import manual
from callbacks import register_chat
from callbacks import set_forward
from callbacks import try_forward
from logger import logger
from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import filters
from telegram.ext import MessageHandler


def main() -> None:
    """Run the bot."""
    try:
        # Create the Application and pass it your bot's token
        app = Application.builder().token(API_TOKEN).post_init(post_init).build()
        # Bot manual
        app.add_handler(CommandHandler("start", callback=manual))
        # Register chat
        app.add_handler(CommandHandler("reg", callback=register_chat))
        # Register forwarding rules
        app.add_handler(CommandHandler("fwd", callback=set_forward))
        # Try to forward any message that is not a command
        app.add_handler(MessageHandler(filters.Regex(r"#\w+.*"), callback=try_forward))
        app.add_handler(MessageHandler(filters.CaptionRegex(r"#\w+.*"), callback=try_forward))
        # Print alive
        logger.info("Running IrRedirector TG Bot | To stop press Ctrl+C")
        # Run the bot until the user presses Ctrl-C
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception:
        logger.exception("Tragic fail")


if __name__ == "__main__":
    main()
