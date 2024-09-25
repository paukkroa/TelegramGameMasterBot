from telegram import Update
from telegram.ext import ContextTypes

class Game:
    def __init__(self, name: str, id: int, player_ids: list, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.name = name
        self.id = id
        self.player_ids = player_ids
        self.update = update
        self.context = context

    async def start(self):
        await self.update.message.reply_text(f"Let's play {self.name}!")


