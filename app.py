import os
from flask import Flask, request
import telebot
from telebot import types
from openai import OpenAI

# Получение переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Проверка переменных окружения
if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ Отсутствует TELEGRAM_BOT_TOKEN или OPENAI_API_KEY в переменных окружения")

# Инициализация Telegram-бота и OpenAI клиента
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# Инициализация Flask
app = Flask(__name__)

@app.route('/', methods=["GET"])
def home():
    return '🤖 Бот работает!'

@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# Обработка команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🔍 Задать вопрос")
    btn2 = types.KeyboardButton("ℹ️ О боте")
    btn3 = types.KeyboardButton("📞 Связь с разработчиком")
    markup.add(btn1, btn2, btn3)

    welcome_text = (
        "Приветствую! Я искусственный суперинтеллект Джарвис, созданный @karim_co для помощи пользователям в поиске информации.\n\n"
        "Что вас интересует?"
    )

    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# Обработка всех остальных сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        user_input = message.text

        # Обработка встроенных кнопок
        if user_input == "ℹ️ О боте":
            bot.send_message(message.chat.id, "Я ИИ-ассистент для поиска информации. Напиши вопрос!")
            return
        elif user_input == "📞 Связь с разработчиком":
            bot.send_message(message.chat.id, "Связаться с автором: @karim_co")
            return

        # Запрос к OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}]
        )
        reply = response.choices[0].message.content.strip()

    except Exception as e:
        reply = f"❌ Ошибка: {e}"

    bot.send_message(message.chat.id, reply)

# Запуск Flask-сервера
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


