from telethon import TelegramClient, events
from dotenv import load_dotenv
import os
import re

load_dotenv()

api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
channel_id = -4736754644

client = TelegramClient('bitget_session', api_id, api_hash)

@client.on(events.NewMessage(chats=channel_id))
async def handler(event):
    sender = await event.get_sender()
    message = event.raw_text

    print(f"\nMessage from {sender.username or sender.id}: \n{message}\n")

    #Filter pesan tidak nyambung
    if any(word in message.upper() for word in ['LONG', 'SHORT', 'ENTRY', 'TP']):
        parsed = parse_signal(message)
        parsed['symbol'] = parsed['symbol'].upper() + "USDT"
        print("Parsed Signal:", parsed)

def parse_signal(text):
    result = {}
    text = text.upper()

    #Regex
    result['direction'] = 'LONG' if 'LONG' in text else 'SHORT' if 'SHORT' in text else None
    result['symbol'] = re.search(r'\$([A-Z]+)', text)
    result['entry'] = re.search(r'ENTRY\s*●?\s*([\d\-.–]+)', text)
    result['leverage'] = re.search(r'LEVERAGE\s*●?\s*(\d+X)', text)
    result['sl'] = re.search(r'SL\s*●?\s*([\d.]+)', text)
    result['tp1'] = re.search(r'TP1\s*●?\s*([\d.]+)', text)
    result['tp2'] = re.search(r'TP2\s*●?\s*([\d.]+)', text)
    # Add more as you much as you need
    # result['tp3'] = re.search(r'TP3\s*●?\s*([\d.]+)', text)
    # result['tp4'] = re.search(r'TP4\s*●?\s*([\d.]+)', text)
    # result['tp5'] = re.search(r'TP5\s*●?\s*([\d.]+)', text)

    for key, match in result.items():
        if hasattr(match, 'group'): 
            result[key] = match.group(1)
    
    return result

client.start()
print("Listening to Telegram messages....")
client.run_until_disconnected()