BEGIN TRANSACTION;
CREATE TABLE groups (
    gid INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR UNIQUE NOT NULL,
    description VARCHAR DEFAULT "" NOT NULL ON CONFLICT REPLACE
);
INSERT INTO "groups" VALUES(1,'netadmins','Network administrators');
INSERT INTO "groups" VALUES(2,'netusers','Network users');
DELETE FROM sqlite_sequence;
INSERT INTO "sqlite_sequence" VALUES('groups',2);
INSERT INTO "sqlite_sequence" VALUES('users',1);
CREATE TABLE users (
    uid INTEGER PRIMARY KEY AUTOINCREMENT,
    gid INTEGER NOT NULL,
    name VARCHAR UNIQUE NOT NULL,
    fullname VARCHAR DEFAULT "" NOT NULL ON CONFLICT REPLACE,
    shell VARCHAR DEFAULT "/bin/bash"
        NOT NULL ON CONFLICT REPLACE
);
INSERT INTO "users" VALUES(1,1,'sysadmin','System administrator','/bin/bash');
CREATE TABLE real_group_entries (
    uid INTEGER NOT NULL,
    gid INTEGER NOT NULL,
    UNIQUE (uid, gid)
);
INSERT INTO "real_group_entries" VALUES(1,2);
CREATE VIEW group_entries AS
    SELECT uid, gid, 1 AS is_primary FROM users
    UNION ALL
    SELECT uid, gid, 0 AS is_primary FROM real_group_entries;
CREATE TRIGGER on_user_add
BEFORE INSERT ON users
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, "You can't add user to non-existant group")
        WHERE (SELECT gid FROM groups WHERE gid = NEW.gid) IS NULL;
END;
CREATE TRIGGER on_user_change
BEFORE UPDATE ON users
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, "You can't add user to non-existant group")
        WHERE (SELECT gid FROM groups WHERE gid = NEW.gid) IS NULL;
    DELETE FROM real_group_entries
        WHERE real_group_entries.gid == NEW.gid;
END;
CREATE TRIGGER on_user_deletion
BEFORE DELETE ON users
FOR EACH ROW BEGIN
    DELETE FROM real_group_entries WHERE real_group_entries.uid == OLD.uid;
END;
CREATE TRIGGER on_group_deletion
BEFORE DELETE ON groups
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, "You can't delete group which is primary for some users")
        FROM users WHERE users.gid == OLD.gid;
    DELETE FROM real_group_entries WHERE real_group_entries.gid == OLD.gid;
END;
CREATE TRIGGER on_adding_user_to_group
BEFORE INSERT ON real_group_entries
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, "You can't add non-existant user to group")
        WHERE (SELECT uid FROM users WHERE uid = NEW.uid) IS NULL;
    SELECT RAISE(ABORT, "You can't add user to non-existant group")
        WHERE (SELECT gid FROM groups WHERE gid = NEW.gid) IS NULL;
    SELECT RAISE(ABORT, "You can't add a user to the group more than once")
        FROM group_entries
        WHERE group_entries.uid == NEW.uid AND group_entries.gid == NEW.gid;
END;
COMMIT;
