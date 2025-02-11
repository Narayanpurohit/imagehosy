import os
from pyrogram import Client, filters
from pyrogram.types import Message

# Replace these with your own values
API_ID =15191874 
API_HASH = "3037d39233c6fad9b80d83bb8a339a07" 
BOT_TOKEN = "7727908791:AAHUDR2RyXynqjnTgGkeN1zOHf79GanWCqk"  
IMAGE_DIR = '/www/wwwroot/Jnmovies.site/wp-content/uploads'

# Ensure the directory exists
os.makedirs(IMAGE_DIR, exist_ok=True)

app = Client("image_host_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.photo)
async def handle_image(client: Client, message: Message):
    # Download the image
    file_path = await message.download(file_name=os.path.join(IMAGE_DIR, f"{message.photo.file_id}.jpg"))
    
    # Construct the URL (assuming your domain is correctly set up)
    image_url = f"https://Jnmovies.site/wp-content/uploads/{os.path.basename(file_path)}"
    
    # Send the URL back to the user
    await message.reply_text(f"Here is your image link: {image_url}")

print("Bot is running...")
app.run()