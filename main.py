import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from google import genai

# Подтягиваем ключи из настроек сервера (Railway/Render)
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_KEY")

# Твой ID гифки с котиком
WELCOME_GIF = "CgACAgIAAxkBAAMEaeTWVAABQqZK6helgWVlaTjAez2_AAK2fQACaAMJSPGizpcfJjErOwQ"

# Настройка ИИ и бота
client = genai.Client(api_key=GEMINI_API_KEY)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# 1. ПРИВЕТСТВИЕ НОВЫХ УЧАСТНИКОВ
@dp.message(F.new_chat_members)
async def welcome_new_member(message: types.Message):
    for user in message.new_chat_members:
        # Проверяем, что зашел не сам бот
        if user.id != (await bot.get_me()).id:
            try:
                await message.answer_animation(
                    animation=WELCOME_GIF,
                    caption=f"Привіт, друк {user.first_name}! Ласкаво просимо! ✨"
                )
            except Exception as e:
                logging.error(f"Ошибка отправки гифки: {e}")

# 2. РАБОТА С КОМАНДОЙ "bk "
@dp.message(F.text.lower().startswith("bk "))
async def handle_gemini_request(message: types.Message):
    # Отрезаем "bk " от сообщения
    user_prompt = message.text[3:].strip()
    if not user_prompt:
        return
    
    # Показываем, что бот печатает
    await bot.send_chat_action(message.chat.id, action="typing")
    
    try:
        # Запрос к Gemini
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=f"Ты — дружелюбный персонаж. Отвечай кратко: {user_prompt}"
        )
        
        if response.text:
            await message.reply(response.text)
        else:
            await message.reply("ИИ задумался и ничего не ответил... 😶")
            
    except Exception as e:
        logging.error(f"Ошибка Gemini: {e}")
        await message.reply("Ой, что-то пошло не так при общении с ИИ. 🐾")

# Запуск
async def main():
    # Пропускаем накопленные сообщения при запуске
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")

