from telegram import Update
from telegram.ext import ContextTypes
from typing import Callable

class Game:
    def __init__(self, name: str, id: int, player_ids: list, update: Update, context: ContextTypes.DEFAULT_TYPE,
                 is_part_of_tournament: bool = False, start_next_game: Callable[[], None] = None):
        self.name = name
        self.id = id
        self.player_ids = player_ids
        self.is_part_of_tournament = is_part_of_tournament
        self.update = update
        self.context = context
        self.start_next_game = start_next_game

    async def start(self):
        await self.update.message.reply_text(f"Let's play {self.name}!")


