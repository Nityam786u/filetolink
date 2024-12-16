import os
import logging
from flask import Flask, send_from_directory, jsonify
from pyrogram import Client, filters

# Logging configuration
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Bot configuration
API_ID = 27174510  # Replace with your API_ID
API_HASH = "8f99458e1569ef46e27ff4ffdbe2bdec"  # Replace with your API_HASH
BOT_TOKEN = "7970190380:AAH6ynCRC2vk-ocdXe7jkI553Vh-eTYtYvY"
DOWNLOADS_DIR = "./downloads"  # Directory to save downloaded files
WEB_SERVER_HOST = "192.168.29.152"  # Public-facing host
WEB_SERVER_PORT = 8080  # Port for the web server

# Flask web server
app = Flask(__name__)

# Create downloads directory if it doesn't exist
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Pyrogram bot instance
bot = Client("file_to_link_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    """Serve the file via HTTP."""
    file_path = os.path.join(DOWNLOADS_DIR, filename)
    if os.path.exists(file_path):
        return send_from_directory(DOWNLOADS_DIR, filename, as_attachment=True)
    else:
        LOGGER.error(f"File not found: {filename}")
        return jsonify({"error": "File not found"}), 404


@bot.on_message(filters.document | filters.video | filters.audio | filters.photo)
def handle_file(client, message):
    """Handle user-uploaded files and generate download links."""
    try:
        LOGGER.info("Processing file upload...")

        # Synchronously download the file
        file_name = message.download(file_name=DOWNLOADS_DIR)
        LOGGER.info(f"File downloaded to: {file_name}")

        # Generate download link
        if file_name:
            file_basename = os.path.basename(file_name)
            download_url = f"http://{WEB_SERVER_HOST}:{WEB_SERVER_PORT}/download/{file_basename}"
            message.reply_text(f"Your download link: {download_url}")
            LOGGER.info(f"Download link sent: {download_url}")
        else:
            message.reply_text("Failed to download the file. Please try again.")
    except Exception as e:
        LOGGER.error(f"Error while processing file: {e}")
        message.reply_text("An error occurred while processing your file.")


def main():
    """Start the bot and the web server."""
    # Start the web server in a separate thread
    from threading import Thread

    def run_web_server():
        LOGGER.info(f"Starting web server at http://{WEB_SERVER_HOST}:{WEB_SERVER_PORT}/")
        app.run(host=WEB_SERVER_HOST, port=WEB_SERVER_PORT, debug=False)

    web_thread = Thread(target=run_web_server)
    web_thread.daemon = True
    web_thread.start()

    # Start the bot
    LOGGER.info("Starting Telegram bot...")
    bot.run()


if __name__ == "__main__":
    main()
