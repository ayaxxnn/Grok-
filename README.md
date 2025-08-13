# Aizen Bot

A Telegram bot with admin controls and premium features.

## Setup
1. Create a bot via @BotFather and get the token.
2. Get your Telegram user ID (e.g., via @userinfobot).
3. Create `.env` file with:
4. Install dependencies: `pip install -r requirements.txt`
5. Run locally: `python main.py`
6. Deploy to Render:
- Create a new Web Service.
- Set Build Command: `pip install -r requirements.txt`
- Set Start Command: `python main.py`
- Add environment variables in Render dashboard.

## Features
- `/start`: Welcome message.
- `/redeem`: Free users (1 time), premium (unlimited).
- `/premium <key>`: Activate premium with admin-generated key.
- Admin: `/genk <days>`, `/broadcast <msg>`, `/ban <user_id>`, `/unban <user_id>`, `/reply <user_id> <msg>`, `/on`, `/off`.
