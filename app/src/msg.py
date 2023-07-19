from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

import env

def send_message_to_telegram(chat_id, message, reply_markup=None):
    bot = Bot(token=env.TELEGRAM_TOKEN)
    bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)