import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent / "PlaylistLinkerBot.env")

print("DEBUG client_id:", os.getenv("SPOTIFY_CLIENT_ID"))  # має вивести client_id, якщо .env працює

# Токени з .env
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Spotify клієнт
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))


# Отримання треків з плейлиста
def get_tracks(playlist_url):
    playlist_id = playlist_url.split("/")[-1].split("?")[0]
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return [t['track']['external_urls']['spotify'] for t in tracks]


# Обробка повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "open.spotify.com/playlist" in text:
        await update.message.reply_text("⏳ Обробляю плейлист...")

        # Кнопки для вибору формату
        keyboard = [
            [
                InlineKeyboardButton("Кожну пісню окремо", callback_data="separate"),
                InlineKeyboardButton("Всі пісні в одному повідомленні", callback_data="all_in_one")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Виберіть, як ви хочете отримати список пісень:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Надішли посилання на плейлист Spotify 🎧")


# Обробка кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Відповідаємо на натискання кнопки

    text = query.message.text
    playlist_url = query.message.reply_to_message.text  # Отримуємо URL плейлиста

    # Отримуємо список пісень
    links = get_tracks(playlist_url)

    if query.data == "separate":
        # Відправляємо кожну пісню окремо
        for i, link in enumerate(links, start=1):
            await query.message.reply_text(f"{i}. {link}")
            await asyncio.sleep(0.3)  # затримка, щоб уникнути таймаутів
    elif query.data == "all_in_one":
        # Всі пісні в одному повідомленні
        message = "\n".join([f"{i}. {link}" for i, link in enumerate(links, start=1)])
        await query.message.reply_text(message)


# Команда /stop для зупинки бота
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот зупинено.")
    await context.application.shutdown()


# Запуск бота
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CommandHandler("stop", stop))  # Додавання обробника для команди /stop
app.add_handler(CallbackQueryHandler(button))  # Додавання обробника для кнопок
app.run_polling()
