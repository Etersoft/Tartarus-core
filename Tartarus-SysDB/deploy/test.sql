BEGIN TRANSACTION;
CREATE TABLE users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR UNIQUE NOT NULL,
    fullname    VARCHAR DEFAULT NULL,
    shell       VARCHAR DEFAULT "/bin/bash"
);
INSERT INTO "users" VALUES(1,'user1','user1','/bin/bash');
INSERT INTO "users" VALUES(2,'user2','user2','/bin/bash');
INSERT INTO "users" VALUES(3,'user3','user3','/bin/bash');
DELETE FROM sqlite_sequence;
INSERT INTO "sqlite_sequence" VALUES('groups',3);
INSERT INTO "sqlite_sequence" VALUES('users',7);
CREATE TABLE groups (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR UNIQUE NOT NULL,
    description VARCHAR DEFAULT NULL
);
INSERT INTO "groups" VALUES(1,'group1','group1');
INSERT INTO "groups" VALUES(2,'group2','group2');
INSERT INTO "groups" VALUES(3,'group3','group3');
CREATE TABLE group_entries (
    id          INTEGER PRIMARY KEY,
    userid      INTEGER NOT NULL,
    groupid     INTEGER NOT NULL,
    is_primary  BOOLEAN DEFAULT NULL,
    UNIQUE (userid, groupid),
    UNIQUE (userid, is_primary)
);
INSERT INTO "group_entries" VALUES(1,1,1,1);
INSERT INTO "group_entries" VALUES(2,2,1,1);
INSERT INTO "group_entries" VALUES(3,3,3,1);
INSERT INTO "group_entries" VALUES(4,3,2,NULL);
INSERT INTO "group_entries" VALUES(5,1,2,NULL);
COMMIT;

