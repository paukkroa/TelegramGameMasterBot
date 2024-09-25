import sqlite3

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
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (player_id) REFERENCES D_PLAYER(player_id)
    );
    ''')

    # Game sessions D_SESSION
    conn.execute('''
    CREATE TABLE IF NOT EXISTS D_SESSION (
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        host_id INTEGER NOT NULL,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP,
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (host_id) REFERENCES D_PLAYER(player_id)
    );
    ''')

    # Session participants R_SESSION_PLAYERS
    conn.execute('''
    CREATE TABLE IF NOT EXISTS R_SESSION_PLAYERS (
        session_id INTEGER PRIMARY KEY,
        player_id INTEGER NOT NULL,
        points INTEGER DEFAULT 0,
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (player_id) REFERENCES D_PLAYER(player_id)
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
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # Games played in sessions R_SESSION_GAMES
    conn.execute('''
    CREATE TABLE IF NOT EXISTS R_SESSION_GAMES (
        session_id INTEGER NOT NULL,
        game_id INTEGER NOT NULL,
        winner_id INTEGER NOT NULL,
        loser_id INTEGER NOT NULL,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP,
        iby TEXT,
        uby TEXT,
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
    CREATE TABLE IF NOT EXISTS F_SESSION_CONTEXT (
        session_id INTEGER NOT NULL,
        sender_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        message_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        iby TEXT,
        uby TEXT,
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES D_SESSION(session_id),
        FOREIGN KEY (sender_id) REFERENCES D_PLAYER(player_id)
    );
    ''')

def insert_player(conn: sqlite3.Connection, telegram_id: str) -> int:
    cursor = conn.cursor()
    cursor.execute(f'''
    INSERT INTO D_PLAYER (player_id) VALUES ({telegram_id})
    ''')
    conn.commit()
    player_id = cursor.lastrowid
    return player_id

def get_players(conn: sqlite3.Connection) -> list:
    cursor = conn.cursor()
    cursor.execute(f'''
    SELECT player_id FROM D_PLAYER 
    ''')
    player_ids = cursor.fetchall()
    return player_ids

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

def start_session(conn: sqlite3.Connection, host_id: int) -> int:
    cursor = conn.cursor()
    cursor.execute(f'''
    INSERT INTO D_SESSION (host_id) VALUES ({host_id})
    ''')
    conn.commit()
    session_id = cursor.lastrowid
    return session_id

def end_session(conn: sqlite3.Connection, session_id: int) -> None:
    cursor = conn.cursor()
    cursor.execute(f'''
    UPDATE D_SESSION SET end_time = CURRENT_TIMESTAMP WHERE session_id = {session_id}
    ''')
    conn.commit()

def add_player_to_session(conn: sqlite3.Connection, session_id: int, player_id: int) -> None:
    cursor = conn.cursor()
    cursor.execute(f'''
    INSERT INTO R_SESSION_PLAYERS (session_id, player_id) VALUES ({session_id}, {player_id})
    ''')
    conn.commit()

def delete_player_from_session(conn: sqlite3.Connection, session_id: int, player_id: int) -> None:
    cursor = conn.cursor()
    cursor.execute(f'''
    DELETE FROM R_SESSION_PLAYERS WHERE session_id = {session_id} AND player_id = {player_id}
    ''')
    conn.commit()

def get_session_players(conn: sqlite3.Connection, session_id: int) -> list:
    cursor = conn.cursor()
    cursor.execute(f'''
    SELECT player_id FROM R_SESSION_PLAYERS WHERE session_id = {session_id}
    ''')
    player_ids = cursor.fetchall()
    return player_ids

def add_game_to_session(conn: sqlite3.Connection, session_id: int, game_id: int) -> None:
    cursor = conn.cursor()
    cursor.execute(f'''
    INSERT INTO R_SESSION_GAMES (session_id, game_id) VALUES ({session_id}, {game_id})
    ''')
    conn.commit()

def end_game_in_session(conn: sqlite3.Connection, session_id: int, game_id: int, winner_id: int, loser_id: int, iby: str) -> None:
    cursor = conn.cursor()
    cursor.execute(f'''
    UPDATE R_SESSION_GAMES SET end_time = CURRENT_TIMESTAMP, winner_id = {winner_id}, loser_id = {loser_id}, iby = {iby} WHERE session_id = {session_id} AND game_id = {game_id}
    ''')
    conn.commit()

def get_player_facts(conn: sqlite3.Connection, player_id: int) -> list:
    cursor = conn.cursor()
    cursor.execute(f'''
    SELECT fact FROM R_PLAYER_FACTS WHERE player_id = {player_id}
    ''')
    facts = cursor.fetchall()
    return facts

def get_player_points(conn: sqlite3.Connection, session_id: int, player_id: int) -> int:
    cursor = conn.cursor()
    cursor.execute(f'''
    SELECT points FROM R_SESSION_PLAYERS WHERE session_id = {session_id} AND player_id = {player_id}
    ''')
    points = cursor.fetchone()
    return points

def add_points_to_player(conn: sqlite3.Connection, session_id: int, player_id: int, points: int) -> None:
    cursor = conn.cursor()
    cursor.execute(f'''
    UPDATE R_SESSION_PLAYERS SET points = points + {points} WHERE session_id = {session_id} AND player_id = {player_id}
    ''')
    conn.commit()

def remove_points_from_player(conn: sqlite3.Connection, session_id: int, player_id: int, points: int) -> None:
    cursor = conn.cursor()
    cursor.execute(f'''
    UPDATE R_SESSION_PLAYERS SET points = points - {points} WHERE session_id = {session_id} AND player_id = {player_id}
    ''')
    conn.commit()

def add_message_to_session_context(conn: sqlite3.Connection, session_id: int, sender_id: int, message: str) -> None:
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO F_SESSION_CONTEXT (session_id, sender_id, message) VALUES (?, ?, ?, ?)
    ''', (session_id, sender_id, message))
    conn.commit()

def get_session_messages(conn: sqlite3.Connection, session_id: int) -> list:
    cursor = conn.cursor()
    cursor.execute('''
    SELECT message, message_timestamp, sender_id FROM F_SESSION_CONTEXT WHERE session_id = ?
    ''', (session_id,))
    messages = cursor.fetchall()
    return messages

def get_messages_from_sender(conn: sqlite3.Connection, session_id: int, sender_id: int) -> list:
    cursor = conn.cursor()
    cursor.execute('''
    SELECT message, message_timestamp, session_id FROM F_SESSION_CONTEXT WHERE session_id = ? AND sender_id = ?
    ''', (session_id, sender_id,))
    messages = cursor.fetchall()
    return messages