from telegram import Update
from telegram.ext import ContextTypes
from utils import get_username_by_id

class Waitlist:
    def __init__(self, chat_id: int):
        self.player_ids = []
        self.chat_id = chat_id

    def add_player(self, player_id) -> bool:
        if player_id not in self.player_ids:
            self.player_ids.append(player_id)
            return True

        return False

    def remove_player(self, player_id) -> bool:
        if player_id not in self.player_ids:
            return False

        self.player_ids.remove(player_id)
        return True

    def clear(self) -> None:
        self.player_ids = []

    def get_chat_id(self) -> int:
        return self.chat_id

    async def list_players(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        message = f"Players on waitlist: \n"
        for id in self.player_ids:
            username = await get_username_by_id(id, context)
            message += f"\n{username}"

        await update.message.reply_text(message)
