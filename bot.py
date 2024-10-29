from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from datetime import datetime, timedelta
import json
import os

# Замените 'YOUR_TELEGRAM_BOT_TOKEN' на ваш новый токен
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

user_tokens = {}
user_last_claim = {}

def save_data():
    with open('data.json', 'w') as f:
        json.dump({
            'user_tokens': user_tokens,
            'user_last_claim': user_last_claim
        }, f)

def load_data():
    global user_tokens, user_last_claim
    if os.path.exists('data.json'):
        with open('data.json', 'r') as f:
            data = json.load(f)
            user_tokens = data.get('user_tokens', {})
            user_last_claim = data.get('user_last_claim', {})
    else:
        user_tokens = {}
        user_last_claim = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Открыть игру", web_app=WebAppInfo(url="https://your-web-app-url.com"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Добро пожаловать в игру по фарму токенов.", reply_markup=reply_markup)

async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.message.web_app_data.data  # Получаем данные от Web App
    user_id = str(update.effective_user.id)

    if data == 'farm':
        tokens = user_tokens.get(user_id, 0)
        tokens += 10
        user_tokens[user_id] = tokens
        save_data()
        await update.message.reply_text(f"Вы получили 10 токенов! Всего у вас {tokens} токенов.")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    tokens = user_tokens.get(user_id, 0)
    await update.message.reply_text(f"У вас {tokens} токенов.")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sorted_users = sorted(user_tokens.items(), key=lambda x: x[1], reverse=True)
    message = "🏆 Лидерборд:\n"
    for user_id, tokens in sorted_users[:10]:
        try:
            user = await context.bot.get_chat(int(user_id))
            message += f"{user.first_name}: {tokens} токенов\n"
        except Exception:
            message += f"Пользователь {user_id}: {tokens} токенов\n"
    await update.message.reply_text(message)

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    now = datetime.now()
    last_claim_str = user_last_claim.get(user_id)
    if last_claim_str:
        last_claim = datetime.fromisoformat(last_claim_str)
        if now - last_claim < timedelta(days=1):
            await update.message.reply_text("Вы уже получили ежедневный бонус. Приходите завтра!")
            return
    user_tokens[user_id] = user_tokens.get(user_id, 0) + 50
    user_last_claim[user_id] = now.isoformat()
    save_data()
    await update.message.reply_text("Вы получили ежедневный бонус в размере 50 токенов!")

def main():
    load_data()
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('balance', balance))
    application.add_handler(CommandHandler('leaderboard', leaderboard))
    application.add_handler(CommandHandler('daily', daily))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))

    application.run_polling()

if __name__ == '__main__':
    main()
