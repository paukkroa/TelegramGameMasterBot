from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
import random
from typing import Callable

import db
from games.Game import Game
from resources.challenges import all_challenges_by_level
from utils.logger import get_logger
from utils.helpers import get_username_by_id, convert_swigs_to_units, convert_shots_to_units

logger = get_logger(__name__)

class ChallengeGame(Game):
    def __init__(self, 
                 id: int, 
                 player_ids: list, 
                 update: Update, 
                 context: ContextTypes.DEFAULT_TYPE,
                 is_part_of_tournament: bool = False, 
                 start_next_game: Callable[[], None] = None,
                 session_id: str = None):
        super().__init__(name="Random challenges", 
                         id=id, 
                         player_ids=player_ids, 
                         update=update, 
                         context=context,
                         is_part_of_tournament=is_part_of_tournament, 
                         start_next_game=start_next_game,
                         session_id=session_id)
        self.rounds = 10
        self.current_challenge_number = 1

    async def start(self):
        await self.send_group_chat("💃 Let's play random challenges! 🕺\n\nSend /next whenever you are ready for the next challenge!")
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
        challenges = all_challenges_by_level[challenge_level]

        challenge = random.choice(challenges)

        user_index = random.randint(0, len(self.player_ids) - 1)
        user_id = self.player_ids[user_index]

        username = await get_username_by_id(user_id, context)
        await self.send_group_chat(f"{username}, your challenge is:\n{challenge['name']}")

        if challenge['swigs'] > 0:
            drink_units = convert_swigs_to_units(challenge['swigs'])
            db.add_drinks_to_player(self.sql_connection, self.session_id, user_id, drink_units)

        if challenge['shots'] > 0:
            drink_units = convert_shots_to_units(challenge['shots'])
            db.add_drinks_to_player(self.sql_connection, self.session_id, user_id, drink_units)

        points = challenge['points']
        db.add_points_to_player(self.sql_connection, self.session_id, user_id, points)

        self.current_challenge_number += 1

    async def end(self):
        """End game and remove command handlers"""
        await self.send_group_chat("💃 Congratulations, challenge game ended! 🕺")
        self.remove_handlers()

        self.current_challenge_number = 1

        for player_id in self.player_ids:
            db.increase_player_game_count(self.sql_connection, self.session_id, player_id, 1)

        if self.is_part_of_tournament:
            await self.start_next_game()
        else:
            db.end_session(self.sql_connection, self.session_id)
            logger.info(f"Gamewise session {self.session_id} ended.")