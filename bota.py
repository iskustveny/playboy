import logging
import asyncio
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.ext import CallbackContext

# Получение порта из переменной окружения, иначе используем стандартный 8080
port = os.environ.get('PORT', 8080)

# Логирование для отладки
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Словарь, который будет хранить пары пользователей (собеседников)
pairs = {}

# Команда /start
async def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    await update.message.reply_text(f'Привет, {user.first_name}! Я анонимный бот знакомств.\n'
                                    'Напиши мне любое сообщение, чтобы начать разговор!')

# Обработка текстовых сообщений
async def handle_message(update: Update, context: CallbackContext):
    user = update.message.from_user
    text = update.message.text

    # Если пользователь уже в паре, отправляем сообщение другому пользователю
    if user.id in pairs and pairs[user.id] is not None:
        other_user_id = pairs[user.id]
        await context.bot.send_message(other_user_id, f'Сообщение от {user.first_name}: {text}')
    else:
        # Если нет пары, добавляем пользователя в очередь
        # Проверка на то, есть ли пара для текущего пользователя
        for other_user_id, paired_user in pairs.items():
            if paired_user is None and other_user_id != user.id:
                pairs[user.id] = other_user_id
                pairs[other_user_id] = user.id

                # Уведомляем обоих пользователей о паре
                await update.message.reply_text(f'Ты теперь общаешься с {user.first_name} анонимно. '
                                               'Отправьте сообщения, чтобы начать разговор.')
                await context.bot.send_message(other_user_id,
                                               f'Ты теперь общаешься с {user.first_name} анонимно. '
                                               'Отправьте сообщения, чтобы начать разговор.')
                break
        else:
            # Если не нашли пару, сообщаем, что пользователь в очереди
            pairs[user.id] = None
            await update.message.reply_text('Ты в очереди, жди собеседника...')

# Обработка ошибок
async def error(update: Update, context: CallbackContext):
    logger.warning(f'Update {update} caused error {context.error}')

def main():
    """Запуск бота."""
    # Ваш API-токен
    token = '8101914867:AAFSkaFsPsH-2un3z2voe4QP11ruzL4Zudo'

    # Создаём приложение
    application = Application.builder().token(token).build()

    # Обработчик команд
    application.add_handler(CommandHandler("start", start))

    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Обработчик ошибок
    application.add_error_handler(error)

    # Запуск бота без циклического ожидания
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
