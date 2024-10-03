import sqlite3

from utils.logger import get_logger

logger = get_logger(__name__)

def get_chat_settings(conn: sqlite3.Connection, chat_id: str) -> dict:
    cursor = conn.cursor()
    cursor.execute('''
    SELECT context_window_type, 
        rolling_context_window_size, 
        static_window_start_time, 
        static_window_end_time,
        n_messages
    FROM D_CHAT_SETTINGS
    WHERE chat_id = ?
    ''', (chat_id,))
    row = cursor.fetchone()
    if row is None:
        logger.info(f"No settings found for chat_id {chat_id}.")
        return None

    settings = {
        'context_window_type': row[0],
        'rolling_context_window_size': row[1],
        'static_window_start_time': row[2],
        'static_window_end_time': row[3],
        'n_messages': row[4]
    }
    return settings