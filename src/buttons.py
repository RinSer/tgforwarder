from telegram import Bot
from telegram import BotCommand
from telegram.ext import Application


command_info = [BotCommand("start", "See the manual"), BotCommand("reg", "Register chat with the bot")]


async def post_init(application: Application) -> None:
    bot: Bot = application.bot
    await bot.set_my_commands(commands=command_info)
