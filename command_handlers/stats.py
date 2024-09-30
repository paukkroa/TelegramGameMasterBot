from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def get_player_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton('Tournament', callback_data='stats:player_session'),
            InlineKeyboardButton('All-time', callback_data='stats:player_alltime')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Options: ', reply_markup=reply_markup)


async def get_group_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton('Tournament', callback_data='stats:group_session'),
            InlineKeyboardButton('All-time', callback_data='stats:group_alltime')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Options: ', reply_markup=reply_markup)


async def get_session_ranking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton('Points', callback_data='ranking:session_points'),
            InlineKeyboardButton('Drinks', callback_data='ranking:session_drinks')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Options: ', reply_markup=reply_markup)


async def get_all_time_ranking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton('Points', callback_data='ranking:alltime_points'),
            InlineKeyboardButton('Drinks', callback_data='ranking:alltime_drinks'),
            InlineKeyboardButton('Games', callback_data='ranking:alltime_games'),
            InlineKeyboardButton('Tournaments', callback_data='ranking:alltime_tournaments')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Options: ', reply_markup=reply_markup)
