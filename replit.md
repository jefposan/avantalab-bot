# Avantalab Bot

## Overview
This is a Python Telegram bot that logs all incoming messages to a CSV file. The bot listens for text messages and commands, recording the timestamp, user ID, username, and message content.

## Project Structure
- `telegram_bot.py` - Main bot application
- `dados.csv` - CSV file storing message logs
- `requirements.txt` - Python dependencies

## Recent Changes
- **2025-11-05**: Initial Replit setup
  - Installed Python 3.11 and dependencies
  - Configured TELEGRAM_TOKEN secret
  - Set up workflow to run the bot
  - Added .gitignore for Python projects
  - Created documentation

## Dependencies
- `python-telegram-bot==13.15` - Telegram bot framework

## Environment Variables
- `TELEGRAM_TOKEN` - Required. Bot token from @BotFather on Telegram

## How It Works
1. The bot connects to Telegram using the provided token
2. It listens for all text messages and commands
3. Each message is logged to `dados.csv` with:
   - Timestamp (UTC)
   - User ID
   - Username (or full name if username not set)
   - Message text

## Running the Bot
The bot runs automatically via the `telegram-bot` workflow. It uses polling to receive updates from Telegram.

## Important Notes
- Only one instance of the bot can run at a time with the same token
- If you see a "Conflict" error, make sure no other instances are running elsewhere
- The CSV file grows over time - consider periodic backups or cleanup
- The bot logs all messages it receives, so ensure proper data privacy practices

## Deployment
This bot is configured to run as a VM deployment since it needs to maintain a persistent connection to Telegram's servers.
