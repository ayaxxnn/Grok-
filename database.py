# database.py
import sqlite3
from datetime import datetime, timedelta

def init_db():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    # Users table: tracks user status and redeem usage
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        is_premium INTEGER DEFAULT 0,
        premium_expiry TEXT,
        redeem_used INTEGER DEFAULT 0
    )''')
    # Keys table: stores admin-generated keys
    c.execute('''CREATE TABLE IF NOT EXISTS keys (
        key TEXT PRIMARY KEY,
        days INTEGER,
        used INTEGER DEFAULT 0
    )''')
    # Bans table: tracks banned users
    c.execute('''CREATE TABLE IF NOT EXISTS bans (
        user_id INTEGER PRIMARY KEY
    )''')
    # Settings table: stores unlimited redeem mode
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value INTEGER
    )''')
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('unlimited_redeem', 0)")
    conn.commit()
    conn.close()

def is_user_premium(user_id):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT is_premium, premium_expiry FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    if result and result[0] == 1:
        expiry = datetime.strptime(result[1], "%Y-%m-%d %H:%M:%S")
        if datetime.now() < expiry:
            return True
        else:
            # Premium expired
            conn = sqlite3.connect("bot.db")
            c.execute("UPDATE users SET is_premium = 0, premium_expiry = NULL WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
    return False

def has_used_redeem(user_id):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT redeem_used FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def set_redeem_used(user_id):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (user_id, redeem_used) VALUES (?, 1)", (user_id,))
    conn.commit()
    conn.close()

def activate_premium(user_id, days):
    expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("UPDATE users SET is_premium = 1, premium_expiry = ? WHERE user_id = ?", (expiry, user_id))
    conn.commit()
    conn.close()

def generate_key(days):
    import uuid
    key = str(uuid.uuid4())
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("INSERT INTO keys (key, days, used) VALUES (?, ?, 0)", (key, days))
    conn.commit()
    conn.close()
    return key

def validate_key(key):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT days, used FROM keys WHERE key = ?", (key,))
    result = c.fetchone()
    if result and result[1] == 0:
        c.execute("UPDATE keys SET used = 1 WHERE key = ?", (key,))
        conn.commit()
        conn.close()
        return result[0]  # Return number of days
    conn.close()
    return None

def ban_user(user_id):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO bans (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def unban_user(user_id):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("DELETE FROM bans WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def is_banned(user_id):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT user_id FROM bans WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result is not None

def set_unlimited_redeem(status):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("UPDATE settings SET value = ? WHERE key = 'unlimited_redeem'", (status,))
    conn.commit()
    conn.close()

def is_unlimited_redeem():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = 'unlimited_redeem'")
    result = c.fetchone()
    conn.close()
    return result[0] == 1