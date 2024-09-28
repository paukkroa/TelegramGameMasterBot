import sqlite3
import logging
import hashlib

# LOGGING
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

def connect(db: str = 'drink_games.db') -> sqlite3.Connection:
    conn = sqlite3.connect(db)
    return conn

def close_connection(conn: sqlite3.Connection) -> None:
    conn.close()

def create_tables(conn: sqlite3.Connection) -> None:
    # Registered players D_PLAYER
    conn.execute('''
    CREATE TABLE IF NOT EXISTS D_PLAYER (
        player_id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        iby TEXT DEFAULT 'system',
        uby TEXT DEFAULT 'system',
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # Facts for trivias D_PLAYER_FACTS
    conn.execute('''
    CREATE TABLE IF NOT EXISTS R_PLAYER_FACTS (
        fact_id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id INTEGER NOT NULL,
        fact TEXT NOT NULL,
        iby TEXT DEFAULT 'system',
        uby TEXT DEFAULT 'system',
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (player_id) REFERENCES D_PLAYER(player_id)
    );
    ''')

    # Chat information D_CHAT
    conn.execute('''
    CREATE TABLE IF NOT EXISTS D_CHAT (
        chat_id TEXT PRIMARY KEY,
        chat_name TEXT,
        iby TEXT DEFAULT 'system',
        uby TEXT DEFAULT 'system',
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # Chat members R_CHAT_MEMBERS
    conn.execute('''
    CREATE TABLE IF NOT EXISTS R_CHAT_MEMBERS (
        chat_id TEXT NOT NULL,
        player_id INTEGER NOT NULL,
        iby TEXT DEFAULT 'system',
        uby TEXT DEFAULT 'system',
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (chat_id) REFERENCES D_CHAT(chat_id),
        FOREIGN KEY (player_id) REFERENCES D_PLAYER(player_id)
    );
    ''')

    # Game sessions D_SESSION
    conn.execute('''
    CREATE TABLE IF NOT EXISTS D_SESSION (
        session_id TEXT PRIMARY KEY,
        chat_id TEXT NOT NULL,
        chat_running_id INTEGER NOT NULL DEFAULT 1,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP,
        ongoing BOOLEAN DEFAULT 1,
        iby TEXT DEFAULT 'system',
        uby TEXT DEFAULT 'system',
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (chat_id) REFERENCES D_CHAT(chat_id)
    );
    ''')

    # Session participants R_SESSION_PLAYERS
    conn.execute('''
    CREATE TABLE IF NOT EXISTS R_SESSION_PLAYERS (
        session_id TEXT NOT NULL,
        player_id INTEGER,
        points INTEGER DEFAULT 0,
        iby TEXT DEFAULT 'system',
        uby TEXT DEFAULT 'system',
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (player_id) REFERENCES D_PLAYER(player_id),
        FOREIGN KEY (session_id) REFERENCES D_PLAYER(session_id)
    );
    ''')

    # All available games D_GAMES
    conn.execute('''
    CREATE TABLE IF NOT EXISTS D_GAMES (
        game_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        type TEXT NOT NULL,
        rules TEXT,
        telegram_commands TEXT,
        iby TEXT DEFAULT 'system',
        uby TEXT DEFAULT 'system',
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # Games played in sessions R_SESSION_GAMES
    conn.execute('''
    CREATE TABLE IF NOT EXISTS R_SESSION_GAMES (
        session_id TEXT NOT NULL,
        game_id INTEGER NOT NULL,
        winner_id INTEGER NOT NULL,
        loser_id INTEGER NOT NULL,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP,
        iby TEXT DEFAULT 'system',
        uby TEXT DEFAULT 'system',
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES D_SESSION(session_id),
        FOREIGN KEY (game_id) REFERENCES D_GAMES(game_id),
        FOREIGN KEY (winner_id) REFERENCES D_PLAYER(player_id),
        FOREIGN KEY (loser_id) REFERENCES D_PLAYER(player_id)
    );
    ''')

    # Session context F_SESSION_CONTEXT
    conn.execute('''
    CREATE TABLE IF NOT EXISTS R_SESSION_CONTEXT (
        session_id TEXT NOT NULL,
        sender_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        message_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        iby TEXT DEFAULT 'system',
        uby TEXT DEFAULT 'system',
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES D_SESSION(session_id),
        FOREIGN KEY (sender_id) REFERENCES D_PLAYER(player_id)
    );
    ''')

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

# TODO: Use hashing for chat_id for improved security
def create_chat(conn: sqlite3.Connection, chat_id: str, chat_name: str = '') -> None:
    cursor = conn.cursor()
    # Check if the chat_id already exists
    cursor.execute('SELECT 1 FROM D_CHAT WHERE chat_id = ?', (chat_id,))
    if cursor.fetchone() is not None:
        logger.info(f"Chat with id {chat_id}, name {chat_name} already exists in D_CHAT.")
        return

    # Insert the new chat
    cursor.execute('''
    INSERT INTO D_CHAT (chat_id, chat_name) VALUES (?, ?)
    ''', (chat_id, chat_name))
    conn.commit()

# TODO: Use hashing for chat_id for improved security
def delete_chat(conn: sqlite3.Connection, chat_id: str) -> None:
    cursor = conn.cursor()
    cursor.execute('''
    DELETE FROM D_CHAT WHERE chat_id = ?
    ''', (chat_id,))
    conn.commit()

# TODO: Use hashing for player_id and chat_id for improved security
def add_player_to_chat(conn: sqlite3.Connection, chat_id: str, player_id: int) -> None:
    cursor = conn.cursor()
    # Check if the player already exists in the chat
    cursor.execute('SELECT 1 FROM R_CHAT_MEMBERS WHERE chat_id = ? AND player_id = ?', (chat_id, player_id))
    if cursor.fetchone() is not None:
        logger.info(f"Player with id {player_id} already exists in chat {chat_id}.")
        return

    # Insert the player into the chat
    cursor.execute('''
    INSERT INTO R_CHAT_MEMBERS (chat_id, player_id) VALUES (?, ?)
    ''', (chat_id, player_id))
    conn.commit()

# TODO: Use hashing for player_id and chat_id for improved security
def remove_player_from_chat(conn: sqlite3.Connection, chat_id: str, player_id: int) -> None:
    cursor = conn.cursor()
    cursor.execute('''
    DELETE FROM R_CHAT_MEMBERS WHERE chat_id = ? AND player_id = ?
    ''', (chat_id, player_id))
    conn.commit()

# TODO: Use hashing for chat_id for improved security
def get_chat_members(conn: sqlite3.Connection, chat_id: str) -> list:
    cursor = conn.cursor()
    cursor.execute('''
    SELECT dp.username 
    FROM R_CHAT_MEMBERS rcm
    JOIN D_PLAYER dp ON rcm.player_id = dp.player_id
    WHERE rcm.chat_id = ?
    ''', (chat_id,))
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

def insert_game(conn: sqlite3.Connection, name: str, description: str, game_type: str, rules: str = None, telegram_commands: str = None) -> int:
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO D_GAMES (name, description, type, rules, telegram_commands) VALUES (?, ?, ?, ?, ?)
    ''', (name, description, game_type, rules, telegram_commands))
    conn.commit()
    game_id = cursor.lastrowid
    return game_id

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
    UPDATE R_SESSION_PLAYERS SET points = points + {points} WHERE session_id = {session_id} AND player_id = {player_id}
    ''')
    conn.commit()

# TODO: Use hashing for session_id and player_id for improved security
def remove_points_from_player(conn: sqlite3.Connection, session_id: str, player_id: int, points: int) -> None:
    cursor = conn.cursor()
    cursor.execute(f'''
    UPDATE R_SESSION_PLAYERS SET points = points - {points} WHERE session_id = {session_id} AND player_id = {player_id}
    ''')
    conn.commit()

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

# TODO: Use hashing for player_id for improved security
# IMPROVEMENT: Replace this command with a function to get the most recent by chat_id
def get_most_recent_session_by_player(conn: sqlite3.Connection, player_id: int) -> int:
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
    
def get_most_recent_session_by_chat(conn: sqlite3.Connection, chat_id: str) -> str:
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