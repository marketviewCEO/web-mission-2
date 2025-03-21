import os
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Токен бота
TELEGRAM_BOT_TOKEN = "BOT TOKEN"
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HUGGINGFACE_API_TOKEN = "API TOKEN"

# Функция генерации изображения
async def generate_image(prompt: str):
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "num_inference_steps": 30,
            "guidance_scale": 7.5,
            "width": 512,
            "height": 512
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(HUGGINGFACE_API_URL, headers=headers, json=payload) as response:
                if response.status == 200:
                    return await response.read()  # Возвращает бинарные данные изображения
                else:
                    error_text = await response.text()
                    print(f"Ошибка API: {response.status} - {error_text}")
    except Exception as e:
        print(f"Ошибка при генерации изображения: {e}")
    return None

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Отправь мне текст, и я создам изображение.')

# Обработчик сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        prompt = update.message.text
        print(f"Получен запрос: {prompt}")
        
        # Отправляем сообщение о начале генерации
        processing_message = await update.message.reply_text("Генерирую изображение, пожалуйста подождите...")
        
        image = await generate_image(prompt)
        
        if image:
            await update.message.reply_photo(photo=image)
            print("Изображение успешно отправлено")
        else:
            await update.message.reply_text("Ошибка при генерации изображения. Попробуйте другой запрос.")
        
        # Удаляем сообщение о генерации
        await processing_message.delete()
    except Exception as e:
        print(f"Ошибка в обработке сообщения: {e}")
        await update.message.reply_text("Произошла ошибка при обработке запроса.")

def main():
    """Основная функция для запуска бота"""
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Бот запущен...")
    
    # Запускаем бота
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
    finally:
        print("Бот завершил работу")
