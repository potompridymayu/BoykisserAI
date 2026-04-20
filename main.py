import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from google import genai

# 1. Загрузка ключей (авто-очистка)
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_KEY", "").strip()

# Твоя гифка
WELCOME_GIF = "CgACAgIAAxkBAAMEaeTWVAABQqZK6helgWVlaTjAez2_AAK2fQACaAMJSPGizpcfJjErOwQ"

# Инициализация
client = genai.Client(api_key=GEMINI_API_KEY)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# Список моделей по приоритету (если одна 404, пробуем следующую)
MODELS = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-flash-8b"]

@dp.message(F.text.lower().startswith("bk "))
async def handle_ai(message: types.Message):
    prompt = message.text[3:].strip()
    if not prompt: return
    
    await bot.send_chat_action(message.chat.id, action="typing")
    
    # Пытаемся перебрать модели автоматически
    for model_name in MODELS:
        try:
            response = client.models.generate_content(
                model=model_name, 
                contents=prompt
            )
            if response.text:
                await message.reply(response.text)
                return # Успех! Выходим из цикла
        except Exception as e:
            logging.error(f"Модель {model_name} не сработала: {e}")
            continue # Пробуем следующую модель
    
    # Если ни одна модель не сработала
    await message.reply("❌ Ошибка: Все доступные модели выдали отказ (404). Скорее всего, нужно зайти в AI Studio с VPN и нажать 'Accept' в окне условий.")

@dp.message(F.new_chat_members)
async def welcome(message: types.Message):
    for user in message.new_chat_members:
        if user.id != (await bot.get_me()).id:
            try:
                await message.answer_animation(animation=WELCOME_GIF, caption=f"Привіт, {user.first_name}! ✨")
            except:
                await message.answer(f"Привіт, {user.first_name}!")

async def main():
    # Авто-чистка вебхуков при старте
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
