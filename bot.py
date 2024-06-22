import os
import logging
import discord
import pandas as pd
from ta.momentum import RSIIndicator
from discord.ext import commands
from pybit.unified_trading import HTTP
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import asyncio

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")

# Validate environment variables
if TOKEN is None:
    logger.error("DISCORD_BOT_TOKEN environment variable not set")
if CHANNEL_ID is None:
    logger.error("CHANNEL_ID environment variable not set")
if BYBIT_API_KEY is None:
    logger.error("BYBIT_API_KEY environment variable not set")
if BYBIT_API_SECRET is None:
    logger.error("BYBIT_API_SECRET environment variable not set")

CHANNEL_ID = int(CHANNEL_ID)

# Initialize Discord bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize Bybit session
session = HTTP(testnet=False, api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET)

SYMBOL = "SOLUSDT"
INTERVAL = "60"  # 1 hour time frame


def fetch_kline_data():
    response = session.get_kline(category="spot", symbol=SYMBOL, interval=INTERVAL)
    if response["retCode"] == 0:
        return response["result"]
    else:
        logger.error(f"Error fetching Kline data: {response['retMsg']}")
        return None


def calculate_rsi(data):
    if data is None:
        return None
    df = pd.DataFrame(data["list"])
    df.columns = ["start_time", "open", "high", "low", "close", "volume", "turnover"]
    df["close"] = df["close"].astype(float)
    rsi_indicator = RSIIndicator(df["close"], window=14)
    df["rsi"] = rsi_indicator.rsi()
    return df.iloc[-1]["rsi"]


async def check_rsi():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        logger.error(f"Channel with ID {CHANNEL_ID} not found")
        return

    data = fetch_kline_data()
    if data is None:
        logger.error("Failed to fetch Kline data.")
        return

    rsi = calculate_rsi(data)
    if rsi is None:
        logger.error("Failed to calculate RSI.")
        return

    logger.info(f"RSI: {rsi}")

    if rsi > 70:
        await channel.send(f"RSI Alert! RSI is over 70: {rsi}")
    elif rsi < 30:
        await channel.send(f"RSI Alert! RSI is below 30: {rsi}")


async def wait_until_next_bar_close():
    now = datetime.now(timezone.utc)
    next_close = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    wait_seconds = (next_close - now).total_seconds() + 1
    logger.info(f"Waiting for {wait_seconds} seconds until next bar close.")
    await asyncio.sleep(wait_seconds)


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")
    while True:
        await wait_until_next_bar_close()
        await check_rsi()


# Start the bot
bot.run(TOKEN)
