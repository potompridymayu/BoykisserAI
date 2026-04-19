import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
import google.generativeai as genai

# Подтягиваем ключи
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_KEY", "").strip()

# Настройка Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# Приветствие
@dp.message(F.new_chat_members)
async def welcome(message: types.Message):
    for user in message.new_chat_members:
        if user.id != (await bot.get_me()).id:
            await message.answer(f"Привіт, {user.first_name}! Я ожив!")

# Ответы ИИ
@dp.message(F.text.lower().startswith("bk "))
async def chat(message: types.Message):
    prompt = message.text[3:].strip()
    if not prompt: return
    
    await bot.send_chat_action(message.chat.id, action="typing")
    
    try:
        # Прямой запрос без лишних оберток
        response = model.generate_content(prompt)
        await message.reply(response.text)
    except Exception as e:
        error_msg = str(e)
        logging.error(f"Error: {error_msg}")
        # Если опять 404, бот сам предложит что делать
        if "404" in error_msg:
            await message.reply("Всё еще 404. Google не видит модель. Попробуй подождать 15 минут или смени аккаунт Google.")
        else:
            await message.reply(f"Ошибка: {error_msg[:100]}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
