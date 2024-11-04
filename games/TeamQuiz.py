import random

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from typing import Callable

import db
from games.Game import Game
from utils.logger import get_logger
from utils.helpers import get_username_by_id
from resources.questions import questions

logger = get_logger(__name__)

class TeamQuiz(Game):
    """
    Players are divided into teams.
    Every player gets a trivia question with 4 options.
    Only fastest answer from every team is counted.
    Round ends when a team answers correctly or all teams have answered wrong.

    NOTES:
    Options for implementation:

    - Let every team answer and correct guesses get points
    - (CURRENT) Only fastest correct answer gets points
    """
    def __init__(self,
                 id: int,
                 player_ids: list,
                 update: Update,
                 context: ContextTypes.DEFAULT_TYPE,
                 is_part_of_tournament: bool = False,
                 start_next_game: Callable[[], None] = None,
                 session_id: str = None):
        super().__init__(name="Team quiz",
                         id=id,
                         player_ids=player_ids,
                         update=update,
                         context=context,
                         is_part_of_tournament=is_part_of_tournament,
                         start_next_game=start_next_game,
                         session_id=session_id)

        self.num_of_teams = 0
        self.rounds = 20
        self.current_round = 1
        self.questions_for_game = []
        self.team_points = {}
        self.current_question = None
        self.is_round_ongoing = False
        self.player_points = {player_id: 0 for player_id in self.player_ids}
        # TODO: Disable keyboards so that only the latest is showing?

    async def start(self):
        await self.send_group_chat(f"Let's play team quiz!")
        await self.draw_teams()
        await self.send_group_chat("Send /begin when you want to start.")

        for team_id in self.teams.keys():
            self.team_points[team_id] = 0

        self.draw_questions()

        self.handlers.append(CommandHandler("begin", self.next_question))
        self.handlers.append(CallbackQueryHandler(self.handle_answer, pattern=r'^quiz:'))
        self.add_handlers()

    def set_num_of_teams(self, num):
        self.num_of_teams = num

    def set_rounds(self, rounds):
        self.rounds = rounds

    async def draw_teams(self):
        num_of_players = len(self.player_ids)

        if num_of_players == 2:
            self.num_of_teams = 2

        elif self.num_of_teams == 0:
            self.num_of_teams = num_of_players // 2

        if num_of_players < 2:
            self.num_of_teams = 1

        await self.divide_players_into_teams(self.num_of_teams)
        await self.print_teams()

    def draw_questions(self):
        self.questions_for_game = random.sample(questions, self.rounds)

    async def next_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.is_round_ongoing = True
        self.current_question = self.questions_for_game[self.current_round - 1]

        options = self.current_question['options']
        random.shuffle(options)

        keyboard = [
            [InlineKeyboardButton(option, callback_data=f"quiz:{option}")]
            for option in options
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await self.context.bot.send_message(chat_id=self.chat_id, text=self.current_question['question'],
                                            reply_markup=reply_markup)

        # TODO: decide if question is sent in the group or dm
        """        
        for player_id in self.player_ids:
            await self.context.bot.send_message(chat_id=player_id, text=self.current_question['question'],
                                                reply_markup=reply_markup)
        """

    async def handle_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        answering_player = update.effective_user
        answering_team = self.player_teams[answering_player.id]

        logger.info(f"Answer by {answering_player.username}")

        if not self.is_round_ongoing:
            return

        if self.teams[answering_team]['has_answered']:
            await self.send_player_chat(answering_player.id, "Your team answered already.")
            return

        query = update.callback_query
        await query.answer()
        selected_option = query.data.split(':')[1]

        self.teams[answering_team]['has_answered'] = True
        correct_answers = self.current_question['correct']

        # Team has answered right -> they win the round instantly
        if selected_option in correct_answers:
            self.team_points[answering_team] += 1
            self.player_points[answering_player.id] += 1
            await self.send_group_chat(f"Round winner is team {answering_team}! {answering_player.username} "
                                       f"got the correct answer.")
            await self.end_round()

        # Wrong guess
        else:
            await self.send_group_chat(f"{answering_player.username} from team {answering_team} "
                                       f"guessed wrong.")

        # Everyone has answered and no right answers
        if all(team['has_answered'] for team in self.teams.values()):
            await self.send_group_chat("Round ended. Everyone guessed wrong.")
            await self.end_round()

    async def end_round(self):
        self.is_round_ongoing = False
        self.current_round += 1

        for team_id in self.teams.keys():
            self.teams[team_id]['has_answered'] = False

        if self.current_round > self.rounds:
            await self.end()
            return

        await self.next_question(self.update, self.context)

    async def end(self):
        await self.send_group_chat("Team quiz ended.")
        self.remove_handlers()

        # Sort by points desc
        sorted_teams = sorted(self.team_points.items(), key=lambda item: item[1], reverse=True)
        sorted_players = sorted(self.player_points.items(), key=lambda item: item[1], reverse=True)
        best_player_id = sorted_players[0][0]
        best_player_points = sorted_players[0][1]
        best_player_username = await get_username_by_id(best_player_id, self.context)

        # AWARD POINTS

        first_team_id = sorted_teams[0][0]
        for member in self.teams[first_team_id]['members']:
            db.add_points_to_player(self.sql_connection, self.session_id, member['id'], 5)

        if len(sorted_teams) >= 2:
            second_team_id = sorted_teams[1][0]
            for member in self.teams[second_team_id]['members']:
                db.add_points_to_player(self.sql_connection, self.session_id, member['id'], 3)

        if len(sorted_teams) >= 3:
            third_team_id = sorted_teams[2][0]
            for member in self.teams[third_team_id]['members']:
                db.add_points_to_player(self.sql_connection, self.session_id, member['id'], 1)

        # SHOW FINAL RANKING AND DRINKS

        ranking_msg = "Final ranking of the quiz:\n"
        drink_msg = "Drinks awarded:\n"

        winner_points = self.team_points[first_team_id]

        for i, team_tuple in enumerate(sorted_teams):
            [team_id, points] = team_tuple
            team = self.teams[team_id]
            ranking_msg += f"\n{i + 1}. Team {team_id} ("
            drink_msg += f"\nTeam {team_id} ("

            for j, member in enumerate(team['members']):
                if j > 0:
                    ranking_msg += ", "
                    drink_msg += ", "

                ranking_msg += member['username']
                drink_msg += member['username']

            ranking_msg += f"): {points}"
            drink_msg += f"): {(self.rounds - points) * 2}"

        ranking_msg += f"\n\nTop player was {best_player_username} with {best_player_points} points."

        await self.send_group_chat(ranking_msg)
        await self.send_group_chat(drink_msg)

        self.num_of_teams = 0
        self.current_round = 1
        self.team_points = {}
        self.current_question = None
        self.is_round_ongoing = False
        self.questions_for_game = []

        if self.is_part_of_tournament:
            await self.start_next_game()
        else:
            db.end_session(self.sql_connection, self.session_id)
            logger.info(f"Gamewise session {self.session_id} ended.")
