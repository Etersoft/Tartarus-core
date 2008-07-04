
CREATE TABLE users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR UNIQUE NOT NULL,
    fullname    VARCHAR DEFAULT NULL,
    shell       VARCHAR DEFAULT "/bin/bash"
);

CREATE TABLE groups (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR UNIQUE NOT NULL,
    description VARCHAR DEFAULT NULL
);

CREATE TABLE group_entries (
    id          INTEGER PRIMARY KEY,
    userid      INTEGER NOT NULL,
    groupid     INTEGER NOT NULL,
    is_primary  BOOLEAN DEFAULT NULL,
    UNIQUE (userid, groupid),
    UNIQUE (userid, is_primary)
);

/* values for group_entries.is_primary:
    NULL      -- ordinary group (the default)
    1 (true)  -- primary group
    0 (false) -- reserved for future use
    other     -- illegal
*/

