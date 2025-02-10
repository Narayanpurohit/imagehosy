import os
import re
import logging
import aiohttp
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from imdb import IMDb

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot Configuration
BOT_TOKEN = "7727908791:AAFz7vFBuJTfcRneBEJmceTy775xIjH2MPY"
API_ID = int("15191874")
API_HASH = "3037d39233c6fad9b80d83bb8a339a07"

# Directories
IMDB_DIR = "/www/wwwroot/Jnmovies.site/wp-content/uploads/"
USER_DIR = "/www/wwwroot/Jnmovies.site/ss/"
BASE_URL = "https://jnmovies.site/"

# Ensure directories exist
os.makedirs(IMDB_DIR, exist_ok=True)
os.makedirs(USER_DIR, exist_ok=True)

# Initialize bot
bot = Client("ImageHostBot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)
imdb = IMDb()

# Function to generate unique filenames
def get_unique_filename(directory, filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(os.path.join(directory, filename)):
        filename = f"{base}_{counter}{ext}"
        counter += 1
    return filename

# Sanitize filenames
def sanitize_filename(filename):
    return re.sub(r"[^\w\-_.]", "", filename)

# Start command
@bot.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text("Hello! Send me an IMDb link or an image file to host.")

# Handle IMDb Links
@bot.on_message(filters.text & filters.regex(r"imdb\.com/title/tt\d+"))
async def handle_imdb(client: Client, message: Message):
    imdb_url = message.text.strip()

    # Extract IMDb ID
    match = re.search(r"title/(tt\d+)", imdb_url)
    if not match:
        await message.reply_text("Invalid IMDb link!")
        return

    imdb_id = match.group(1)
    movie = imdb.get_movie(imdb_id[2:])  # IMDbPY uses only the digits

    if not movie:
        await message.reply_text("Couldn't fetch IMDb details!")
        return

    title = sanitize_filename(movie["title"].replace(" ", "_"))
    poster_url = movie.get("full-size cover url")

    if not poster_url:
        await message.reply_text("No poster found for this movie!")
        return

    # Download poster
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(poster_url) as response:
                if response.status != 200:
                    await message.reply_text("Failed to download poster!")
                    return
                content = await response.read()
    except Exception as e:
        await message.reply_text(f"Failed to download poster: {e}")
        return

    # Save image
    filename = get_unique_filename(IMDB_DIR, f"{title}.jpg")
    filepath = os.path.join(IMDB_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(content)

    # Send image link
    image_url = f"{BASE_URL}wp-content/uploads/{filename}"
    await message.reply_text(f"Poster saved! ✅\n[View Image]({image_url})", disable_web_page_preview=True)

# Handle User-Uploaded Images
@bot.on_message(filters.document)
async def handle_image(client: Client, message: Message):
    doc = message.document
    if not doc.mime_type.startswith("image/"):
        await message.reply_text("Please send an image file!")
        return

    filename = sanitize_filename(doc.file_name or f"image_{message.message_id}.jpg")
    filepath = os.path.join(USER_DIR, filename)

    await message.reply_text("Saving image... ⏳")
    await message.download(file_name=filepath)

    # Send image link
    image_url = f"{BASE_URL}ss/{filename}"
    await message.reply_text(f"Image saved! ✅\n[View Image]({image_url})", disable_web_page_preview=True)

# Start the bot
if __name__ == "__main__":
    logger.info("Bot is starting...")
    bot.run()