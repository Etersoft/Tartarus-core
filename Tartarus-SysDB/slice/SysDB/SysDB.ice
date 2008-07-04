
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
                            throws UserNotFound, PermissionDenied;
    idempotent UserRecord getByName(string name)
                            throws UserNotFound, PermissionDenied;

    idempotent UserSeq getUsers(IdSeq userIds)
                            throws UserNotFound, PermissionDenied;

    idempotent UserSeq search(string factor, long limit)
                            throws PermissionDenied;

    idempotent long count() throws PermissionDenied;

    idempotent UserSeq get(long limit, long offset)
                            throws PermissionDenied;
};

interface UserManager extends UserReader
{
    idempotent void modify(UserRecord user)
                            throws UserNotFound, PermissionDenied;
    /** uid field from parameter is ignored */
    long create(UserRecord newUser)
                            throws UserAlreadyExists, PermissionDenied;
    void delete(long id) throws UserNotFound, PermissionDenied;
};

interface GroupReader
{
    idempotent GroupRecord getById(long gid)
                            throws GroupNotFound, PermissionDenied;
    idempotent GroupRecord getByName(string name)
                            throws GroupNotFound, PermissionDenied;

    idempotent IdSeq getGroupsForUserId(long uid)
                            throws UserNotFound, PermissionDenied;
    idempotent IdSeq getGroupsForUserName(string name)
                            throws UserNotFound, PermissionDenied;

    idempotent GroupSeq getGroups(IdSeq groupIds)
                            throws GroupNotFound, PermissionDenied;
    idempotent IdSeq getUsers(long gid)
                            throws GroupNotFound, PermissionDenied;


    GroupSeq search(string factor, long limit) throws PermissionDenied;
    idempotent long count() throws PermissionDenied;
    idempotent GroupSeq get(long limit, long offset)
                            throws PermissionDenied;
};

interface GroupManager extends GroupReader
{
    idempotent void setUsers(long gid, IdSeq userIds)
                            throws GroupNotFound, PermissionDenied;
    void addUsers(long gid, IdSeq userIds)
                            throws GroupNotFound, PermissionDenied;
    void delUsers(long gid, IdSeq userIds)
                            throws GroupNotFound, PermissionDenied;

    idempotent void modify(GroupRecord group)
                            throws GroupNotFound, PermissionDenied;

    /** gid field from parameter is ignored */
    long create(GroupRecord newGroup)
                            throws GroupAlreadyExists, PermissionDenied;
    void delete(long id) throws UserNotFound, PermissionDenied;

    void addUserToGroups(long uid, IdSeq groups)
                            throws GroupNotFound, PermissionDenied;

    /** */
    void delUserFromGroups(long uid, IdSeq groups)
                            throws GroupNotFound, PermissionDenied;
};

};
};};

