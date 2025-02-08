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
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": "BTCUSDT", "interval": "1h", "limit": 1}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # 檢查請求是否成功
        data = response.json()
        logging.info(f"Received data: {data}")

        if data:
            high_price = float(data[0][2])
            low_price = float(data[0][3])
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

        if low_price is not None:
            channel2 = guild.get_channel(CHANNEL_ID2)
            if channel2:
                new_name = f"BTC Low (1h): ${low_price}"
                logging.info(f"Updating channel 2 name: {new_name}")
                try:
                    await channel2.edit(name=new_name)
                except Exception as e:
                    logging.error(f"Error updating channel 2 name: {e}")

    await client.close()


client.run(TOKEN)
