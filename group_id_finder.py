from telethon.sync import TelegramClient
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
phone_number = os.getenv("PHONE_NUMBER")

client = TelegramClient('session_name', api_id, api_hash)

conn = sqlite3.connect('telegram.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY,
    title TEXT
)
''')

conn.commit()

def save_group(group_id, title):
    cursor.execute('SELECT id FROM groups WHERE id = ?', (group_id,))
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO groups (id, title) VALUES (?, ?)', (group_id, title))
        conn.commit()

def list_groups():
    with client:
        for dialog in client.iter_dialogs():
            if dialog.is_group:
                save_group(dialog.id, dialog.title)
                print(f"{dialog.name} — {dialog.id}")

list_groups()
