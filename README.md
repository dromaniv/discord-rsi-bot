# Discord RSI Bot

This Discord bot fetches SOL/USDT spot K-line data from Bybit, calculates the RSI, and sends notifications to a Discord channel if the RSI value is over 70 or below 30.

## Requirements

- Docker

## Setup

1. Clone the repository:
    ```sh
    git clone https://github.com/dromaniv/discord-rsi-bot.git
    cd discord-rsi-bot
    ```

2. Create a `.env` file in the root directory and add your environment variables:
    ```env
    DISCORD_BOT_TOKEN=your_discord_bot_token
    CHANNEL_ID=your_channel_id
    BYBIT_API_KEY=your_bybit_api_key
    BYBIT_API_SECRET=your_bybit_api_secret
    ```

3. Build and run the Docker container:
    ```sh
    docker build -t discord-rsi-bot .
    docker run -d --env-file .env discord-rsi-bot
    ```