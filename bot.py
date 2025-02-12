import os
import requests
import base64
from imdb import Cinemagoer
from pyrogram import Client, filters
from pyrogram.types import Message
import re
# 🔹 Pyrogram Bot Setup
API_ID = 15191874
API_HASH = "3037d39233c6fad9b80d83bb8a339a07"
BOT_TOKEN = "7727908791:AAHUDR2RyXynqjnTgGkeN1zOHf79GanWCqk"

app = Client("image_host_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🔹 WordPress API Details
WP_URL = "https://jnmovies.site/wp-json/wp/v2/media"
WP_USER = "bot"
WP_APP_PASSWORD = "xvBu 19Cm GzIj mTMi pO0z 1ODM"  # Store this securely

# 🔹 IMDbPY Setup
ia = Cinemagoer()

def upload_to_wordpress(image_path):
    """Uploads an image to WordPress Media Library and returns the URL."""
    
    with open(image_path, "rb") as img:
        image_data = img.read()

    filename = os.path.basename(image_path)
    
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode(),
        "Content-Disposition": f"attachment; filename={filename}",
        "Content-Type": "image/jpeg"
    }

    response = requests.post(WP_URL, headers=headers, data=image_data)

    if response.status_code == 201:
        return response.json().get("source_url")
    else:
        print(f"❌ Upload failed: {response.text}")
        return None

@app.on_message(filters.photo)
async def handle_image(client: Client, message: Message):
    """Handles user-uploaded images, uploads to WordPress, and returns the URL."""
    
    file_path = await message.download()
    
    wp_url = upload_to_wordpress(file_path)

    if wp_url:
        await message.reply_text(f"✅ Your image has been uploaded:\n{wp_url}")
    else:
        await message.reply_text("❌ Failed to upload image to WordPress.")

# ✅ IMDb Poster Fetch & Upload
def fetch_imdb_data(imdb_url):
    """Fetches IMDb movie title and poster URL."""
    
    imdb_id_match = re.search(r'tt(\d+)', imdb_url)
    imdb_id = imdb_id_match.group(1) if imdb_id_match else None

    if not imdb_id:
        return None, None

    try:
        movie = ia.get_movie(imdb_id)
        if not movie:
            return None, None

        title = movie.get("title", "Unknown_Title").replace(" ", "_").replace("/", "_")
        poster_url = movie.get("full-size cover url", None)

        return title, poster_url

    except Exception as e:
        print(f"⚠️ Error fetching IMDb data: {str(e)}")
        return None, None

def download_imdb_poster(poster_url, movie_title):
    """Downloads and saves the IMDb poster."""
    
    if not poster_url:
        return None

    ext = poster_url.split(".")[-1].split("?")[0]
    file_name = f"{movie_title}.{ext}"
    file_path = os.path.join("/tmp", file_name)

    response = requests.get(poster_url, stream=True)
    if response.status_code == 200:
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        return file_path
    return None

@app.on_message(filters.text)
async def handle_message(client, message):
    """Handles IMDb links and uploads movie posters to WordPress."""
    
    text = message.text.strip()

    if "imdb.com/title/" in text:
        title, poster_url = fetch_imdb_data(text)

        if not title or not poster_url:
            await message.reply_text("❌ Failed to fetch IMDb image.")
            return

        saved_poster = download_imdb_poster(poster_url, title)

        if saved_poster:
            wp_url = upload_to_wordpress(saved_poster)

            if wp_url:
                await message.reply_text(f"🎬 IMDb Poster Uploaded:\n{wp_url}")
            else:
                await message.reply_text("❌ Failed to upload IMDb poster.")
        else:
            await message.reply_text("❌ Failed to download IMDb poster.")

# ✅ Run the bot
if __name__ == "__main__":
    print("🚀 Bot is running...")
    app.run()