from callbacks import API_TOKEN
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
        application = Application.builder().token(API_TOKEN).build()
        # Register chat
        application.add_handler(CommandHandler("reg", callback=register_chat))
        # Register forwarding rules
        application.add_handler(CommandHandler("fwd", callback=set_forward))
        # Try to forward any message that is not a command
        application.add_handler(
            MessageHandler(filters.Regex(r"#\w+.*"), callback=try_forward)
        )
        application.add_handler(
            MessageHandler(
                filters.CaptionRegex(r"#\w+.*"), callback=try_forward
            )
        )
        # Print alive
        logger.info("Running IrRedirector TG Bot | To stop press Ctrl+C")
        # Run the bot until the user presses Ctrl-C
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception:
        logger.exception("Tragic fail")


if __name__ == "__main__":
    main()
