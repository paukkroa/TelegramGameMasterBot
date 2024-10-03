import sqlite3
import hashlib
from datetime import datetime, timedelta

def start_session(conn: sqlite3.Connection, chat_id: str) -> str:
    cursor = conn.cursor()

    # Get the current max chat_running_id for the given chat_id
    cursor.execute('''
    SELECT COALESCE(MAX(chat_running_id), 0) + 1 FROM D_SESSION WHERE chat_id = ?
    ''', (chat_id,))
    chat_running_id = cursor.fetchone()[0]

    # Create the session_id
    session_id = f"{chat_id}_{chat_running_id}"

    # Hash the session_id
    session_hash = hashlib.md5(session_id.encode()).hexdigest()

    # Insert the new session
    cursor.execute('''
    INSERT INTO D_SESSION (session_id, chat_id, chat_running_id) VALUES (?, ?, ?)
    ''', (session_hash, chat_id, chat_running_id,))
    conn.commit()

    return session_hash

# TODO: Use hashing for session_id for improved security
def end_session(conn: sqlite3.Connection, session_id: str) -> None:
    cursor = conn.cursor()
    cursor.execute(f'''
    UPDATE D_SESSION SET end_time = CURRENT_TIMESTAMP, ongoing = 0 WHERE session_id = ?
    ''', (session_id,))
    conn.commit()

# TODO: Use hashing for session_id and player_id for improved security
def add_player_to_session(conn: sqlite3.Connection, session_id: str, player_id: int) -> None:
    cursor = conn.cursor()
    cursor.execute(f'''
    INSERT INTO R_SESSION_PLAYERS (session_id, player_id) VALUES (?, ?)
    ''', (session_id, player_id))
    conn.commit()

# TODO: Use hashing for session_id and player_id for improved security
def delete_player_from_session(conn: sqlite3.Connection, session_id: str, player_id: int) -> None:
    cursor = conn.cursor()
    cursor.execute(f'''
    DELETE FROM R_SESSION_PLAYERS WHERE session_id = {session_id} AND player_id = {player_id}
    ''')
    conn.commit()

# TODO: Use hashing for session_id for improved security
def get_session_players(conn: sqlite3.Connection, session_id: str) -> list:
    cursor = conn.cursor()
    cursor.execute(f'''
    SELECT player_id FROM R_SESSION_PLAYERS WHERE session_id = {session_id}
    ''')
    player_ids = cursor.fetchall()
    return player_ids

# TODO: Use hashing for session_id for improved security
def add_game_to_session(conn: sqlite3.Connection, session_id: str, game_id: int) -> None:
    cursor = conn.cursor()
    cursor.execute(f'''
    INSERT INTO R_SESSION_GAMES (session_id, game_id) VALUES ({session_id}, {game_id})
    ''')
    conn.commit()

# TODO: Use hashing for session_id for improved security
def end_game_in_session(conn: sqlite3.Connection, session_id: str, game_id: int, winner_id: int, loser_id: int, iby: str) -> None:
    cursor = conn.cursor()
    cursor.execute(f'''
    UPDATE R_SESSION_GAMES SET end_time = CURRENT_TIMESTAMP, winner_id = {winner_id}, loser_id = {loser_id}, iby = {iby} WHERE session_id = {session_id} AND game_id = {game_id}
    ''')
    conn.commit()

# TODO: Use hashing for player_id for improved security
# IMPROVEMENT: Replace this command with a function to get the most recent by chat_id
def get_latest_ongoing_session_by_player(conn: sqlite3.Connection, player_id: int) -> int:
    cursor = conn.cursor()
    cursor.execute('''
    SELECT rsp.session_id 
    FROM R_SESSION_PLAYERS rsp
    JOIN D_SESSION ds ON rsp.session_id = ds.session_id
    WHERE rsp.player_id = ? AND ds.ongoing = 1
    ORDER BY ds.idate DESC 
    LIMIT 1
    ''', (player_id,))
    try:
        session_id = cursor.fetchone()
        return session_id[0]
    except:
        return None

def get_latest_ongoing_session_by_chat(conn: sqlite3.Connection, chat_id: str) -> str:
    cursor = conn.cursor()
    cursor.execute('''
    SELECT session_id 
    FROM D_SESSION
    WHERE chat_id = ? 
    AND ongoing = 1
    ORDER BY chat_running_id DESC 
    LIMIT 1
    ''', (chat_id,))
    try:
        session_id = cursor.fetchone()
        return session_id[0]
    except:
        return None

def get_most_recent_session_by_player(conn: sqlite3.Connection, player_id: int) -> None:
    cursor = conn.cursor()
    cursor.execute('''
    SELECT session_id
    FROM R_SESSION_PLAYERS rsp
    WHERE player_id = ?
    ORDER BY idate DESC
    LIMIT 1
    ''', (player_id,))
    try:
        session_id = cursor.fetchone()
        return session_id[0]
    except:
        return None


def add_message_to_chat_context(conn: sqlite3.Connection, chat_id: str, sender_id: int, message: str, session_id: str = None) -> None:
    cursor = conn.cursor()
    
    # If session_id is not provided, get the latest ongoing session for the chat
    if session_id is None:
        cursor.execute('''
        SELECT session_id 
        FROM D_SESSION
        WHERE chat_id = ? 
        AND ongoing = 1
        ORDER BY chat_running_id DESC 
        LIMIT 1
        ''', (chat_id,))
        session_id = cursor.fetchone()
        if session_id:
            session_id = session_id[0]
        else:
            session_id = ''

    cursor.execute('''
    INSERT INTO R_CHAT_CONTEXT (session_id, chat_id, sender_id, message) VALUES (?, ?, ?, ?)
    ''', (session_id, chat_id, sender_id, message))
    conn.commit()

def get_session_messages(conn: sqlite3.Connection, session_id: str) -> str:
    cursor = conn.cursor()
    cursor.execute('''
    SELECT dp.username, fsc.message 
    FROM R_CHAT_CONTEXT fsc
    JOIN D_PLAYER dp ON fsc.sender_id = dp.player_id
    WHERE fsc.session_id = ?
    ''', (session_id,))
    messages = cursor.fetchall()
    formatted_messages = ', '.join([f"{username} said: {message}" for username, message in messages])
    return formatted_messages

def get_session_messages_from_sender(conn: sqlite3.Connection, session_id: str, sender_id: int) -> list:
    cursor = conn.cursor()
    cursor.execute('''
    SELECT message FROM R_CHAT_CONTEXT WHERE session_id = ? AND sender_id = ?
    ''', (session_id, sender_id,))
    messages = cursor.fetchall()
    formatted_messages = ', '.join([f"{message}" for message in messages])
    return formatted_messages

def get_all_chat_messages(conn: sqlite3.Connection, chat_id: str) -> list:
    cursor = conn.cursor()
    cursor.execute('''
    SELECT dp.username, fsc.message 
    FROM R_CHAT_CONTEXT fsc
    JOIN D_PLAYER dp ON fsc.sender_id = dp.player_id
    JOIN D_SESSION ds ON fsc.session_id = ds.session_id
    WHERE ds.chat_id = ?
    ''', (chat_id,))
    messages = cursor.fetchall()
    formatted_messages = ', '.join([f"{username} said: {message}" for username, message in messages])
    return formatted_messages

def get_all_chat_messages_from_sender(conn: sqlite3.Connection, chat_id: str, sender_id: int) -> list:
    cursor = conn.cursor()
    cursor.execute('''
    SELECT fsc.message 
    FROM R_CHAT_CONTEXT fsc
    JOIN D_SESSION ds ON fsc.session_id = ds.session_id
    WHERE ds.chat_id = ? AND fsc.sender_id = ?
    ''', (chat_id, sender_id,))
    messages = cursor.fetchall()
    formatted_messages = ', '.join([f"{message}" for message in messages])
    return formatted_messages

def get_chat_messages_from_rolling_time_window(conn: sqlite3.Connection, chat_id: str) -> list:
    cursor = conn.cursor()
    cursor.execute('''
    SELECT rolling_context_window_size FROM D_CHAT_SETTINGS WHERE chat_id = ?
    ''', (chat_id,))
    rolling_time_window = cursor.fetchone()
    if rolling_time_window:
        rolling_time_window = rolling_time_window[0]
    else:
        rolling_time_window = 0

    end_time = datetime.now()
    start_time = end_time - timedelta(seconds=rolling_time_window)
    cursor.execute('''
    SELECT dp.username, fsc.message, fsc.message_timestamp
    FROM R_CHAT_CONTEXT fsc
    JOIN D_PLAYER dp ON fsc.sender_id = dp.player_id
    JOIN D_SESSION ds ON fsc.session_id = ds.session_id
    WHERE ds.chat_id = ? AND fsc.idate BETWEEN ? AND ?
    ''', (chat_id, start_time, end_time))
    messages = cursor.fetchall()
    formatted_messages = ', '.join([f"At {timestamp} {username} said: {message}" for username, message, timestamp in messages])
    return formatted_messages

def get_chat_messages_within_time_window(conn: sqlite3.Connection, chat_id: str) -> list:
    cursor = conn.cursor()
    cursor.execute('''
    SELECT static_window_start_time, static_window_end_time FROM D_CHAT_SETTINGS WHERE chat_id = ?
    ''', (chat_id,))
    time_window = cursor.fetchone()
    if time_window:
        start_time, end_time = time_window
        if end_time is None:
            end_time = datetime.now()
    else:
        current_timestamp = datetime.now()
        start_time, end_time = current_timestamp, current_timestamp
    cursor.execute('''
    SELECT dp.username, fsc.message, fsc.message_timestamp
    FROM R_CHAT_CONTEXT fsc
    JOIN D_PLAYER dp ON fsc.sender_id = dp.player_id
    JOIN D_SESSION ds ON fsc.session_id = ds.session_id
    WHERE ds.chat_id = ? AND fsc.message_timestamp BETWEEN ? AND ?
    ''', (chat_id, start_time, end_time))
    messages = cursor.fetchall()
    formatted_messages = ', '.join([f"At {timestamp} {username} said: {message}" for username, message, timestamp in messages])
    return formatted_messages

def get_last_n_messages(conn: sqlite3.Connection, chat_id: str) -> list:
    cursor = conn.cursor()
    
    # Get the number of messages to retrieve from D_CHAT_SETTINGS
    cursor.execute('''
    SELECT n_messages FROM D_CHAT_SETTINGS WHERE chat_id = ?
    ''', (chat_id,))
    n_messages = cursor.fetchone()
    if n_messages:
        n_messages = n_messages[0]
    else:
        n_messages = 0  # Default value if not set

    # Retrieve the last n messages from R_CHAT_CONTEXT
    cursor.execute('''
    SELECT dp.username, fsc.message, fsc.message_timestamp
    FROM R_CHAT_CONTEXT fsc
    JOIN D_PLAYER dp ON fsc.sender_id = dp.player_id
    JOIN D_SESSION ds ON fsc.session_id = ds.session_id
    WHERE ds.chat_id = ?
    ORDER BY fsc.message_timestamp DESC
    LIMIT ?
    ''', (chat_id, n_messages))
    messages = cursor.fetchall()
    
    # Format the messages
    formatted_messages = ', '.join([f"At {timestamp} {username} said: {message}" for username, message, timestamp in messages])
    return formatted_messages