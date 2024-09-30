import sqlite3

from utils.logger import get_logger

logger = get_logger(__name__)

# TODO: Use hashing for telegram_id for improved security
def insert_player(conn: sqlite3.Connection, telegram_id: int, username: str) -> int:
    cursor = conn.cursor()
    # Check if the player already exists
    cursor.execute('SELECT 1 FROM D_PLAYER WHERE player_id = ?', (telegram_id,))
    if cursor.fetchone() is not None:
        logger.info(f"Player with id {telegram_id}, username {username} already exists in D_PLAYER.")
        return None

    # Insert the new player
    cursor.execute('''
    INSERT INTO D_PLAYER (player_id, username) VALUES (?, ?)
    ''', (telegram_id, username))
    conn.commit()
    player_id = cursor.lastrowid
    return player_id


# IMPROVEMENT: Remove the below command as it compromises privacy
def get_all_players(conn: sqlite3.Connection) -> list:
    cursor = conn.cursor()
    cursor.execute(f'''
    SELECT username FROM D_PLAYER 
    ''')
    usernames = cursor.fetchall()
    return usernames

# TODO: Use hashing for player_id and chat_id for improved security
def insert_player_fact(conn: sqlite3.Connection, player_id: int, fact: str) -> int:
    cursor = conn.cursor()

    # Check if the player exists
    cursor.execute('SELECT 1 FROM D_PLAYER WHERE player_id = ?', (player_id,))
    if cursor.fetchone() is None:
        raise Warning(f"Player with id {player_id} does not exist.")

    # Insert the fact
    cursor.execute('''
    INSERT INTO R_PLAYER_FACTS (player_id, fact) VALUES (?, ?)
    ''', (player_id, fact))
    conn.commit()
    fact_id = cursor.lastrowid
    return fact_id

# TODO: Use hashing for player_id for improved security
def get_player_facts(conn: sqlite3.Connection, player_id: int) -> list:
    cursor = conn.cursor()
    cursor.execute(f'''
    SELECT fact FROM R_PLAYER_FACTS WHERE player_id = {player_id}
    ''')
    facts = cursor.fetchall()
    return facts


# TODO: Use hashing for session_id and player_id for improved security
def get_player_points(conn: sqlite3.Connection, session_id: str, player_id: int) -> int:
    cursor = conn.cursor()
    cursor.execute(f'''
    SELECT points FROM R_SESSION_PLAYERS WHERE session_id = {session_id} AND player_id = {player_id}
    ''')
    points = cursor.fetchone()
    return points

# TODO: Use hashing for session_id and player_id for improved security
def add_points_to_player(conn: sqlite3.Connection, session_id: str, player_id: int, points: int) -> None:
    cursor = conn.cursor()
    cursor.execute(f'''
    UPDATE R_SESSION_PLAYERS SET points = points + {points} WHERE session_id = "{session_id}" AND player_id = {player_id}
    ''')
    conn.commit()

# TODO: Use hashing for session_id and player_id for improved security
def remove_points_from_player(conn: sqlite3.Connection, session_id: str, player_id: int, points: int) -> None:
    cursor = conn.cursor()
    cursor.execute(f'''
    UPDATE R_SESSION_PLAYERS SET points = points - {points} WHERE session_id = {session_id} AND player_id = {player_id}
    ''')
    conn.commit()

def add_drinks_to_player(conn: sqlite3.Connection, session_id: str, player_id: int, drink_units: float) -> None:
    cursor = conn.cursor()
    cursor.execute(f'''
        UPDATE R_SESSION_PLAYERS SET drink_units = drink_units + {drink_units} 
        WHERE session_id = "{session_id}" AND player_id = {player_id}
    ''')
    conn.commit()

def increase_player_game_count(conn: sqlite3.Connection, session_id: str, player_id: int, games: int) -> None:
    cursor = conn.cursor()
    cursor.execute(f'''
        UPDATE R_SESSION_PLAYERS SET games = games + {games} 
        WHERE session_id = "{session_id}" AND player_id = {player_id}
    ''')
    conn.commit()
