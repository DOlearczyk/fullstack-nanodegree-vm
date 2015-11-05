-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament

-- Players participating in tournament
CREATE TABLE Player (
  player_id SERIAL PRIMARY KEY,
  name      TEXT NOT NULL
);
-- Possible outcomes of matches
CREATE TABLE GameResult (
  game_result_id INTEGER PRIMARY KEY,
  description    TEXT NOT NULL
);
-- Defining possible results
-- Could be additionally extended by values like Unplayed etc.
INSERT INTO GameResult VALUES (1, 'Player 1 won');
INSERT INTO GameResult VALUES (2, 'Player 2 won');
INSERT INTO GameResult VALUES (3, 'Draw');

-- Tournament matches table
CREATE TABLE Match (
  match_id      SERIAL PRIMARY KEY,
  player_one_id INTEGER REFERENCES Player (player_id)          NOT NULL,
  player_two_id INTEGER REFERENCES Player (player_id),
  result_id     INTEGER REFERENCES GameResult (game_result_id) NOT NULL
);

-- View showing how many matches player has played
CREATE VIEW PlayerMatches AS
  SELECT
    player_id,
    SUM(ile) AS matches
  FROM (
         SELECT
           player_id,
           COUNT(player_one_id) AS ile
         FROM Player p LEFT JOIN Match m ON p.player_id = m.player_one_id
         GROUP BY player_id
         UNION ALL
         SELECT
           player_id,
           COUNT(player_two_id) AS ile
         FROM Player p LEFT JOIN Match m ON p.player_id = m.player_two_id
         GROUP BY player_id
       ) s
  GROUP BY player_id;

-- View showing how many matches player has won
CREATE VIEW PlayerWins AS
  SELECT
    player_id,
    SUM(ile) AS wins
  FROM (
         SELECT
           player_id,
           COUNT(player_one_id) AS ile
         FROM Player p LEFT JOIN Match m
             ON p.player_id = m.player_one_id AND m.result_id = '1'
         GROUP BY player_id
         UNION ALL
         SELECT
           player_id,
           COUNT(player_two_id) AS ile
         FROM Player p LEFT JOIN Match m
             ON p.player_id = m.player_two_id AND m.result_id = '2'
         GROUP BY player_id
       ) s
  GROUP BY player_id;

-- View showing how many matches player has tied
CREATE VIEW PlayerTies AS
  SELECT
    player_id,
    SUM(ile) AS ties
  FROM (
         SELECT
           player_id,
           COUNT(player_one_id) AS ile
         FROM Player p LEFT JOIN Match m
             ON p.player_id = m.player_one_id AND m.result_id = '3'
         GROUP BY player_id
         UNION ALL
         SELECT
           player_id,
           COUNT(player_two_id) AS ile
         FROM Player p LEFT JOIN Match m
             ON p.player_id = m.player_two_id AND m.result_id = '3'
         GROUP BY player_id
       ) s
  GROUP BY player_id;

-- View counting how many points players have
-- Created as additional view so we can use ranking function later in query
CREATE VIEW PlayerPoints AS
  SELECT
    pw.player_id,
    wins * 3 + ties AS points
  FROM PlayerWins pw JOIN PlayerTies pt ON pw.player_id = pt.player_id;

-- View showing current tournament standings using views created earlier
CREATE VIEW Standings AS
  SELECT
    pm.player_id,
    name,
    wins,
    ties,
    matches,
    points,
    RANK()
    OVER (
      ORDER BY points DESC, matches, wins DESC) AS ranking
  FROM Player p JOIN PlayerMatches pm ON p.player_id = pm.player_id
    JOIN PlayerTies pt ON p.player_id = pt.player_id
    JOIN PlayerWins pw ON p.player_id = pw.player_id
    JOIN PlayerPoints pp ON p.player_id = pp.player_id;