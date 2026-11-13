# Telegram Grocery Order Bot

A simple Telegram bot where customers pick items from a menu, review their cart, and place an order. Orders are saved in SQLite.

## Features
- /start or /menu: shows the product menu with inline buttons
- Add items to a cart with one tap
- View Cart: shows items, quantities and total
- Place Order: saves the order to SQLite and returns an order number

## Setup
1. Install: pip install -r requirements.txt
2. Copy .env.example to .env and set TELEGRAM_TOKEN (from @BotFather)
3. Run: python bot.py

## Security
- The bot token is read from .env, which is git-ignored
- The orders database (orders.db) is git-ignored
- Never commit tokens or real customer data
