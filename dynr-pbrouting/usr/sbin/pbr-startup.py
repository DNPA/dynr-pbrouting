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
    def setVia(self,tableno,gateway):
        self.__route("add 0.0.0.0/0 via " + str(gateway) + " table " + str(tableno))
    def addNetRule(self,net,table,prio):
        self.__rule("add from " + net + " table " + str(table) + " prio " + str(prio)) 
    def addHostRule(self,host,table,prio):
        net=host + "/32"
        self.addNetRule(net,table,prio)

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
    iproute.setVia(tableno,ip)
iproute.addHostRule(conf["devices"]["routers"]["ip"],"main",19)
clientinterfaces=conf["devices"]["clients"]
for inter in clientinterfaces:
    iproute.addHostRule(inter["ip"],"main",19)
    iproute.addNetRule(inter["net"],parkiptable,20)
iproute.flushCache()
