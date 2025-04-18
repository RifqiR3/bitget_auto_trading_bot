from telethon.sync import TelegramClient
from dotenv import load_dotenv
import os

load_dotenv()

api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")

client = TelegramClient('bitget_session', api_id, api_hash)
client.start()

dialogs = client.get_dialogs()
# print(dialogs)

for dialog in dialogs:
    if dialog.is_group:
        print(f"Channel: {dialog.name} | ID: {dialog.id}") 
