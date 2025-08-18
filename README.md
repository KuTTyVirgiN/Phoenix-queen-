# Phoenix-queen-
Unlimited entertainment word guessing game
# 🐙 Octopus Bot (Telegram)

A simple Tamil guessing game bot for Telegram using `python-telegram-bot`.

## Commands
- `/start` – start the bot
- `/play` – ask a question

## Run locally
1. `pip install -r requirements.txt`
2. Set env var `BOT_TOKEN=<your-telegram-botfather-token>`
3. `python bot.py`

## Deploy on Railway
- Add project from GitHub
- Add Variable: `BOT_TOKEN`
- Procfile defines a worker: `python bot.py`
