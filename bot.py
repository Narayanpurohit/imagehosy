import os
import re
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from imdb import IMDb

# Initialize IMDb
ia = IMDb()

# Bot configuration
API_ID =15191874  # Replace with your Telegram API ID
API_HASH = "3037d39233c6fad9b80d83bb8a339a07"  # Replace with your Telegram API Hash
BOT_TOKEN = "7727908791:AAHUDR2RyXynqjnTgGkeN1zOHf79GanWCqk"  # Replace with your bot token

# Directories
IMDB_POSTER_DIR = "/www/wwwroot/Jnmovies.site/wp-content/uploads/"
USER_IMAGE_DIR = "/www/wwwroot/Jnmovies.site/ss/"

# Initialize Pyrogram client
app = Client("image_hosting_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Helper function to handle duplicate filenames
def get_unique_filename(directory, filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(os.path.join(directory, filename)):
        filename = f"{base}_{counter}{ext}"
        counter += 1
    return filename

# Start command handler
@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text("Welcome to the Image Hosting Bot! 🎉\n\n"
                             "Send an IMDb link or upload an image file to get started.")

# IMDb link handler
@app.on_message(filters.text & filters.regex(r"https?://www\.imdb\.com/title/tt\d+/"))
async def handle_imdb_link(client: Client, message: Message):
    try:
        # Extract IMDb ID
        imdb_id = re.search(r"tt\d+", message.text).group(0)
        
        # Fetch movie details
        movie = ia.get_movie(imdb_id)
        title = movie.get("title", "unknown_title").replace(" ", "_")
        poster_url = movie.get("full-size cover url")
        
        if not poster_url:
            await message.reply_text("❌ Unable to fetch the movie poster.")
            return
        
        # Download the poster
        response = requests.get(poster_url)
        if response.status_code != 200:
            await message.reply_text("❌ Failed to download the movie poster.")
            return
        
        # Save the poster
        filename = f"{title}.jpg"
        filename = get_unique_filename(IMDB_POSTER_DIR, filename)
        with open(os.path.join(IMDB_POSTER_DIR, filename), "wb") as f:
            f.write(response.content)
        
        # Send the direct link
        direct_link = f"https://jnmovies.site/wp-content/uploads/{filename}"
        await message.reply_text(f"Poster saved! ✅\n[View Image]({direct_link})")
    
    except Exception as e:
        await message.reply_text(f"❌ An error occurred: {e}")

# Image file handler
@app.on_message(filters.document & filters.photo)
async def handle_image_upload(client: Client, message: Message):
    try:
        # Check if the file is an image
        if not message.document.mime_type.startswith("image/"):
            await message.reply_text("❌ Only image files are supported.")
            return
        
        # Download the file
        file_path = await message.download()
        filename = os.path.basename(file_path)
        filename = get_unique_filename(USER_IMAGE_DIR, filename)
        
        # Move the file to the user image directory
        os.rename(file_path, os.path.join(USER_IMAGE_DIR, filename))
        
        # Send the direct link
        direct_link = f"https://jnmovies.site/ss/{filename}"
        await message.reply_text(f"Image saved! ✅\n[View Image]({direct_link})")
    
    except Exception as e:
        await message.reply_text(f"❌ An error occurred: {e}")

# Run the bot
print("Bot is running...")
app.run()