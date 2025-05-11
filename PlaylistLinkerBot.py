import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
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
    return [t['track']['external_urls']['spotify'] for t in tracks]  # ❗️Без нумерації тут

# Обробка повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "open.spotify.com/playlist" in text:
        await update.message.reply_text("⏳ Обробляю плейлист...")
        try:
            links = get_tracks(text)
            for i, link in enumerate(links, start=1):
                await update.message.reply_text(f"{i}. {link}")
                await asyncio.sleep(0.3)  # затримка, щоб уникнути таймаутів
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка: {e}")
    else:
        await update.message.reply_text("Надішли посилання на плейлист Spotify 🎧")


# Запуск бота
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()