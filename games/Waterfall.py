from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from typing import Callable
import random

import db
from utils.helpers import get_username_by_id
from utils.logger import get_logger
from games.Game import Game

logger = get_logger(__name__)

class Waterfall(Game):

    def __init__(self, 
                 id: int, 
                 player_ids: list, 
                 update: Update, 
                 context: ContextTypes.DEFAULT_TYPE,
                 is_part_of_tournament: bool = False, 
                 start_next_game: Callable[[], None] = None,
                 session_id: str = None):
        super().__init__(name="Waterfall", 
                         id=id, 
                         player_ids=player_ids, 
                         update=update, 
                         context=context,
                         is_part_of_tournament=is_part_of_tournament, 
                         start_next_game=start_next_game,
                         session_id=session_id)

    async def start(self):
        random_player_id = random.sample(self.player_ids, 1)[0]
        username = await get_username_by_id(random_player_id, self.context)
        await self.send_group_chat(f"Let's play Waterfall! {username} starts. Send /done when you've played it.")

        self.handlers.append(CommandHandler("done", self.end))
        self.add_handlers()

    async def end(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.send_group_chat("Waterfall ended.")
        self.remove_handlers()

        for player_id in self.player_ids:
            db.increase_player_game_count(self.sql_connection, self.session_id, player_id, 1)
            db.add_points_to_player(self.sql_connection, self.session_id, player_id, 1)

        if self.is_part_of_tournament:
            await self.start_next_game()
        else:
            db.end_session(self.sql_connection, self.session_id)
            logger.info(f"Gamewise session {self.session_id} ended.")
