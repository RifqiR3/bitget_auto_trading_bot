from telethon import TelegramClient, events
from dotenv import load_dotenv
from bitget_order_execute import execute_trade
import os
import re
import json

load_dotenv()

api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
channel_id = -1002635215988

client = TelegramClient('bitget_session', api_id, api_hash)

@client.on(events.NewMessage(chats=channel_id))
async def handler(event):
    sender = await event.get_sender()
    message = event.raw_text

    print(f"\nMessage from {sender.username or sender.id}: \n{message}\n")

    # Filter valid signal messages
    if any(word in message.upper() for word in ['LONG', 'SHORT', 'SPOT', 'ENTRY', 'TP']):
        parsed = parse_signal(message)
        if all([parsed["direction"], parsed["symbol"], parsed["entry"], parsed["leverage"], parsed["sl"], parsed["tp2"]]):
            parsed['symbol'] = parsed['symbol'].upper()
            print("✅ Parsed Signal:", parsed)
            execute_trade(parsed)
        else:
            print("⚠️ Incomplete signal, skipping:", parsed)

def parse_signal(text):
    result = {}
    text = text.upper()
    text = re.sub(r'[•●]', '•', text)
    text = re.sub(r'\s+', ' ', text)

    if 'LONG' in text:
        result['direction'] = 'LONG'
    elif 'SHORT' in text:
        result['direction'] = 'SHORT'
    elif 'SPOT' in text:
        result['direction'] = 'LONG'
    else:
        result['direction'] = None

    symbol_match = re.search(r'\$([A-Z0-9]+)', text)
    entry_match = re.search(r'ENTRY\s*•\s*([\d.]+)', text)
    leverage_match = re.search(r'LEVERAGE\s*•\s*(\d+X)', text)
    sl_match = re.search(r'SL\s*•\s*([\d.]+)', text)
    tp1_match = re.search(r'TP\s*1\s*•\s*([\d.]+)', text)
    tp2_match = re.search(r'TP\s*2\s*•\s*([\d.]+)', text)

    result['symbol'] = symbol_match.group(1) if symbol_match else None
    result['entry'] = entry_match.group(1) if entry_match else None
    result['leverage'] = leverage_match.group(1) if leverage_match else "20X"
    result['sl'] = sl_match.group(1) if sl_match else None
    result['tp1'] = tp1_match.group(1) if tp1_match else None
    result['tp2'] = tp2_match.group(1) if tp2_match else None

    return result

client.start()
print("👂 Listening to Telegram messages....")
client.run_until_disconnected()
