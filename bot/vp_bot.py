from aiogram import Bot
import config


vp_bot = Bot(config.BOT_TOKEN)
Bot.set_current(vp_bot)