
import os
import sqlite3
def search():

    DATA_DIR = os.path.dirname(__file__)
    DATABASE_FILENAME = os.path.join(DATA_DIR, 'NBARefs.db')
    #print(DATABASE_FILENAME)
    connection = sqlite3.connect(DATABASE_FILENAME)
    c = connection.cursor()

    ref_query = "SELECT DISTINCT referee_name, referee_name FROM referees JOIN calls \
        on referees.game_code = calls.game_code;"
    committing_player_query = "SELECT DISTINCT committing_player, committing_player \
        FROM referees JOIN calls on referees.game_code = calls.game_code;"
    disadvantaged_player_query = "SELECT DISTINCT disadvantaged_player, disadvantaged_player \
        FROM referees JOIN calls on referees.game_code = calls.game_code;"
    call_type_query = "SELECT DISTINCT call_type, call_type \
        FROM referees JOIN calls on referees.game_code = calls.game_code;"
    #call_accuracy_query = "SELECT DISTINCT call_accuracy, call_accuracy \
    #    FROM referees JOIN calls on referees.game_code = calls.game_code;"
   
    home_team_query = "SELECT DISTINCT home_team, home_team \
        FROM referees JOIN calls on referees.game_code = calls.game_code;"
    away_team_query = "SELECT DISTINCT away_team, away_team \
        FROM referees JOIN calls on referees.game_code = calls.game_code;"
    offending_team_query = "SELECT DISTINCT offending_team, offending_team \
        FROM referees JOIN calls on referees.game_code = calls.game_code;"
    defending_team_query = "SELECT DISTINCT defending_team, defending_team \
        FROM referees JOIN calls on referees.game_code = calls.game_code;"

    c.execute(ref_query)
    REFS = c.fetchall()

    c.execute(committing_player_query)
    COMMITTING_PLAYER = c.fetchall()
    v = COMMITTING_PLAYER
    v.remove(('', ''))
    v.remove((',', ','))
'''
    c.execute(disadvantaged_player_query)
    DISADVANTAGED_PLAYER = c.fetchall()

    c.execute(call_type_query)
    CALL_TYPE = c.fetchall()

    c.execute(home_team_query)
    HOME_TEAM = c.fetchall()

    c.execute(away_team_query)
    AWAY_TEAM = c.fetchall()

    c.execute(offending_team_query)
    OFFENDING_TEAM = c.fetchall()

    c.execute(defending_team_query)
    DEFENDING_TEAM = c.fetchall()
'''
    return v