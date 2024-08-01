import functools
import inspect
import os

from dotenv import load_dotenv
from logger import logger
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from db import add_db_user
from db import get_chat_id
from db import get_receivers
from db import get_users
from db import put


load_dotenv()
API_TOKEN = os.getenv("TG_BOT_API_TOKEN")
ROOTERS = [int(user_id) for user_id in os.getenv("ROOTERS").split(",")]
MANUAL_TEXT = r"""
To forward messages, you need to create a chat with the recipient or destination chat/group\.
Add the bot as a user to the chat or group and execute the /reg command\.
For the bot to send messages to a user, the user must find the bot and send the /reg command in a private message\.

To set up forwarding, execute the /fwd command in the chat or group from which messages should be forwarded,
using the format: /fwd \#hashtag *\[list of usernames and/or chat/group names separated by commas\]*\.
After this, any message starting with \#hashtag as the first line will be forwarded to all users, groups, or chats specified in the /fwd command\.
"""


def auth(users):
    def auth_func(func):
        @functools.wraps(func)
        async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if inspect.iscoroutinefunction(users):
                user_ids = await users()
            else:
                user_ids = users
            if update.message.from_user.id in user_ids:
                await func(update, context)
            else:
                await context.bot.send_message(update.message.chat_id, "Permissions denied")

        return callback

    return auth_func


@auth(ROOTERS)
async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.message.text.split(" ")[1]
        await add_db_user(user_id)
        await context.bot.send_message(update.message.chat_id, f"Have added user id {user_id}")
    except Exception:
        msg = f"Could not {update.message.text}"
        logger.exception(msg)
        await context.bot.send_message(update.message.chat_id, msg)


async def manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Send user manual
    """
    try:
        await context.bot.send_message(update.message.chat_id, MANUAL_TEXT, parse_mode=ParseMode.MARKDOWN_V2)
    except Exception:
        msg = "Could not send manual"
        logger.exception(msg)
        await context.bot.send_message(update.message.chat_id, msg)


async def register_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Register chat id
    """
    try:
        message_parts = update.message.text.split(" ")
        chat_alias = update.message.from_user.name if len(message_parts) < 2 else message_parts[1]
        await put(chat_alias, update.message.chat_id)
        await context.bot.send_message(update.message.chat_id, f"Have saved chat with {chat_alias}")
    except Exception:
        msg = f"Could not register chat alias {update.message.text}"
        logger.exception(msg)
        await context.bot.send_message(update.message.chat_id, msg)


@auth(get_users)
async def set_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Set forwarding rule
    """
    try:
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
                f"""Forward command should be:
`/fwd #tag @Person0,Chat1,etc...`
Have received: {update.message.text}
                """,
            )
    except Exception:
        msg = f"Could not set forward {update.message.text}"
        logger.exception(msg)
        await context.bot.send_message(update.message.chat_id, msg)


async def try_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Try to forward the message if necessary
    """
    try:
        if update.message.text or update.message.caption:
            message_text = update.message.text.strip() if update.message.text else update.message.caption
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
                        elif not chat_id:
                            msg = update.message.text
                            await context.bot.send_message(
                                update.message.chat_id,
                                f"{msg}: unknown chat {receiver}",
                            )
    except Exception:
        msg = f"Error forwarding {update.message.text} to {update.message.id}"
        logger.exception(msg)
        await context.bot.send_message(update.message.chat_id, msg)
