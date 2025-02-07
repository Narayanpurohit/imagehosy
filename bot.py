
# Directory to save the downloaded images
import os
import requests
from pyrogram import Client, filters
from cinemagoer import IMDb  # CinemaPy (IMDbPY fork)

API_ID = int(os.getenv("API_ID", "15191874"))
API_HASH = os.getenv("API_HASH", "3037d39233c6fad9b80d83bb8a339a07")
BOT_TOKEN = os.getenv("BOT_TOKEN", "6677023637:AAES7_yErqBDZY7wQP1EOyIGhpAN1d9fY5o")

# Directory to save the downloaded images
DOWNLOAD_DIR = "/www/wwwroot/Jnmovies.site/wp-content/uploads/"

# Ensure the directory exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Initialize the Pyrogram client
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Initialize IMDb
ia = IMDb()

# Function to download an image from a URL
def download_image(url, file_name):
    response = requests.get(url)
    if response.status_code == 200:
        file_path = os.path.join(DOWNLOAD_DIR, file_name)
        with open(file_path, "wb") as file:
            file.write(response.content)
        return file_path
    return None

# Function to extract IMDb movie ID from URL
def extract_imdb_id(url):
    if "imdb.com/title/tt" in url:
        return url.split("tt")[1].split("/")[0]
    return None

# Handler for messages containing an IMDb link
@app.on_message(filters.text & filters.private)
async def handle_message(client, message):
    url = message.text.strip()
    imdb_id = extract_imdb_id(url)
    if imdb_id:
        # Fetch movie details using IMDb
        movie = ia.get_movie(imdb_id)
        if movie:
            # Get movie title and poster URL
            title = movie.get("title", "unknown_title").replace(" ", "_").replace("/", "_")
            poster_url = movie.get("full-size cover url", movie.get("cover url"))
            if poster_url:
                # Download the poster
                file_name = f"{title}.jpg"
                file_path = download_image(poster_url, file_name)
                if file_path:
                    # Send the poster back to the user
                    await message.reply_photo(file_path, caption=f"Poster for: {movie.get('title')}")
                    os.remove(file_path)  # Clean up the file
                else:
                    await message.reply_text("Failed to download the poster. Please try again.")
            else:
                await message.reply_text("No poster found for this movie.")
        else:
            await message.reply_text("Failed to fetch movie details. Please check the IMDb link.")
    else:
        await message.reply_text("Please send a valid IMDb link.")

# Start the bot
print("Bot is running...")
app.run()