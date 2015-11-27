#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM matches *;")
    conn.commit()
    conn.close()

def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players *;")
    conn.commit()
    conn.close()

def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM players;")
    count = cursor.fetchall()
    conn.commit()
    conn.close()
    count = count[0]
    count1 = int(count[0])
    print(count1)
    return count1


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO players (name) VALUES (%s);",(name,))
    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DROP VIEW prime;")
    cursor.execute("CREATE VIEW prime AS SELECT count(matches.winner) as matches, players.id, players.name from matches right join players on players.id = matches.winner or players.id = matches.loser group by players.id;")
    cursor.execute("SELECT prime.id, prime. name, count(matches.winner) as wins, prime.matches FROM matches RIGHT JOIN prime ON prime.id = matches.winner group by prime.id, prime.matches, prime.name ORDER BY wins DESC;")
    standings = cursor.fetchall()
    conn.commit()
    conn.close()
    return standings



def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO matches (winner, loser) VALUES (%s, %s);",(winner, loser))
    conn.commit()
    conn.close()
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DROP VIEW prime;")
    cursor.execute("CREATE VIEW prime AS SELECT count(matches.winner) as matches, players.id, players.name from matches right join players on players.id = matches.winner or players.id = matches.loser group by players.id;")
    cursor.execute("SELECT prime.id, prime. name, count(matches.winner) as wins, prime.matches FROM matches RIGHT JOIN prime ON prime.id = matches.winner group by prime.id, prime.matches, prime.name ORDER BY wins DESC;")

    count = 0
    temp_list = []
    pairings = []

    for row in cursor.fetchall():
        temp_list.append(int(row[0]))
        temp_list.append(str(row[1]))
        count += 1
        if count%2==0:
            pairings.append(temp_list)
            temp_list = []

    conn.commit()
    conn.close()
    return pairings

