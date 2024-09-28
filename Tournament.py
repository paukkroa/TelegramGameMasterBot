from telegram import Update
from telegram.ext import ContextTypes
from typing import Type
import random
import sqlite3

from utils import get_username_by_id
from games.GuessNumber import GuessNumber
from games.ChallengeGame import ChallengeGame
from games.Waterfall import Waterfall
from games.Game import Game
from EventPoller import EventPoller
import db

class Tournament:
    def __init__(self, session_id: str, player_ids: list, number_of_games: int, update: Update,
                 context: ContextTypes.DEFAULT_TYPE, sql_connection: sqlite3.Connection, bot_tg_id: int):
        self.player_ids = player_ids
        self.update = update
        self.context = context
        self.games = []
        self.number_of_games = number_of_games
        self.current_game_index = 0
        self.is_active = False
        self.poller = EventPoller(30, self.player_ids, self.update, self.context)
        self.handlers = []
        self.chat_id = self.update.effective_chat.id
        self.sql_connection = sql_connection
        self.session_id = session_id
        self.bot_tg_id = bot_tg_id

    async def send_group_chat(self, message: str):
        db.add_message_to_session_context(self.sql_connection, self.session_id, self.bot_tg_id, message)
        await self.context.bot.send_message(chat_id=self.chat_id, text=message)

    async def start(self) -> None:
        self.is_active = True
        await self.draw_games()

        if self.games:
            await self.poller.start()
            await self.start_next_game()

        return
        # TEST
        await self.games[0].start()

    async def start_next_game(self) -> None:
        if self.current_game_index < len(self.games):
            current_game = self.games[self.current_game_index]
            msg = f"Starting game {self.current_game_index + 1} of {self.number_of_games}"
            await self.send_group_chat(msg)
            await current_game.start()

            self.current_game_index += 1

        else:
            await self.end()

    async def draw_games(self) -> None:
        # Add games whenever they get implemented
        game_classes = [GuessNumber, ChallengeGame, Waterfall]

        if self.number_of_games <= 0:
            await self.send_group_chat("Error: number of games must be greater than 0.")
            return

        if self.number_of_games > len(game_classes):
            await self.send_group_chat("Warning: selected number of games is greater than available games")
            self.number_of_games = len(game_classes)

        if self.number_of_games == 0:
            await self.send_group_chat("Error: no games selected")
            return

        selected_games = random.sample(game_classes, self.number_of_games)

        # TODO: define actual game ids
        counter = 1
        for game_class in selected_games:
            game_instance = self._create_game_instance(game_class, 
                                                       counter, 
                                                       self.player_ids, 
                                                       self.update, 
                                                       self.context, 
                                                       self.sql_connection, 
                                                       self.session_id, 
                                                       self.bot_tg_id)
            self.games.append(game_instance)
            counter += 1

        msg = f"Created {len(self.games)} games"
        await self.send_group_chat(msg)

    def set_games(self, games: list) -> None:
        self.games = games

    def _create_game_instance(self, game_class: Type[Game], 
                              id: int, 
                              player_ids: list, 
                              update: Update,
                              context: ContextTypes.DEFAULT_TYPE, 
                              sql_connection: sqlite3.Connection = db.connect(), 
                              session_id: str = None, 
                              bot_tg_id: str = None) -> Game:
        return game_class(id=id, 
                          player_ids=player_ids, 
                          is_part_of_tournament=True,
                          start_next_game=self.start_next_game, 
                          update=update, 
                          context=context, 
                          sql_connection=sql_connection, 
                          session_id=session_id, 
                          bot_tg_id=bot_tg_id)

    async def end(self):
        self.is_active = False

        """End the current session"""
        user = self.update.effective_user
        session_id = db.get_most_recent_session_by_player(self.sql_connection, user.id)

        if session_id is None:
            print("No active session found to end.")

        db.end_session(self.sql_connection, session_id)
        await self.send_group_chat("Tournament finished!")
        self.poller.end()