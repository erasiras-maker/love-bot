import telebot
import os
import random
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from telebot import types

# ------------------ ВСТАВЬ СВОЙ ТОКЕН ------------------
TOKEN = "8480081700:AAGB4Cp1_eCQPo3sXkoebYCGiEmB5YkTUbo"
bot = telebot.TeleBot(TOKEN)

# Для хранения текущего задания каждого пользователя
user_task = {}

# ------------------ START ------------------
@bot.message_handler(commands=["start"])
def start(message):
    text = (
        "❤️ Привет, любимая.\n"
        "Я очень тебя люблю и для укрепления наших отношений "
        "создал карту наших свиданий 💌\n\n"
        "Нажми кнопку ниже, чтобы получить задание"
    )
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton("Получить задание")
    markup.add(button)
    
    bot.send_message(message.chat.id, text, reply_markup=markup)

# ------------------ КНОПКА ПОЛУЧЕНИЯ ЗАДАНИЯ ------------------
@bot.message_handler(func=lambda m: m.text == "Получить задание")
def send_task(message):
    cards = os.listdir("cards")
    if not cards:
        bot.send_message(message.chat.id, "❌ Нет карточек в папке.")
        return

    # Выбираем случайную карточку
    card = random.choice(cards)
    card_path = os.path.join("cards", card)
    user_task[message.chat.id] = card_path

    with open(card_path, "rb") as photo:
        bot.send_photo(message.chat.id, photo)

    bot.send_message(
        message.chat.id,
        "📸 Это ваше задание.\n"
        "У вас есть 2 недели, чтобы выполнить его.\n\n"
        "После выполнения — пришли ваше общее фото ❤️"
    )

# ------------------ ПРИЁМ ФОТО ------------------
@bot.message_handler(content_types=["photo"])
def receive_photo(message):
    if message.chat.id not in user_task:
        bot.send_message(message.chat.id, "⚠️ Сначала получи задание.")
        return

    # Скачать фото от пользователя
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    user_photo_path = f"user_{message.chat.id}.png"
    with open(user_photo_path, "wb") as f:
        f.write(downloaded_file)

    card_path = user_task[message.chat.id]
    result_path = make_collage(card_path, user_photo_path)

    with open(result_path, "rb") as img:
        bot.send_photo(message.chat.id, img)

    bot.send_message(message.chat.id, "💖 Это наше с тобой общее воспоминание, солнце ☀️")

    # Очистка
    os.remove(user_photo_path)
    del user_task[message.chat.id]

# ------------------ ФУНКЦИЯ ВСТАВКИ ФОТО В ЦЕНТР ------------------
def make_collage(card_path, user_photo_path):
    base = Image.open(card_path).convert("RGB")
    user_img = Image.open(user_photo_path).convert("RGBA")

    # размеры карточки
    card_w, card_h = base.size

    # максимальный размер фото (чтобы фото не занимало всю карточку)
    max_w = int(card_w * 0.7)  # 70% ширины
    max_h = int(card_h * 0.5)  # 50% высоты

    # сохраняем пропорции
    user_img.thumbnail((max_w, max_h))

    # координаты для центрирования
    paste_x = (card_w - user_img.width) // 2
    paste_y = (card_h - user_img.height) // 2

    # создаём лёгкую тень (эффект “инстакс-фото”)
    shadow = Image.new("RGBA", (user_img.width + 10, user_img.height + 10), (0,0,0,80))
    base.paste(shadow, (paste_x + 5, paste_y + 5), shadow)

    # вставляем фото
    base.paste(user_img, (paste_x, paste_y), user_img)

    # дата и подпись
    draw = ImageDraw.Draw(base)
    today = datetime.now().strftime("%d.%m.%Y")
    try:
        font_big = ImageFont.truetype("arial.ttf", 42)
        font_small = ImageFont.truetype("arial.ttf", 32)
    except:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    draw.text((180, 1380), f"📅 {today}", fill=(80,80,80), font=font_small)
    draw.text((180, 1440),
              "Это наше с тобой общее воспоминание, солнце ☀️",
              fill=(180,60,90),
              font=font_big)

    if not os.path.exists("results"):
        os.mkdir("results")
    
    result_path = f"results/result_{random.randint(1000,9999)}.png"
    base.save(result_path)
    return result_path

# ------------------ ЗАПУСК ------------------
print("✅ Бот запущен...")
bot.infinity_polling()
