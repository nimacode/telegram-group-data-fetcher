import sqlite3
import asyncio
import time
from InquirerPy import inquirer
from telethon.sync import TelegramClient
from telethon.errors import FloodWaitError
import os
from dotenv import load_dotenv

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
phone_number = os.getenv("PHONE_NUMBER")

conn = sqlite3.connect('telegram.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY,
    title TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER,
    group_id INTEGER,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    phone TEXT,
    PRIMARY KEY (id, group_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS state (
    key TEXT PRIMARY KEY,
    value TEXT
)
''')
conn.commit()


def save_group(group_id, title):
    cursor.execute('SELECT id FROM groups WHERE id = ?', (group_id,))
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO groups (id, title) VALUES (?, ?)', (group_id, title))
        conn.commit()

def save_user(user):
    # cursor.execute('SELECT id FROM users WHERE id = ? AND group_id = ?', (user['id'], user['group_id']))
    cursor.execute('SELECT id FROM users WHERE id = ?', (user['id'],))
    if cursor.fetchone() is None:
        cursor.execute('''
        INSERT INTO users (id, group_id, username, first_name, last_name, phone)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user['id'],
            user['group_id'],
            user['username'],
            user['first_name'],
            user['last_name'],
            user['phone']
        ))
        conn.commit()

def get_oldest_message_id(group_id):
    key = f'oldest_message_id_{group_id}'
    cursor.execute("SELECT value FROM state WHERE key = ?", (key,))
    row = cursor.fetchone()
    return int(row[0]) if row else None

def update_oldest_message_id(msg_id, group_id):
    key = f'oldest_message_id_{group_id}'
    cursor.execute("INSERT OR REPLACE INTO state (key, value) VALUES (?, ?)", (key, str(msg_id)))
    conn.commit()

async def fetch_groups():
    async with TelegramClient('session_name', api_id, api_hash) as client:
        await client.start(phone=phone_number)
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                save_group(dialog.id, dialog.title)
        print("Groups fetched and saved to database.")

def list_groups_from_db():
    cursor.execute("SELECT id, title FROM groups")
    return cursor.fetchall()

async def fetch_messages(group_id):
    async with TelegramClient('session_name', api_id, api_hash) as client:
        await client.start(phone=phone_number)
        print(f"Start Fetch Group Messages {group_id}...")

        while True:
            try:
                oldest_id = get_oldest_message_id(group_id)
                batch_size = 1000

                if oldest_id:
                    messages = client.iter_messages(group_id, limit=batch_size, max_id=oldest_id)
                else:
                    messages = client.iter_messages(group_id, limit=batch_size)

                count = 0
                async for message in messages:
                    if not message.message or not message.sender_id:
                        continue

                    sender = await message.get_sender()
                    if sender and hasattr(sender, 'username') and sender.username and hasattr(sender, 'first_name'):
                        user_data = {
                            'id': sender.id,
                            'group_id': group_id,
                            'username': sender.username,
                            'first_name': sender.first_name,
                            'last_name': sender.last_name,
                            'phone': getattr(sender, 'phone', None)
                        }
                        save_user(user_data)
                        update_oldest_message_id(message.id, group_id)
                        count += 1

                if count == 0:
                    print("Message Finished!")
                    break

                print("Waiting for 5 seconds before next batch...")
                time.sleep(5)

            except FloodWaitError as e:
                print(f"⛔️ FloodWait! We need to wait for {e.seconds} seconds...")
                time.sleep(e.seconds + 5)

async def main():
    await fetch_groups()

    groups = list_groups_from_db()
    if not groups:
        print("Group not found!")
        return

    selected = await inquirer.select(
        message="✅ Select Group",
        choices=[{"name": f"{title} ({group_id})", "value": group_id} for group_id, title in groups],
        pointer="👉",
        instruction="Select group to fetch messages with arrow keys",
    ).execute_async()

    await fetch_messages(selected)

if __name__ == "__main__":
    asyncio.run(main())
