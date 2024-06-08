import os

from dotenv import load_dotenv
from logger import logger
from telegram import Update
from telegram.ext import ContextTypes

from db import get_chat_id
from db import get_receivers
from db import put


load_dotenv()
API_TOKEN = os.getenv("TG_BOT_API_TOKEN")
ROOTERS = os.getenv("ROOTERS").split(",")


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
        await put(chat_alias, update.message.chat_id)
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
                await put(tag, receivers)
                await context.bot.send_message(
                    update.message.chat_id,
                    f"Have registered forwarding to {receivers} by tag {tag}",
                )
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
        if update.message.text or update.message.caption:
            message_text = (
                update.message.text.strip()
                if update.message.text
                else update.message.caption
            )
            if message_text.startswith("#"):
                tag = message_text.split("\n")[0]
                tag = tag.strip()
                receivers = await get_receivers(tag)
                if receivers:
                    for receiver in receivers:
                        chat_id = await get_chat_id(receiver)
                        if chat_id and chat_id != update.message.chat_id:
                            await context.bot.forward_message(
                                chat_id,
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
