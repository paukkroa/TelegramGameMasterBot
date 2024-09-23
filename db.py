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
        player_id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id TEXT NOT NULL,
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

    # Session participants F_SESSION_PLAYERS
    conn.execute('''
    CREATE TABLE IF NOT EXISTS F_SESSION_PLAYERS (
        session_id INTEGER PRIMARY KEY,
        player_id INTEGER NOT NULL,
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # All available games D_GAMES
    conn.execute('''
    CREATE TABLE IF NOT EXISTS D_GAMES (
        game_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        function TEXT,
        idate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        udate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # Games played in sessions F_SESSION_GAMES
    conn.execute('''
    CREATE TABLE IF NOT EXISTS F_SESSION_GAMES (
        session_id INTEGER NOT NULL,
        game_id INTEGER NOT NULL,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP,
        winner_id INTEGER,
        loser_id INTEGER,
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

def insert_player(conn: sqlite3.Connection, telegram_id: str) -> int:
    cursor = conn.cursor()
    cursor.execute(f'''
    INSERT INTO D_PLAYER (telegram_id) VALUES ({telegram_id})
    ''')
    conn.commit()
    player_id = cursor.lastrowid
    return player_id

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

def insert_game(conn: sqlite3.Connection, name: str, description: str, function: function = None) -> int:
    cursor = conn.cursor()
    cursor.execute(f'''
    INSERT INTO D_GAMES (name, description, function) VALUES ({name}, {description}, {function})
    ''')
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
    INSERT INTO F_SESSION_PLAYERS (session_id, player_id) VALUES ({session_id}, {player_id})
    ''')
    conn.commit()

def delete_player_from_session(conn: sqlite3.Connection, session_id: int, player_id: int) -> None:
    cursor = conn.cursor()
    cursor.execute(f'''
    DELETE FROM F_SESSION_PLAYERS WHERE session_id = {session_id} AND player_id = {player_id}
    ''')
    conn.commit()

def add_game_to_session(conn: sqlite3.Connection, session_id: int, game_id: int) -> None:
    cursor = conn.cursor()
    cursor.execute(f'''
    INSERT INTO F_SESSION_GAMES (session_id, game_id) VALUES ({session_id}, {game_id})
    ''')
    conn.commit()

def end_game_in_session(conn: sqlite3.Connection, session_id: int, game_id: int, winner_id: int, loser_id: int, iby: str) -> None:
    cursor = conn.cursor()
    cursor.execute(f'''
    UPDATE F_SESSION_GAMES SET end_time = CURRENT_TIMESTAMP, winner_id = {winner_id}, loser_id = {loser_id}, iby = {iby} WHERE session_id = {session_id} AND game_id = {game_id}
    ''')
    conn.commit()
