-- ============================================================================
-- SCENARIO 2: IPL PLAYER PERFORMANCE STREAKS (2024 SEASON)
-- Description:
-- Identifies players who scored 30+ runs in at least 3 consecutive matches.
-- Returns the player's name and the date the scoring streak commenced.
-- Utilizes the Island-and-Gaps window function pattern for consecutive streak grouping.
-- ============================================================================

-- Drop existing table if present
DROP TABLE IF EXISTS ipl_match_scores;

-- 1. Table Schema
CREATE TABLE ipl_match_scores (
    match_id INT,
    match_date DATE NOT NULL,
    player_id VARCHAR(20) NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    team VARCHAR(50),
    opponent VARCHAR(50),
    runs_scored INT NOT NULL,
    balls_faced INT,
    PRIMARY KEY (match_id, player_id)
);

-- 2. Seed Data (IPL 2024 Season Match-by-Match Innings)
INSERT INTO ipl_match_scores (match_id, match_date, player_id, player_name, team, opponent, runs_scored, balls_faced) VALUES
-- Virat Kohli (RCB):
-- Match 6: 77 (2024-03-25)
-- Match 10: 83 (2024-03-29)
-- Match 15: 22 (2024-04-02) -> streak reset
-- Match 19: 113 (2024-04-06) -> STREAK 1 COMMENCES (4 matches: 113, 42, 42, 51)
-- Match 25: 42 (2024-04-11)
-- Match 30: 42 (2024-04-15)
-- Match 36: 51 (2024-04-21)
-- Match 41: 18 (2024-04-25) -> streak ended
(6,  '2024-03-25', 'P_VK18', 'Virat Kohli', 'RCB', 'PBKS', 77,  49),
(10, '2024-03-29', 'P_VK18', 'Virat Kohli', 'RCB', 'KKR',  83,  59),
(15, '2024-04-02', 'P_VK18', 'Virat Kohli', 'RCB', 'LSG',  22,  16),
(19, '2024-04-06', 'P_VK18', 'Virat Kohli', 'RCB', 'RR',   113, 72),
(25, '2024-04-11', 'P_VK18', 'Virat Kohli', 'RCB', 'MI',   42,  29),
(30, '2024-04-15', 'P_VK18', 'Virat Kohli', 'RCB', 'SRH',  42,  20),
(36, '2024-04-21', 'P_VK18', 'Virat Kohli', 'RCB', 'KKR',  51,  36),
(41, '2024-04-25', 'P_VK18', 'Virat Kohli', 'RCB', 'SRH',  18,  13),

-- Ruturaj Gaikwad (CSK):
-- Match 22: 67 (2024-04-08) -> STREAK COMMENCES (5 matches: 67, 69, 43, 108, 98)
-- Match 29: 69 (2024-04-14)
-- Match 34: 43 (2024-04-19)
-- Match 39: 108 (2024-04-23)
-- Match 46: 98 (2024-04-28)
-- Match 49: 1 (2024-05-01) -> streak ended
(22, '2024-04-08', 'P_RG31', 'Ruturaj Gaikwad', 'CSK', 'KKR', 67,  58),
(29, '2024-04-14', 'P_RG31', 'Ruturaj Gaikwad', 'CSK', 'MI',  69,  40),
(34, '2024-04-19', 'P_RG31', 'Ruturaj Gaikwad', 'CSK', 'LSG', 43,  34),
(39, '2024-04-23', 'P_RG31', 'Ruturaj Gaikwad', 'CSK', 'LSG', 108, 60),
(46, '2024-04-28', 'P_RG31', 'Ruturaj Gaikwad', 'CSK', 'SRH', 98,  54),
(49, '2024-05-01', 'P_RG31', 'Ruturaj Gaikwad', 'CSK', 'PBKS', 1,   2),

-- Rohit Sharma (MI):
-- Match 5: 43 (2024-03-24)
-- Match 8: 26 (2024-03-27) (<30)
-- Match 14: 0 (2024-04-01) (<30)
-- Match 20: 49 (2024-04-07) -> STREAK COMMENCES (3 matches: 49, 38, 105)
-- Match 25: 38 (2024-04-11)
-- Match 29: 105 (2024-04-14)
-- Match 33: 6 (2024-04-18) -> streak ended
(5,  '2024-03-24', 'P_RS45', 'Rohit Sharma', 'MI', 'GT',  43,  29),
(8,  '2024-03-27', 'P_RS45', 'Rohit Sharma', 'MI', 'SRH', 26,  12),
(14, '2024-04-01', 'P_RS45', 'Rohit Sharma', 'MI', 'RR',   0,   1),
(20, '2024-04-07', 'P_RS45', 'Rohit Sharma', 'MI', 'DC',  49,  27),
(25, '2024-04-11', 'P_RS45', 'Rohit Sharma', 'MI', 'RCB', 38,  24),
(29, '2024-04-14', 'P_RS45', 'Rohit Sharma', 'MI', 'CSK', 105, 63),
(33, '2024-04-18', 'P_RS45', 'Rohit Sharma', 'MI', 'PBKS', 6,   8),

-- KL Rahul (LSG):
-- Match 4: 58 (2024-03-24)
-- Match 11: 15 (2024-03-30) (<30)
-- Match 21: 33 (2024-04-07) -> STREAK COMMENCES (3 matches: 33, 39, 82)
-- Match 26: 39 (2024-04-12)
-- Match 34: 82 (2024-04-19)
-- Match 39: 16 (2024-04-23) -> streak ended
(4,  '2024-03-24', 'P_KL01', 'KL Rahul', 'LSG', 'RR',  58, 44),
(11, '2024-03-30', 'P_KL01', 'KL Rahul', 'LSG', 'PBKS', 15,  9),
(21, '2024-04-07', 'P_KL01', 'KL Rahul', 'LSG', 'GT',  33, 31),
(26, '2024-04-12', 'P_KL01', 'KL Rahul', 'LSG', 'DC',  39, 22),
(34, '2024-04-19', 'P_KL01', 'KL Rahul', 'LSG', 'CSK', 82, 53),
(39, '2024-04-23', 'P_KL01', 'KL Rahul', 'LSG', 'CSK', 16, 14),

-- Glenn Maxwell (RCB) - Control case: No 3-match streak
(1,  '2024-03-22', 'P_GM32', 'Glenn Maxwell', 'RCB', 'CSK',  0,  1),
(6,  '2024-03-25', 'P_GM32', 'Glenn Maxwell', 'RCB', 'PBKS', 3,  5),
(10, '2024-03-29', 'P_GM32', 'Glenn Maxwell', 'RCB', 'KKR', 28, 19),
(15, '2024-04-02', 'P_GM32', 'Glenn Maxwell', 'RCB', 'LSG',  0,  2);

-- 3. SQL Query: Island-and-Gaps Window Functions
-- Step A: Sequentially rank every match played by the player.
-- Step B: Sequentially rank only qualifying matches (runs_scored >= 30).
-- Step C: Compute gap identifier (match_seq - qualifying_seq).
--         Consecutive 30+ matches share the identical streak_group_id!
-- Step D: Filter groups having COUNT(*) >= 3, extract MIN(match_date) as commencement date.

WITH player_match_sequence AS (
    SELECT 
        match_id,
        match_date,
        player_id,
        player_name,
        runs_scored,
        ROW_NUMBER() OVER (
            PARTITION BY player_id 
            ORDER BY match_date, match_id
        ) AS overall_match_seq
    FROM ipl_match_scores
),
qualifying_matches AS (
    SELECT 
        match_id,
        match_date,
        player_id,
        player_name,
        runs_scored,
        overall_match_seq,
        ROW_NUMBER() OVER (
            PARTITION BY player_id 
            ORDER BY match_date, match_id
        ) AS qualifying_seq,
        -- Island identifier: remains constant across consecutive qualifying matches
        (overall_match_seq - ROW_NUMBER() OVER (
            PARTITION BY player_id 
            ORDER BY match_date, match_id
        )) AS streak_group_id
    FROM player_match_sequence
    WHERE runs_scored >= 30
),
streaks_aggregated AS (
    SELECT 
        player_name,
        MIN(match_date) AS streak_commenced_date,
        MAX(match_date) AS streak_concluded_date,
        COUNT(*) AS consecutive_matches,
        GROUP_CONCAT(runs_scored, ', ') AS scores_in_streak
    FROM qualifying_matches
    GROUP BY player_id, player_name, streak_group_id
    HAVING COUNT(*) >= 3
)
SELECT 
    player_name,
    streak_commenced_date,
    consecutive_matches,
    streak_concluded_date,
    scores_in_streak
FROM streaks_aggregated
ORDER BY streak_commenced_date, player_name;
