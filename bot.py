import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# Load configuration from environment variables
API_ID = int(os.getenv("API_ID", "15191874"))
API_HASH = os.getenv("API_HASH", "3037d39233c6fad9b80d83bb8a339a07")
BOT_TOKEN = os.getenv("BOT_TOKEN", "6677023637:AAES7_yErqBDZY7wQP1EOyIGhpAN1d9fY5o")

# Directory to save images
UPLOAD_FOLDER = "/home/wwwroot/jnmovies.site/uploads/"

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Pyrogram Client
app = Client("ImageHostBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.photo)
async def save_image(client: Client, message: Message):
    """Handles image uploads from users"""
    photo = message.photo[-1]  # Get the highest resolution image
    file_name = message.caption if message.caption else f"{photo.file_id}.jpg"

    # Sanitize filename
    file_name = file_name.replace(" ", "_").replace("/", "_")

    # Check if file already exists and rename if necessary
    base_name, ext = os.path.splitext(file_name)
    counter = 1
    while os.path.exists(os.path.join(UPLOAD_FOLDER, file_name)):
        file_name = f"{base_name}_{counter}{ext}"
        counter += 1

    file_path = os.path.join(UPLOAD_FOLDER, file_name)

    # Download the image
    await message.download(file_path)

    # Generate image URL
    image_url = f"https://jnmovies.site/uploads/{file_name}"

    # Send the image URL to the user
    await message.reply_text(f"✅ Your image has been uploaded: {image_url}")

# Run the bot
app.run()
