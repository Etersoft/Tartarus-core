
#ifndef TARTARUS_IFACE_SYSDB_ICE
#define TARTARUS_IFACE_SYSDB_ICE

#include <core/exceptions.ice>

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

exception UserNotFound extends core::NotFoundError
{
    long id;
};

exception GroupNotFound extends core::NotFoundError
{
    long id;
};


exception UserAlreadyExists extends core::AlreadyExistsError
{
    long id;
};

exception GroupAlreadyExists extends core::AlreadyExistsError
{
    long id;
};


sequence<UserRecord> UserSeq;
sequence<GroupRecord> GroupSeq;
sequence<long> IdSeq;

interface UserReader
{
    idempotent UserRecord getById(long uid)
                            throws core::Error;
    idempotent UserRecord getByName(string name)
                            throws core::Error;

    idempotent UserSeq getUsers(IdSeq userIds)
                            throws core::Error;

    idempotent UserSeq search(string factor, long limit)
                            throws core::Error;

    idempotent long count() throws core::Error;

    idempotent UserSeq get(long limit, long offset)
                            throws core::Error;
};

interface UserManager extends UserReader
{
    idempotent void modify(UserRecord user)
                            throws core::Error;
    /** uid field from parameter is ignored */
    long create(UserRecord newUser)
                            throws core::Error;
    void delete(long id) throws core::Error;
};

interface GroupReader
{
    idempotent GroupRecord getById(long gid)
                            throws core::Error;
    idempotent GroupRecord getByName(string name)
                            throws core::Error;

    idempotent IdSeq getGroupsForUserId(long uid)
                            throws core::Error;
    idempotent IdSeq getGroupsForUserName(string name)
                            throws core::Error;

    idempotent GroupSeq getGroups(IdSeq groupIds)
                            throws core::Error;
    idempotent IdSeq getUsers(long gid)
                            throws core::Error;

    GroupSeq search(string factor, long limit) throws core::Error;
    idempotent long count() throws core::Error;
    idempotent GroupSeq get(long limit, long offset)
                            throws core::Error;
};

interface GroupManager extends GroupReader
{
    idempotent void setUsers(long gid, IdSeq userIds)
                            throws core::Error;
    void addUsers(long gid, IdSeq userIds)
                            throws core::Error;
    void delUsers(long gid, IdSeq userIds)
                            throws core::Error;

    idempotent void modify(GroupRecord group)
                            throws core::Error;

    /** gid field from parameter is ignored */
    long create(GroupRecord newGroup)
                            throws core::Error;
    void delete(long id) throws core::Error;

    void addUserToGroups(long uid, IdSeq groups)
                            throws core::Error;

    /** */
    void delUserFromGroups(long uid, IdSeq groups)
                            throws core::Error;
};

};
};};

#endif TARTARUS_IFACE_SYSDB_ICE

