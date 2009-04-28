import os

class Config:
    "High-level interface for config files manipulations"
    __instance = None
    @classmethod
    def get(cls):
        if Config.__instance is None:
            cls.__instance = cls()
        return cls.__instance
    def __init__(self):
        self.__server = Server.get()
        self.__cfg_fname = opts().cfg_fname
        self.__cfg_fname_new = self.__cfg_fname + '.new'
        self.__dhcp_cfg_fname = opts().dhcp_cfg_fname
        self.__dhcp_cfg_fname_new = self.__dhcp_cfg_fname + '.new'
    def reset(self):
        self.__server.reset()
        exists = os.path.exists
        if exists(self.__cfg_fname): os.unlink(self.__cfg_fname)
        if exists(self.__dhcp_cfg_fname): os.unlink(self.__dhcp_cfg_fname)
    def isConfigured(self):
        exists = os.path.exists
        return exists(self.__cfg_fname) and exists(self.__dhcp_cfg_fname)
    def save(self):
        storage.save(self.__server, open(self.__cfg_fname_new, 'w+'))
        os.rename(self.__cfg_fname_new, self.__cfg_fname)
    def load(self):
        self.__server.reset()
        if not opts().deploy and os.path.exists(self.__cfg_fname):
            storage.load(self.__server, open(self.__cfg_fname))
    def genDHCPCfg(self):
        self.__server.genConfig(open(self.__dhcp_cfg_fname_new, 'w+'))
        os.rename(self.__dhcp_cfg_fname_new, self.__dhcp_cfg_fname)

from options import opts
import storage
from server import Server

