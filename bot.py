import discord
import requests
import os
import logging
from dotenv import load_dotenv

# 設置 logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
CHANNEL_ID1 = int(os.getenv("CHANNEL_ID1"))
CHANNEL_ID2 = int(os.getenv("CHANNEL_ID2"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)


def get_bitcoin_price():
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


@client.event
async def on_ready():
    logging.info(f"Logged in as {client.user}")
    guild = client.get_guild(GUILD_ID)

    if guild:
        logging.info(f"Server name: {guild}")

        high_price, low_price = get_bitcoin_price()

        if high_price is not None:
            channel1 = guild.get_channel(CHANNEL_ID1)
            if channel1:
                new_name = f"BTC High (1h): ${high_price}"
                logging.info(f"Updating channel 1 name: {new_name}")
                try:
                    await channel1.edit(name=new_name)
                except Exception as e:
                    logging.error(f"Error updating channel 1 name: {e}")
                try:
                    await channel1.send(f"Updated BTC High (1h): ${high_price}")
                except Exception as e:
                    logging.error(f"Error sending message to channel 1: {e}")

        if low_price is not None:
            channel2 = guild.get_channel(CHANNEL_ID2)
            if channel2:
                new_name = f"BTC Low (1h): ${low_price}"
                logging.info(f"Updating channel 2 name: {new_name}")
                try:
                    await channel2.edit(name=new_name)
                except Exception as e:
                    logging.error(f"Error updating channel 2 name: {e}")
                try:
                    await channel2.send(f"Updated BTC Low (1h): ${low_price}")
                except Exception as e:
                    logging.error(f"Error sending message to channel 2: {e}")

    await client.close()


client.run(TOKEN)
