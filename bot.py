import os
from pyrogram import Client, filters
from pyrogram.types import Message
import re

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


import requests
from bs4 import BeautifulSoup
import re
import os

# Directory for saving IMDb posters
IMDB_POSTER_DIR = '/www/wwwroot/Jnmovies.site/screenshots/'
os.makedirs(IMDB_POSTER_DIR, exist_ok=True)

@app.on_message(filters.text & filters.regex(r'https?://www\.imdb\.com/title/'))
async def handle_imdb_link(client: Client, message: Message):
    try:
        # Extract IMDb link from the message
        imdb_url = message.text

        # Fetch the IMDb page
        response = requests.get(imdb_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Scrape the movie title and year
        title_element = soup.find('meta', property='og:title')
        if not title_element:
            await message.reply_text("Could not find the title for this IMDb link.")
            return

        title_data = title_element['content']  # Format: "Movie Title (Year) - IMDb"
        title_match = re.match(r"(.+?) \((\d{4})\)", title_data)
        if not title_match:
            await message.reply_text("Could not extract title and year from the IMDb link.")
            return

        title = title_match.group(1).strip().replace(" ", "_")  # Replace spaces with underscores
        year = title_match.group(2)

        # Scrape the poster image URL
        poster_element = soup.find('meta', property='og:image')
        if not poster_element:
            await message.reply_text("Could not find the poster for this IMDb link.")
            return

        poster_url = poster_element['content']

        # Create the filename
        filename = f"{title}_{year}.jpg"
        poster_path = os.path.join(IMDB_POSTER_DIR, filename)

        # Check if the file already exists
        if os.path.exists(poster_path):
            image_url = f"https://Jnmovies.site/screenshots/{filename}"
            await message.reply_text(f"Here is the poster image: {image_url}")
            return

        # Download the poster image
        poster_response = requests.get(poster_url)
        with open(poster_path, 'wb') as f:
            f.write(poster_response.content)

        # Construct the image URL
        image_url = f"https://Jnmovies.site/screenshots/{filename}"

        # Send the image link back to the user
        await message.reply_text(f"Here is the poster image: {image_url}")

    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

print("Bot is running...")
app.run()