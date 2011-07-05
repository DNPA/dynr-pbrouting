#!/usr/bin/python
import re
import json
import os
import sys

class IpRoute:
    def __init__(self):
        self.binary="/sbin/ip"
    def __cmd(self,cmd):
        command = self.binary + " " + cmd
        print "# " + command
        os.system(command)
    def __route(self,cmd):
        self.__cmd("route " + cmd)
    def __rule(self,cmd):
        self.__cmd("rule " + cmd)
    def flushTable(self,tableno):
        self.__route("flush table " + str(tableno))
    def flushCache(self):
        self.__route("flush cache")
    def delNetRule(self,net):
        self.__rule("del from " + net) 
    def delHostRule(self,host):
        net=host + "/32"
        self.delNetRule(net)

if os.system("/usr/bin/pbr-checkconfig.py"):
    sys.exit(1)
infile=open("/etc/pbrouting.json","r")
conf=json.load(infile)
infile.close()
gateways=conf["gateways"]
iproute=IpRoute()
for gateway in gateways:
    tableno=gateway["tableno"]
    ip=gateway["ip"]
    name=gateway["name"]
    if (name=="parkip"):
        parkiptable=tableno
    iproute.flushTable(tableno)
iproute.delHostRule(conf["devices"]["routers"]["ip"])
clientinterfaces=conf["devices"]["clients"]
for inter in clientinterfaces:
    iproute.delHostRule(inter["ip"])
    iproute.delNetRule(inter["net"])
iproute.flushCache()
