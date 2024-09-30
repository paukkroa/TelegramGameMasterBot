import sqlite3

def get_player_session_stats(conn: sqlite3.Connection, session_id: str, player_id: int) -> dict:
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT player_id, points, drink_units, games
        FROM R_SESSION_PLAYERS 
        WHERE session_id = "{session_id}" AND player_id = {player_id}
    ''')
    result = cursor.fetchone()
    return {
        'player_id': result[0],
        'points': result[1],
        'drink_units': result[2],
        'games': result[3]
    }

def get_player_all_time_stats(conn: sqlite3.Connection, player_id: int) -> dict:
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT player_id, SUM(points) AS total_points, SUM(drink_units) AS total_drink_units, 
            SUM(games) AS total_games, COUNT(DISTINCT session_id) AS total_tournaments
        FROM R_SESSION_PLAYERS 
        WHERE player_id = {player_id}
        GROUP BY player_id
    ''')
    result = cursor.fetchone()
    return {
        'player_id': result[0],
        'total_points': result[1],
        'total_drink_units': result[2],
        'total_games': result[3],
        'total_tournaments': result[4]
    }

def get_group_session_stats(conn: sqlite3.Connection, session_id: str, chat_id: str) -> dict:
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT chat_id, SUM (rsp.points) AS total_points, SUM(rsp.drink_units) AS total_drink_units,
            SUM (rsp.games) AS total_games
        FROM R_CHAT_MEMBERS rcm
        INNER JOIN R_SESSION_PLAYERS AS rsp ON rcm.player_id = rsp.player_id
        WHERE rcm.chat_id = {chat_id}
            AND rsp.session_id = "{session_id}"
    ''')
    result = cursor.fetchone()
    return {
        'chat_id': result[0],
        'total_points': result[1],
        'total_drink_units': result[2],
        'total_games': result[3]
    }

def get_group_all_time_stats(conn: sqlite3.Connection, chat_id: str) -> dict:
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT chat_id, SUM(rsp.points) AS total_points, SUM(rsp.drink_units) AS total_drink_units,
            SUM(rsp.games) AS total_games, COUNT(DISTINCT rsp.session_id) AS total_tournaments
        FROM R_CHAT_MEMBERS rcm
        INNER JOIN R_SESSION_PLAYERS rsp ON rcm.player_id = rsp.player_id
        WHERE rcm.chat_id = {chat_id}
    ''')
    result = cursor.fetchone()
    return {
        'chat_id': result[0],
        'total_points': result[1],
        'total_drink_units': result[2],
        'total_games': result[3],
        'total_tournaments': result[4]
    }

def get_group_session_ranking(conn: sqlite3.Connection, session_id: str, chat_id: str, order_by: str) -> list:
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT rcm.player_id, username, SUM(points) AS points, SUM(drink_units) AS drinks
        FROM R_CHAT_MEMBERS rcm
        INNER JOIN R_SESSION_PLAYERS rsp ON rsp.player_id = rcm.player_id
        INNER JOIN D_PLAYER dp ON dp.player_id = rcm.player_id
        WHERE chat_id = {chat_id}
            AND session_id = "{session_id}"
        GROUP BY rcm.player_id
        ORDER BY {order_by} DESC
    ''')
    players = cursor.fetchall()
    ranking = [
        {
            'player_id': player_id,
            'username': username,
            'points': points,
            'drinks': drinks
        }
        for player_id, username, points, drinks in players
    ]
    return ranking

def get_group_alltime_ranking(conn: sqlite3.Connection, chat_id: str, order_by: str) -> list:
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT rcm.player_id, username, SUM(points) AS points, SUM(drink_units) AS drinks, SUM(games) AS games,
            COUNT(DISTINCT rsp.session_id) AS tournaments
        FROM R_CHAT_MEMBERS rcm
        INNER JOIN R_SESSION_PLAYERS rsp ON rsp.player_id = rcm.player_id
        INNER JOIN D_PLAYER dp ON dp.player_id = rcm.player_id
        WHERE chat_id = {chat_id}
        GROUP BY rcm.player_id
        ORDER BY {order_by} DESC
    ''')
    players = cursor.fetchall()
    ranking = [
        {
            'player_id': player_id,
            'username': username,
            'points': points,
            'drinks': drinks,
            'games': games,
            'tournaments': tournaments
        }
        for player_id, username, points, drinks, games, tournaments in players
    ]
    return ranking