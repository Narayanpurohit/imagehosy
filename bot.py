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


# ✅ Handler for User-Uploaded Images
@app.on_message(filters.photo)
async def handle_image(client: Client, message: Message):
    """Handles user-uploaded images, saves them, and provides a direct link."""
    file = await message.download()
    original_name = f"{message.photo.file_id}.jpg"  # Generates unique filename

    saved_url = save_uploaded_image(file, original_name)

    await message.reply_text(f"✅ Your image has been saved:\n{saved_url}")


import os
import re
import requests
from imdb import Cinemagoer

# 🔹 IMDbPY Setup
ia = Cinemagoer()

# 🔹 Define Image Storage Path
IMDB_IMAGE_DIR = "/www/wwwroot/Jnmovies.site/wp-content/uploads/"
os.makedirs(IMDB_IMAGE_DIR, exist_ok=True)  # Ensure directory exists

def fetch_imdb_data(imdb_url):
    """Fetches IMDb movie title and poster URL using IMDbPY."""
    
    # Extract IMDb ID (Works for both normal & mobile IMDb links)
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

        # Extract movie title & poster URL
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
        return None  # No poster available

    ext = poster_url.split(".")[-1].split("?")[0]  # Get file extension
    file_name = f"{movie_title}.{ext}"
    file_path = os.path.join(IMDB_IMAGE_DIR, file_name)

    # Check for duplicate filenames
    counter = 1
    while os.path.exists(file_path):
        file_path = os.path.join(IMDB_IMAGE_DIR, f"{movie_title}_{counter}.{ext}")
        counter += 1

    print(f"⬇️ Downloading poster: {poster_url} → {file_path}")

    response = requests.get(poster_url, stream=True)
    if response.status_code == 200:
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        return file_path  # Return saved file path
    return None

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