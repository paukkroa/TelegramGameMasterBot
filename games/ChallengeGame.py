from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
import random
from typing import Callable
import sqlite3
import db

from games.Game import Game
from resources.challenges import all_challenges_by_level
from utils import get_username_by_id

class ChallengeGame(Game):
    def __init__(self, 
                 id: int, 
                 player_ids: list, 
                 update: Update, 
                 context: ContextTypes.DEFAULT_TYPE,
                 is_part_of_tournament: bool = False, 
                 start_next_game: Callable[[], None] = None,
                 sql_connection: sqlite3.Connection = db.connect(), 
                 session_id: str = None, 
                 bot_tg_id: str = None):
        super().__init__(name="Random challenges", 
                         id=id, 
                         player_ids=player_ids, 
                         update=update, 
                         context=context,
                         is_part_of_tournament=is_part_of_tournament, 
                         start_next_game=start_next_game, 
                         sql_connection=sql_connection, 
                         session_id=session_id, 
                         bot_tg_id=bot_tg_id)
        self.rounds = 10
        self.challenges = []
        self.current_challenge_number = 1

    async def start(self):
        await self.send_group_chat("Let's play random challenges!")
        await self.send_group_chat("Send /next whenever you are ready for the next challenge")

        self.handlers.append(CommandHandler("next", self.get_next_challenge))
        self.add_handlers()

    def set_rounds(self, rounds: int):
        self.rounds = rounds

    async def get_next_challenge(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Select random challenge and user"""

        if self.current_challenge_number > self.rounds:
            await self.end()
            return

        # Determine challenge level - 0 = easy, 2 = hard
        challenge_level = random.randint(0, 2)
        challenges = [all_challenges_by_level[challenge_level]]

        challenge = random.sample(1, challenges)[0]

        user_index = random.randint(0, len(self.player_ids) - 1)
        user_id = self.player_ids[user_index]

        username = await get_username_by_id(user_id, context)
        await self.send_group_chat(f"Player: {username} \nChallenge: {challenge}")

        # 1 for easy, 3 for medium, 5 for hard
        points = challenge_level * 2 + 1
        db.add_points_to_player(self.sql_connection, self.session_id, user_id, points)

        # TODO: Add drink units - requires structure change in challenges

        self.current_challenge_number += 1

    async def end(self):
        """End game and remove command handlers"""
        await self.send_group_chat("Congratulations, game ended.")
        self.remove_handlers()

        self.current_challenge_number = 1
        self.challenges.clear()

        for player_id in self.player_ids:
            db.increase_player_game_count(self.sql_connection, self.session_id, player_id, 1)

        if self.is_part_of_tournament:
            await self.start_next_game()