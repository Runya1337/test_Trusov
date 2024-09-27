import logging
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
import requests
from config import TOKEN

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Определяем этапы разговора
ASK_NAME = 1

def start(update: Update, context: CallbackContext) -> int:
    """Отправляет приветственное сообщение и переходит к этапу ASK_NAME."""
    update.message.reply_text('Добрый день. Как вас зовут?')
    return ASK_NAME

def ask_name(update: Update, context: CallbackContext) -> int:
    """Получает имя пользователя и сообщает курс доллара."""
    name = update.message.text

    # Получаем курс доллара из API ЦБ РФ
    try:
        response = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
        data = response.json()
        usd_rate = data['Valute']['USD']['Value']
        update.message.reply_text(
            f'Рад знакомству, {name}! Курс доллара сегодня {usd_rate:.2f}₽'
        )
    except Exception as e:
        logger.error(f'Ошибка при получении курса доллара: {e}')
        update.message.reply_text('Извините, не удалось получить курс доллара.')

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """Обрабатывает команду /cancel и завершает разговор."""
    update.message.reply_text('Разговор отменен.')
    return ConversationHandler.END

def main():
    """Запускает бота."""
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Определяем обработчик разговоров
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_NAME: [MessageHandler(Filters.text & ~Filters.command, ask_name)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
