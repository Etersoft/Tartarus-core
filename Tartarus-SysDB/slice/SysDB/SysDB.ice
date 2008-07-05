
module Tartarus { module iface {

module SysDB
{

struct UserRecord
{
    long uid;
    long gid;
    string name;
    string fullName;
    string shell;
};

struct GroupRecord
{
    long gid;
    string name;
    string description;
};

exception Error
{
    string reason;
};

exception ConfigError extends Error
{
    string property;
};

exception NotFound extends Error
{
};

exception UserNotFound extends NotFound
{
    long id;
};

exception GroupNotFound extends NotFound
{
    long id;
};

exception PermissionDenied extends Error
{
};

exception AlreadyExists extends Error
{
};

exception UserAlreadyExists extends AlreadyExists
{
    long id;
};

exception GroupAlreadyExists extends AlreadyExists
{
    long id;
};

exception DBError extends Error
{
    string message;
};

sequence<UserRecord> UserSeq;
sequence<GroupRecord> GroupSeq;
sequence<long> IdSeq;

interface UserReader
{
    idempotent UserRecord getById(long uid)
                            throws Error;
    idempotent UserRecord getByName(string name)
                            throws Error;

    idempotent UserSeq getUsers(IdSeq userIds)
                            throws Error;

    idempotent UserSeq search(string factor, long limit)
                            throws Error;

    idempotent long count() throws Error;

    idempotent UserSeq get(long limit, long offset)
                            throws Error;
};

interface UserManager extends UserReader
{
    idempotent void modify(UserRecord user)
                            throws Error;
    /** uid field from parameter is ignored */
    long create(UserRecord newUser)
                            throws Error;
    void delete(long id) throws Error;
};

interface GroupReader
{
    idempotent GroupRecord getById(long gid)
                            throws Error;
    idempotent GroupRecord getByName(string name)
                            throws Error;

    idempotent IdSeq getGroupsForUserId(long uid)
                            throws Error;
    idempotent IdSeq getGroupsForUserName(string name)
                            throws Error;

    idempotent GroupSeq getGroups(IdSeq groupIds)
                            throws Error;
    idempotent IdSeq getUsers(long gid)
                            throws Error;


    GroupSeq search(string factor, long limit) throws Error;
    idempotent long count() throws Error;
    idempotent GroupSeq get(long limit, long offset)
                            throws Error;
};

interface GroupManager extends GroupReader
{
    idempotent void setUsers(long gid, IdSeq userIds)
                            throws Error;
    void addUsers(long gid, IdSeq userIds)
                            throws Error;
    void delUsers(long gid, IdSeq userIds)
                            throws Error;

    idempotent void modify(GroupRecord group)
                            throws Error;

    /** gid field from parameter is ignored */
    long create(GroupRecord newGroup)
                            throws Error;
    void delete(long id) throws Error;

    void addUserToGroups(long uid, IdSeq groups)
                            throws Error;

    /** */
    void delUserFromGroups(long uid, IdSeq groups)
                            throws Error;
};

};
};};

