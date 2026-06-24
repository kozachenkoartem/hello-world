#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Проверяем .env
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "⚠️  .env not found. Copying from .env.example..."
        cp .env.example .env
        echo "❌ Please set BOT_TOKEN in .env and run again."
        exit 1
    else
        echo "❌ .env file is required. Create it with:"
        echo "   BOT_TOKEN=your_telegram_bot_token_here"
        exit 1
    fi
fi

# Экспортируем переменные из .env
export $(grep -v '^\s*#' .env | grep -v '^\s*$' | xargs)

echo "🔨 Building Docker image..."
docker compose build

echo "🚀 Starting bot..."
docker compose up -d

echo "✅ Bot is running in the background."
echo "   Check logs with: docker compose logs -f"
