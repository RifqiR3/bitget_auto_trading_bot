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

    # Normalize bullet characters and extra spaces
    text = re.sub(r'[•●]', '•', text)  # normalize bullets
    text = re.sub(r'\s+', ' ', text)  # normalize all whitespace to single spaces

    result['direction'] = 'LONG' if 'LONG' in text else 'SHORT' if 'SHORT' in text else None

    symbol_match = re.search(r'\$([A-Z]+)', text)
    entry_match = re.search(r'ENTRY\s*•\s*([\d.]+)', text)
    leverage_match = re.search(r'LEVERAGE\s*•\s*(\d+X)', text)
    sl_match = re.search(r'SL\s*•\s*([\d.]+)', text)
    tp1_match = re.search(r'TP\s*1\s*•\s*([\d.]+)', text)
    tp2_match = re.search(r'TP\s*2\s*•\s*([\d.]+)', text)

    result['symbol'] = symbol_match.group(1) if symbol_match else None
    result['entry'] = entry_match.group(1) if entry_match else None
    result['leverage'] = leverage_match.group(1) if leverage_match else None
    result['sl'] = sl_match.group(1) if sl_match else None
    result['tp1'] = tp1_match.group(1) if tp1_match else None
    result['tp2'] = tp2_match.group(1) if tp2_match else None

    return result

client.start()
print("Listening to Telegram messages....")
client.run_until_disconnected()
