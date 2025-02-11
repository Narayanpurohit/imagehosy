import os
import re
import requests
from imdb import Cinemagoer
from pyrogram import Client, filters
from pyrogram.types import Message

# 🔹 Pyrogram Bot Setup
API_ID = 15191874
API_HASH = "3037d39233c6fad9b80d83bb8a339a07"
BOT_TOKEN = "7727908791:AAHUDR2RyXynqjnTgGkeN1zOHf79GanWCqk"

app = Client("image_host_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🔹 Define Image Storage Paths
UPLOADS_DIR = "/www/wwwroot/Jnmovies.site/wp-content/uploads/"
IMDB_IMAGE_DIR = "/www/wwwroot/Jnmovies.site/wp-content/uploads/imdb/"
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(IMDB_IMAGE_DIR, exist_ok=True)

# 🔹 IMDbPY Setup
ia = Cinemagoer()

# ✅ Function to Save User-Uploaded Images
def save_uploaded_image(file, original_name):
    """Saves user-uploaded images with a unique name and returns the URL."""
    file_ext = original_name.split(".")[-1]
    base_name = os.path.splitext(original_name)[0].replace(" ", "_").replace("/", "_")
    save_path = os.path.join(UPLOADS_DIR, f"{base_name}.{file_ext}")

    # Handle duplicate filenames
    counter = 1
    while os.path.exists(save_path):
        save_path = os.path.join(UPLOADS_DIR, f"{base_name}_{counter}.{file_ext}")
        counter += 1

    file.rename(save_path)  # Move file to correct path
    return f"https://jnmovies.site/wp-content/uploads/{os.path.basename(save_path)}"

# ✅ IMDb Scraper Functions
def fetch_imdb_data(imdb_url):
    """Fetches IMDb movie title and poster URL using IMDbPY."""
    imdb_id_match = re.search(r'tt(\d+)', imdb_url)
    imdb_id = imdb_id_match.group(1) if imdb_id_match else None

    if not imdb_id:
        print("⚠️ Invalid IMDb link!")
        return None, None

    print(f"🔍 Fetching IMDb data for ID: {imdb_id}")

    try:
        movie = ia.get_movie(imdb_id)
        if not movie:
            print("❌ IMDb data not found")
            return None, None

        title = movie.get("title", "Unknown_Title").replace(" ", "_").replace("/", "_")
        poster_url = movie.get("full-size cover url", None)

        print(f"✅ Movie Name: {title}, Poster URL: {poster_url}")
        return title, poster_url

    except Exception as e:
        print(f"⚠️ Error fetching IMDb data: {str(e)}")
        return None, None

def download_imdb_poster(poster_url, movie_title):
    """Downloads and saves the IMDb poster, handling duplicates."""
    if not poster_url:
        return None

    ext = poster_url.split(".")[-1].split("?")[0]
    file_name = f"{movie_title}.{ext}"
    save_path = os.path.join(IMDB_IMAGE_DIR, file_name)

    # Handle duplicate filenames
    counter = 1
    while os.path.exists(save_path):
        save_path = os.path.join(IMDB_IMAGE_DIR, f"{movie_title}_{counter}.{ext}")
        counter += 1

    print(f"⬇️ Downloading poster: {poster_url} → {save_path}")

    response = requests.get(poster_url, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        return save_path
    return None

# ✅ Handler for User-Uploaded Images
@app.on_message(filters.photo)
async def handle_image(client: Client, message: Message):
    """Handles user-uploaded images, saves them, and provides a direct link."""
    file = await message.download()
    original_name = f"{message.photo.file_id}.jpg"  # Generates unique filename

    saved_url = save_uploaded_image(file, original_name)

    await message.reply_text(f"✅ Your image has been saved:\n{saved_url}")

# ✅ Handler for IMDb Links
@app.on_message(filters.text)
async def handle_message(client, message):
    """Handles IMDb links and fetches movie poster images."""
    text = message.text.strip()

    if "imdb.com/title/" in text:
        print(f"📥 Received IMDb link: {text}")

        title, poster_url = fetch_imdb_data(text)

        if not title or not poster_url:
            await message.reply_text("❌ Failed to fetch IMDb image.")
            return

        saved_poster = download_imdb_poster(poster_url, title)

        if saved_poster:
            poster_url = f"https://jnmovies.site/wp-content/uploads/imdb/{os.path.basename(saved_poster)}"
            await message.reply_text(f"🎬 IMDb Poster Saved:\n{poster_url}")
        else:
            await message.reply_text("❌ Failed to download IMDb poster.")

# ✅ Run the bot
if __name__ == "__main__":
    print("🚀 Bot is running...")
    app.run()