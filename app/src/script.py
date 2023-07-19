from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv
import logging
import sqlite3

import env
from transactions import get_last_transaction, track_wallet_transactions, process_transaction
from msg import send_message_to_telegram


# Configuração do logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update, context):
    logger.info("Solicitado comando /start")
    message = "Bem-vindo! Clique nos botões abaixo para realizar as ações:\n\n" \
              "• /track - Ativar o rastreamento de transações\n" \
              "• /last - Obter a última transação realizada na carteira"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def track(update, context):
    logger.info("Solicitado comando /track")
    message = "Rastreamento de transações ativado. Você receberá uma notificação sempre que ocorrer uma transação na carteira."
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

    # Verificar transações a cada 60 segundos
    context.job_queue.run_repeating(track_wallet_transactions, interval=60, first=0)

def stop(update, context):
    logger.info("Solicitado comando stop")
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Você parou de receber as informações de transações.")
    query.job.context.job_queue.stop()

def last(update, context):
    logger.info("Solicitado comando /last")
    message=process_transaction(get_last_transaction(), False)
    send_message_to_telegram(env.CHAT_ID, message)
    message = "👆👆👆\nEsta é a última transação realizada na sua carteira."
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def main():
    logger.info("-----------------------------------")
    logger.info("         Início do Bot")
    logger.info("-----------------------------------")
    updater = Updater(token=env.TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("track", track))
    dispatcher.add_handler(CommandHandler("last", last))
    dispatcher.add_handler(CallbackQueryHandler(stop, pattern='^stop$'))

    # Adicionar botões interativos
    track_button = InlineKeyboardButton("Rastrear transações", callback_data='track')
    last_button = InlineKeyboardButton("Última transação", callback_data='last')
    keyboard = [[track_button], [last_button]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    dispatcher.add_handler(CommandHandler("buttons", lambda update, context: send_message_to_telegram(update.effective_chat.id, "Escolha uma ação:", reply_markup=reply_markup)))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
