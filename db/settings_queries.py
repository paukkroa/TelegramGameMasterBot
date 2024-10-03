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

def set_chat_to_all_context(conn: sqlite3.Connection, chat_id: str, player_id: int) -> None:
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE D_CHAT_SETTINGS
    SET context_window_type = 'all',
        uby = ?,
        udate = CURRENT_TIMESTAMP
    WHERE chat_id = ?
    ''', (player_id, chat_id,))
    conn.commit()

def set_chat_to_static_context(conn: sqlite3.Connection, chat_id: str, player_id: int, start_time: str = None, end_time: str = None) -> None:
    cursor = conn.cursor()
    if start_time is not None:
        if end_time is not None:
            cursor.execute('''
            UPDATE D_CHAT_SETTINGS
            SET context_window_type = 'static',
                static_window_start_time = ?,
                static_window_end_time = ?
                uby = ?,
                udate = CURRENT_TIMESTAMP
            WHERE chat_id = ?
            ''', (start_time, end_time, player_id, chat_id))
        else:
            cursor.execute('''
            UPDATE D_CHAT_SETTINGS
            SET context_window_type = 'static',
                static_window_start_time = ?,
                uby = ?,
                udate = CURRENT_TIMESTAMP
            WHERE chat_id = ?
            ''', (start_time, player_id, chat_id))
    else:
        if end_time is not None:
            cursor.execute('''
            UPDATE D_CHAT_SETTINGS
            SET context_window_type = 'static',
                static_window_start_time = CURRENT_TIMESTAMP,
                static_window_end_time = ?,
                uby = ?,
                udate = CURRENT_TIMESTAMP
            WHERE chat_id = ?
            ''', (end_time, player_id, chat_id))
        else:
            cursor.execute('''
            UPDATE D_CHAT_SETTINGS
            SET context_window_type = 'static',
                static_window_start_time = CURRENT_TIMESTAMP,
                uby = ?,
                udate = CURRENT_TIMESTAMP
            WHERE chat_id = ?
            ''', (player_id, chat_id,))

    conn.commit()

def update_chat_static_context_end_time(conn: sqlite3.Connection, chat_id: str, player_id: int, end_time: str = None) -> None:
    cursor = conn.cursor()
    if end_time is not None:
        cursor.execute('''
        UPDATE D_CHAT_SETTINGS
        SET static_window_end_time = ?,
            uby = ?,
            udate = CURRENT_TIMESTAMP
        WHERE chat_id = ?
        ''', (end_time, player_id, chat_id))
    else:
        cursor.execute('''
        UPDATE D_CHAT_SETTINGS
        SET static_window_end_time = CURRENT_TIMESTAMP,
            uby = ?,
            udate = CURRENT_TIMESTAMP
        WHERE chat_id = ?
        ''', (player_id, chat_id,))
    conn.commit()

def set_chat_to_rolling_context(conn: sqlite3.Connection, chat_id: str, player_id: int, window_size: int) -> None:
    """Window_size is in seconds"""
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE D_CHAT_SETTINGS
    SET context_window_type = 'rolling',
        rolling_context_window_size = ?
        uby = ?,
        udate = CURRENT_TIMESTAMP
    WHERE chat_id = ?
    ''', (window_size, player_id, chat_id))
    conn.commit()

def set_chat_to_n_messages_context(conn: sqlite3.Connection, chat_id: str, player_id: int, n_messages: int) -> None:
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE D_CHAT_SETTINGS
    SET context_window_type = 'n-messages',
        n_messages = ?,
        uby = ?,
        udate = CURRENT_TIMESTAMP
    WHERE chat_id = ?
    ''', (n_messages, player_id, chat_id))
    conn.commit()

def set_chat_to_session_context(conn: sqlite3.Connection, chat_id: str, player_id: int) -> None:
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE D_CHAT_SETTINGS
    SET context_window_type = 'session'
        uby = ?,
        udate = CURRENT_TIMESTAMP
    WHERE chat_id = ?
    ''', (player_id, chat_id,))
    conn.commit()

def set_chat_to_no_context(conn: sqlite3.Connection, chat_id: str, player_id: int) -> None:
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE D_CHAT_SETTINGS
    SET context_window_type = 'none'
        uby = ?,
        udate = CURRENT_TIMESTAMP
    WHERE chat_id = ?
    ''', (player_id, chat_id,))
    conn.commit()