from telegram import Update
from telegram.ext import ContextTypes
from typing import Callable
import sqlite3
import db

class Game:
    def __init__(self, 
                 name: str, 
                 id: int, 
                 player_ids: list, 
                 update: Update, 
                 context: ContextTypes.DEFAULT_TYPE,
                 is_part_of_tournament: bool = False, 
                 start_next_game: Callable[[], None] = None, 
                 sql_connection: sqlite3.Connection = db.connect(), 
                 session_id: str = None, 
                 bot_tg_id: str = None):
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
        self.bot_tg_id = bot_tg_id

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