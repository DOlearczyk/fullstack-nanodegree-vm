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
    c = conn.cursor()
    query = "DELETE FROM Match;"
    c.execute(query)
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    c = conn.cursor()
    query = "DELETE FROM Player;"
    c.execute(query)
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    c = conn.cursor()
    query = "SELECT COUNT(*) FROM Player;"
    c.execute(query)
    result = c.fetchone()
    conn.close()
    return result[0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    c = conn.cursor()
    query = "INSERT INTO Player(name) VALUES (%s);"
    c.execute(query, (name,))
    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players, their win,
    tie, match records, number of points and ranking overall.

    Returns:
      A list of tuples, each of which contains (id, name, wins,
      ties, matches, points, ranking):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        ties: the number of matches the player has tied
        matches: the number of matches the player has played
        points: the number of points the player has gained
        ranking: players ranking based on wins, ties and matches played
    """
    conn = connect()
    c = conn.cursor()
    query = "SELECT * FROM Standings"
    c.execute(query)
    result = c.fetchall()
    conn.close()
    return result


def reportMatch(player_one, player_two, result):
    """Records the outcome of a single match between two players.

    Args:
      player_one:  the id number of the first player
      player_two:  the id number of the second player
      result:   the id number of the result

    Currently accepted result values:
        1: player_one won the match
        2: player_two won the match
        3: the match resulted in a tie
    In case of a 'bye' set player_two value to None and result to 1
    """
    conn = connect()
    c = conn.cursor()
    query = "INSERT INTO Match(player_one_id, player_two_id, result_id) " \
            "VALUES (%s, %s, %s);"
    c.execute(query, (player_one, player_two, result))
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
    # Get player standings
    standings = playerStandings()
    # Variable to hold pairs of players for the next round of a match
    pairs = []
    # Connecting to db and declaring cursor early because of necessity to
    # execute multiple queries to find pairs of players who haven't played yet
    conn = connect()
    c = conn.cursor()
    # Find pairs of players who are closest in ranking and haven't played yet
    while len(standings) > 1:
        # First player of the pair
        first_player = standings[0]
        # Find best pair for first player of the pair
        for i in range(1, len(standings)):
            second_player = standings[i]
            # Check if players played before
            query = "SELECT COUNT(*) FROM Match m " \
                    "WHERE (m.player_one_id=%s AND m.player_two_id=%s) " \
                    "OR (m.player_one_id=%s AND m.player_two_id=%s);"
            c.execute(query, (
                first_player[0], second_player[0],
                second_player[0], first_player[0]))
            result = c.fetchone()
            # If players never played before pair them,
            # else check next player in rankings
            if result[0] == 0:
                pairs.append((first_player[0], first_player[1],
                              second_player[0],
                              second_player[1]))
                del standings[i]
                del standings[0]
                break
    conn.close()
    # If there is odd number of players give 'bye' to player without pair
    if len(standings) == 1:
        #
        pairs.append(
            (standings[0][0], standings[0][1], None, None))
    return pairs
