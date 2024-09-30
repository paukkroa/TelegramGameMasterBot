import sqlite3
import hashlib

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


# TODO: Use hashing for session_id and sender_id for improved security
def add_message_to_session_context(conn: sqlite3.Connection, session_id: str, sender_id: int, message: str) -> None:
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO R_SESSION_CONTEXT (session_id, sender_id, message) VALUES (?, ?, ?)
    ''', (session_id, sender_id, message))
    conn.commit()

# TODO: Use hashing for session_id for improved security
def get_session_messages(conn: sqlite3.Connection, session_id: str) -> str:
    cursor = conn.cursor()
    cursor.execute('''
    SELECT dp.username, fsc.message 
    FROM R_SESSION_CONTEXT fsc
    JOIN D_PLAYER dp ON fsc.sender_id = dp.player_id
    WHERE fsc.session_id = ?
    ''', (session_id,))
    messages = cursor.fetchall()
    formatted_messages = ', '.join([f"{username} said: {message}" for username, message in messages])
    return formatted_messages

# TODO: Use hashing for session_id and sender_id for improved security
def get_messages_from_sender(conn: sqlite3.Connection, session_id: str, sender_id: int) -> list:
    cursor = conn.cursor()
    cursor.execute('''
    SELECT message FROM R_SESSION_CONTEXT WHERE session_id = ? AND sender_id = ?
    ''', (session_id, sender_id,))
    messages = cursor.fetchall()
    formatted_messages = ', '.join([f"{message}" for message in messages])
    return formatted_messages


