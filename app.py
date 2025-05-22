import os
import telebot
from flask import Flask, request
from openai import OpenAI

# Получение ключей из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Проверка наличия токенов
if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ Отсутствует TELEGRAM_BOT_TOKEN или OPENAI_API_KEY в переменных окружения")

# Инициализация бота Telegram и клиента OpenAI
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# Flask-приложение
app = Flask(__name__)

@app.route('/', methods=["GET"])
def home():
    return '🤖 Бот работает!'

@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        user_input = message.text
        print(f"📩 Сообщение: {user_input}")

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}]
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        reply = f"❌ Ошибка: {e}"

    bot.send_message(message.chat.id, reply)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

