import discord
import requests
import os
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
CHANNEL_TEST = int(os.getenv("CHANNEL_TEST"))
CHANNEL_ID1 = int(os.getenv("CHANNEL_ID1"))
CHANNEL_ID2 = int(os.getenv("CHANNEL_ID2"))
CHANNEL_ID3 = int(os.getenv("CHANNEL_ID3"))
CHANNEL_ID4 = int(os.getenv("CHANNEL_ID4"))
IMAGE_PATH = "at_reply.jpg"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def get_btc_price():
    url = "https://www.okx.com/api/v5/market/candles"
    params = {"instId": "BTC-USDT", "bar": "1m", "limit": 60}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if "data" in data and len(data["data"]) > 0:
            high_price = max(float(candle[2]) for candle in data["data"])
            low_price = min(float(candle[3]) for candle in data["data"]) 
            logging.info(f"{high_price}, {low_price}")
            return high_price, low_price
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching price: {e}")

    return None, None

async def update_channel(channel, name, message):
    try:
        await channel.edit(name=name)
        logging.info(f"Updated channel name: {name}")
    except Exception as e:
        logging.error(f"Error updating channel name: {e}")

    try:
        await channel.send(message)
        logging.info(f"Sent message: {message}")
    except Exception as e:
        logging.error(f"Error sending message to channel: {e}")

async def handle_mentions(channel):
    now = datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)

    try:
        async for message in channel.history(limit=100):
            message_time = message.created_at.replace(tzinfo=None)
            if message_time < one_hour_ago:
                break
            
            bot_member = message.guild.get_member(client.user.id)
            bot_roles = {role.id for role in bot_member.roles}
            mentioned_roles = {role.id for role in message.role_mentions}
            
            if client.user in message.mentions or bot_roles.intersection(mentioned_roles) or message.mention_everyone:
                logging.info(f"Found mention at: {message.created_at}")
                with open(IMAGE_PATH, "rb") as image_file:
                    await message.reply(file=discord.File(image_file, filename=IMAGE_PATH))
                    logging.info(f"Replied image: {IMAGE_PATH}")
                break
    except Exception as e:
        logging.error(f"Error checking message from channel: {e}")

@client.event
async def on_ready():
    logging.info(f"Logged in as {client.user}")
    guild = client.get_guild(GUILD_ID)

    if guild:
        logging.info(f"Server name: {guild}")
        
        channel_test = client.get_channel(CHANNEL_TEST)
        if channel_test:
            await handle_mentions(channel_test)

        channel3 = client.get_channel(CHANNEL_ID3)
        if channel3:
            await handle_mentions(channel3)
        # channel4 = client.get_channel(CHANNEL_ID4)
        # if channel4:
        #     await handle_mentions(channel4)

        high_price, low_price = get_btc_price()
        if high_price:
            channel1 = guild.get_channel(CHANNEL_ID1)
            if channel1:
                await update_channel(channel1, f"BTC High (1h): ${high_price}", f"Updated BTC High (1h): ${high_price}")
        if low_price:
            channel2 = guild.get_channel(CHANNEL_ID2)
            if channel2:
                await update_channel(channel2, f"BTC Low (1h): ${low_price}", f"Updated BTC Low (1h): ${low_price}")
        
    await client.close()

client.run(TOKEN)
