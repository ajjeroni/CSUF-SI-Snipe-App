-- Pre-populate the leaderboard with existing points.
-- One row per (guild_id, user_id). Replace the placeholder IDs and
-- counts below with your real values.
--
-- ON CONFLICT makes this safe to re-run: if a row already exists for
-- that guild+user, its points are OVERWRITTEN with the value here.
-- (Change to `points = points + excluded.points` if you'd rather add.)

INSERT INTO leaderboard (guild_id, user_id, points) VALUES
    ('1539757992541552664', '673607126647832620', 24), -- Adam
    ('1539757992541552664', '749335451151761408', 22), -- Samuel
    ('1539757992541552664', '1019903041639555083', 17), -- Adan
    ('1539757992541552664', '1540086677501116556', 16), -- Isa
    ('1539757992541552664', '710919723700977766', 9), -- Elle
    ('1539757992541552664', '777308706081603606', 8), -- Erica
    ('1539757992541552664', '742961299159384115', 7), -- Vic
    ('1539757992541552664', '415355721270558720', 7), -- Nicole
    ('1539757992541552664', '775814641967824986', 6), -- Leigham
    ('1539757992541552664', '1464471410540810240', 5), -- Iris
    ('1539757992541552664', '534519599358541824', 4), -- Jackson
    ('1539757992541552664', '1539791945335963662', 3), -- Grant
    ('1539757992541552664', '714311119367569440', 3), -- Luis
    ('1539757992541552664', '1539863255151808512', 3), -- Faith
    ('1539757992541552664', '1084690458762018877', 2), -- Sawyer
    ('1539757992541552664', '688525285880365106', 2), -- Emily
    ('1539757992541552664', '276581786522484737', 2), -- Justin
    ('1539757992541552664', '1222732012356374608', 1), -- Bessem
    ('1539757992541552664', '1024169898894696558', 1), -- Madi
    ('1539757992541552664', '914710150940598292', 1) -- Ava
ON CONFLICT (guild_id, user_id)
DO UPDATE SET points = excluded.points;


