from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from typing import Callable
import random
import sqlite3
import db

from games.Game import Game
from utils import get_username_by_id
class Waterfall(Game):

    def __init__(self, 
                 id: int, 
                 player_ids: list, 
                 update: Update, 
                 context: ContextTypes.DEFAULT_TYPE,
                 is_part_of_tournament: bool = False, 
                 start_next_game: Callable[[], None] = None,
                 sql_connection: sqlite3.Connection = db.connect(), 
                 session_id: int = None, 
                 bot_tg_id: str = None):
        super().__init__(name="Waterfall", 
                         id=id, 
                         player_ids=player_ids, 
                         update=update, 
                         context=context,
                         is_part_of_tournament=is_part_of_tournament, 
                         start_next_game=start_next_game,
                         sql_connection=sql_connection, 
                         session_id=session_id, 
                         bot_tg_id=bot_tg_id)

    async def start(self):
        random_player_id = random.sample(self.player_ids, 1)[0]
        username = await get_username_by_id(random_player_id, self.context)
        await self.send_group_chat(f"Let's play Waterfall! {username} starts. Send /done when you've played it.")

        self.handlers.append(CommandHandler("done", self.end))
        self.add_handlers()


    async def end(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.send_group_chat("Waterfall ended.")
        self.remove_handlers()

        if self.is_part_of_tournament:
            await self.start_next_game()