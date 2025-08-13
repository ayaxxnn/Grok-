# config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Set in .env
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # Your Telegram user ID