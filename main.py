import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from google import genai

# Подтягиваем ключи из Variables Railway
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_KEY")

# Твой ID гифки
WELCOME_GIF = "CgACAgIAAxkBAAMEaeTWVAABQqZK6helgWVlaTjAez2_AAK2fQACaAMJSPGizpcfJjErOwQ"

# Настройка ИИ и бота
client = genai.Client(api_key=GEMINI_API_KEY)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# 1. ПРИВЕТСТВИЕ
@dp.message(F.new_chat_members)
async def welcome_new_member(message: types.Message):
    for user in message.new_chat_members:
        if user.id != (await bot.get_me()).id:
            try:
                await message.answer_animation(
                    animation=WELCOME_GIF,
                    caption=f"Привіт, друк {user.first_name}! Ласкаво просимо! ✨"
                )
            except Exception as e:
                logging.error(f"Ошибка гифки: {e}")

# 2. ОСНОВНАЯ ЛОГИКА (Исправлено под логи)
@dp.message(F.text.lower().startswith("bk "))
async def handle_gemini_request(message: types.Message):
    user_prompt = message.text[3:].strip()
    if not user_prompt:
        return
    
    await bot.send_chat_action(message.chat.id, action="typing")
    
    try:
        # Используем актуальное имя модели, чтобы избежать 404
        response = client.models.generate_content(
            model="model="gemini-1.5-flash-8b", 
            contents=user_prompt
        )
        
        if response.text:
            await message.reply(response.text)
        else:
            await message.reply("ИИ промолчал... попробуй другой вопрос.")
            
    except Exception as e:
        error_msg = str(e)
        logging.error(f"Ошибка Gemini: {error_msg}")
        # Выводим часть ошибки в чат для диагностики
        await message.reply(f"Ошибка ИИ: {error_msg[:50]}... Проверь API ключ в Variables!")

# Запуск
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот выключен")
