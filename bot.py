from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

import db
from utils.config import sql_connection, BOT_TOKEN, BOT_NAME, BOT_TG_ID
from callback_handler.handler import callback_query_handler
import command_handlers as handlers

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # Create the database connection and create the tables
    db.create_tables(conn=sql_connection)

    # Add bot id to D_PLAYER if not exists
    db.insert_player(sql_connection, BOT_TG_ID, BOT_NAME)

    # Register the user and chat
    application.add_handler(CommandHandler("start", handlers.start))
    # Help command
    application.add_handler(CommandHandler("help", handlers.help_command))

    # List all players in db
    application.add_handler(CommandHandler("all_players", handlers.list_all_players))

    # List group members
    application.add_handler(CommandHandler("group", handlers.list_group_members))
    # Track users who join the group and get their ids
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handlers.handle_new_member))

    # Tournaments / sessions
    application.add_handler(CommandHandler("join", handlers.handle_join_waitlist))
    application.add_handler(CommandHandler("waitlist", handlers.print_waitlist))
    application.add_handler(CommandHandler("tournament", handlers.start_tournament))
    application.add_handler(CommandHandler("force_end", handlers.end_session))

    # Retrieve statistics
    application.add_handler(CommandHandler("stats_g", handlers.get_group_stats))
    application.add_handler(CommandHandler("stats_p", handlers.get_player_stats))
    application.add_handler(CommandHandler("rank_s", handlers.get_session_ranking))
    application.add_handler(CommandHandler("rank_a", handlers.get_all_time_ranking))

    # Games for testing
    application.add_handler(CommandHandler("numbergame", handlers.handle_number_game_start))
    application.add_handler(CommandHandler("challenges", handlers.handle_challenge_game_start))

    # Handle generic group messages and respond with LLM
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & ~filters.ChatType.PRIVATE, handlers.handle_generic_message)
    )

    # General keyboard option handler
    application.add_handler(CallbackQueryHandler(callback_query_handler))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
