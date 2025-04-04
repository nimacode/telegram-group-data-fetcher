# 🧑‍💻 Telegram Group Scraper CLI

A Python CLI tool that uses [Telethon](https://github.com/LonamiWebs/Telethon) to:

- Fetch your Telegram group list
- Let you interactively select a group via arrow keys
- Extract users by scanning chat messages
- Store everything in a local SQLite database

---

## 🚀 Features

- Extracts real users with `username`
- Backward pagination (from newest to oldest messages)
- Saves: `user_id`, `group_id`, `username`, `first_name`, `last_name`, `phone`
- Tracks progress using a `state` table (so you can resume)
- Interactive CLI menu to choose the group (arrow key support)
- Handles Telegram rate limits (`FloodWait`)

---

## 🧰 Requirements

- Python 3.7+
- A Telegram account
- Your Telegram API credentials from [my.telegram.org](https://my.telegram.org)

---

## ⚙️ Installation

1. Clone the repo:

```bash
git clone https://github.com/nimacode/telegram-group-data-fetcher.git
cd telegram-group-data-fetcher
```

2. Set up a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a .env file with your Telegram credentials:

```bash
API_ID=your_api_id
API_HASH=your_api_hash
PHONE_NUMBER=your_phone_number
```

▶️ Usage

```bash
python main.py
```
🗃️ Database Structure
* groups: Stores group titles and IDs
* users: All extracted users per group
* state: Keeps track of the last scanned message for each group

📦 Output
All data is stored locally in telegram.db and can be exported or analyzed however you like (e.g., to CSV or Excel).

📝 License
MIT License

Built with ❤️ by nimacode