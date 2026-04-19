import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from google import genai

# 1. ЗАГРУЗКА КЛЮЧЕЙ (Чистим от лишних пробелов/переносов)
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_KEY", "").strip()

# Твой ID гифки
WELCOME_GIF = "CgACAgIAAxkBAAMEaeTWVAABQqZK6helgWVlaTjAez2_AAK2fQACaAMJSPGizpcfJjErOwQ"

# 2. ИНИЦИАЛИЗАЦИЯ
client = genai.Client(api_key=GEMINI_API_KEY)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# 3. ОБРАБОТКА НОВЫХ УЧАСТНИКОВ (Приветствие)
@dp.message(F.new_chat_members)
async def welcome_new_member(message: types.Message):
    for user in message.new_chat_members:
        # Не приветствуем самого бота
        if user.id != (await bot.get_me()).id:
            try:
                await message.answer_animation(
                    animation=WELCOME_GIF,
                    caption=f"Привіт, друк {user.first_name}! Ласкаво просимо! ✨"
                )
            except Exception as e:
                logging.error(f"Ошибка при отправке гифки: {e}")

# 4. ОБРАБОТКА КОМАНДЫ "bk " (Запросы к ИИ)
@dp.message(F.text.lower().startswith("bk "))
async def handle_gemini_request(message: types.Message):
    # Убираем "bk " из начала сообщения
    user_prompt = message.text[3:].strip()
    if not user_prompt:
        return
    
    # Показываем, что бот "печатает"
    await bot.send_chat_action(message.chat.id, action="typing")
    
    try:
        # Отправляем запрос в Gemini
        # Используем gemini-1.5-flash — она быстрая и стабильная
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=user_prompt
        )
        
        if response.text:
            await message.reply(response.text)
        else:
            await message.reply("ИИ промолчал... попробуй спросить иначе.")
            
    except Exception as e:
        error_text = str(e)
        logging.error(f"Ошибка Gemini: {error_text}")
        
        # Если ошибка 404 — значит Google еще не активировал ключ для этой модели
        if "404" in error_text:
            await message.reply("Ошибка 404: Google ещё активирует твой ключ. Подожди 5-10 минут.")
        else:
            await message.reply(f"Ой, что-то пошло не так при общении с ИИ. 🐾\n(Текст ошибки: {error_text[:50]}...)")

# 5. ЗАПУСК
async def main():
    # Удаляем вебхуки, чтобы бот не конфликтовал сам с собой
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")
