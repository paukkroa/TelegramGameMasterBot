import random

from telegram import Update
from telegram.ext import ContextTypes
from typing import Callable

import db
from utils.logger import get_logger
from utils.config import sql_connection, BOT_TG_ID
from utils.helpers import get_username_by_id

logger = get_logger(__name__)

class Game:
    def __init__(self, 
                 name: str, 
                 id: int, 
                 player_ids: list, 
                 update: Update, 
                 context: ContextTypes.DEFAULT_TYPE,
                 is_part_of_tournament: bool = False, 
                 start_next_game: Callable[[], None] = None,
                 session_id: str = None):

        self.name = name
        self.id = id
        self.player_ids = player_ids
        self.is_part_of_tournament = is_part_of_tournament
        self.update = update
        self.context = context
        self.start_next_game = start_next_game
        self.handlers = []
        self.chat_id = self.update.effective_chat.id
        self.sql_connection = sql_connection
        self.session_id = session_id
        self.bot_tg_id_str = BOT_TG_ID

        # FOR TEAM GAMES:
        """ 
        dict of dicts - entry format: 
        {
            team_id: int (1 - n) {
                members: [
                    {
                        id: int,
                        username: str
                    }
                ],
                has_answered: bool    
            }
        }
        """
        self.teams = {}
        """
        For checking which team player belongs to
        { 'player_id' : team_id }
        """
        self.player_teams = {}

    async def start(self):
        msg = f"Let's play {self.name}!"
        db.add_message_to_chat_context(self.sql_connection, self.chat_id, self.bot_tg_id, msg, self.session_id) 
        await self.send_group_chat(msg)

    async def send_group_chat(self, message: str):
        db.add_message_to_chat_context(self.sql_connection, self.chat_id, self.bot_tg_id, message, self.session_id) 
        await self.context.bot.send_message(chat_id=self.chat_id, text=message)

    async def send_player_chat(self, user_id: int, message: str):
        db.add_message_to_chat_context(self.sql_connection, self.session_id, self.bot_tg_id, message, self.session_id)
        await self.context.bot.send_message(chat_id=user_id, text=message)

    def add_handlers(self):
        for handler in self.handlers:
            self.context.application.add_handler(handler)

    def remove_handlers(self):
        for handler in self.handlers:
            self.context.application.remove_handler(handler)

    async def divide_players_into_teams(self, num_of_teams: int) -> dict:
        num_of_players = len(self.player_ids)
        self.teams = {}
        self.player_teams = {}

        if num_of_teams > num_of_players:
            logger.error(f"Could not divide {num_of_players} into {num_of_teams} groups.")
            return {}

        player_ids = self.player_ids
        random.shuffle(player_ids)

        avg_group_size = num_of_players // num_of_teams
        remainder = num_of_players % num_of_teams
        start = 0

        for i in range(num_of_teams):
            team_id = i + 1
            team = {'members': [], 'has_answered': False}

            group_size = avg_group_size + (1 if i < remainder else 0)
            team_player_ids = player_ids[start:start + group_size]

            for player_id in team_player_ids:
                username = await get_username_by_id(player_id, self.context)
                team['members'].append({'id': player_id, 'username': username})
                self.player_teams[player_id] = team_id

            self.teams[team_id] = team
            start += group_size

        return self.teams

    async def print_teams(self):
        msg = f"The teams are:\n"

        for team_id, team in self.teams.items():
            msg += f"\nTeam {team_id}: "

            for j, member in enumerate(team['members']):
                if j > 0:
                    msg += ", "

                msg += member['username']

        await self.send_group_chat(msg)

