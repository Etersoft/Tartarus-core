#include <core/exceptions.ice>

module Tartarus { module iface {
module DHCP {

sequence<string> StrSeq;

enum HostIdType {
    IDENTITY,
    HARDWARE
};

struct HostId {
    HostIdType type;
    string value;
};

dictionary<string,string> StrStrMap;

interface Scope {
    StrStrMap options();
    void setOption(string key, string value) throws core::Error;
    void unsetOption(string key) throws core::Error;
};


interface Host extends Scope {
    string name();
    HostId id();
};

sequence<Host*> HostSeq;

const int KNOWN = 1;
const int UNKNOWN = 2;

struct IpRange {
    string start;
    string end;
    bool hasValue;
};

interface Range extends Scope {
    string id();
    int caps();
    void setCaps(int caps);
    void addrs(out string start, out string end);
};

sequence<Range*> RangeSeq;

interface Subnet extends Scope {
    string id();
    string cidr();
    RangeSeq ranges();
    Range* getRange(string id) throws core::Error;
    Range* findRange(string addr) throws core::Error;
    Range* addRange(string start, string end, int caps) throws core::Error;
    void delRange(string ip) throws core::Error;
};

sequence<Subnet*> SubnetSeq;

interface Server extends Scope {
    SubnetSeq subnets();
    Subnet* findSubnet(string decl) throws core::Error;
    Subnet* addSubnet(string decl) throws core::Error;
    void delSubnet(string id) throws core::Error;
    HostSeq hosts();
    Host* getHost(string name) throws core::Error;
    Host* addHost(string name, HostId id) throws core::Error;
    void delHost(string name) throws core::Error;
    Range* findRange(string addr) throws core::Error;
    bool isConfigured() throws core::Error;
    void reset() throws core::Error;
};

interface Daemon {
    void start() throws core::Error;
    void stop() throws core::Error;
    bool running();
};

exception KeyError extends core::Error
{
    string key;
};

exception ValueError extends core::Error
{
    string key;
    string value;
};

};
}; };
