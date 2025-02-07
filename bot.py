import os
import requests
from pyrogram import Client, filters

# Load configuration from environment variables
API_ID = int(os.getenv("API_ID", "15191874"))
API_HASH = os.getenv("API_HASH", "3037d39233c6fad9b80d83bb8a339a07")
BOT_TOKEN = os.getenv("BOT_TOKEN", "6677023637:AAES7_yErqBDZY7wQP1EOyIGhpAN1d9fY5o")

# Directory to save images
UPLOAD_FOLDER = "/www/wwwroot/Jnmovies.site/wp-content/uploads/"

# Initialize the Pyrogram client
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Function to download an image from a URL
def download_image(url, file_name):
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_name, "wb") as file:
            file.write(response.content)
        return True
    return False

# Handler for messages containing a URL
@app.on_message(filters.text & filters.private)
async def handle_message(client, message):
    url = message.text.strip()
    if url.startswith("http"):
        # Download the image
        file_name = "downloaded_image.jpg"
        if download_image(url, file_name):
            # Send the image back to the user
            await message.reply_photo(file_name)
            os.remove(file_name)  # Clean up the file
        else:
            await message.reply_text("Failed to download the image. Please check the URL.")
    else:
        await message.reply_text("Please send a valid image URL.")

# Start the bot
print("Bot is running...")
app.run()