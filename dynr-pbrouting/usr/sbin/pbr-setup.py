#!/usr/bin/python
#Please make sure the arp-scan package is installed.
import re
import os
import json
import IPy
class RouterTester:
    def __init__(self,inetip):
        self.origgw=None
        self.inetip=inetip
        route=os.popen("/sbin/route -n")
        for line in route.readlines():
            match=re.match("^0\.0\.0\.0\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+0\.0\.0\.0\s",line)
            if (match):
                self.origgw=match.groups()[0]
                os.system("/sbin/route del default")
    def __del__(self):
        if (self.origgw):
            os.system("/sbin/route add default gw "+self.origgw)
    def __call__(self,peer):
        os.system("/sbin/route add default gw "+peer.ip)
        rval=os.system("/bin/ping -W 1 -c 1 "+self.inetip+">/dev/null")
        os.system("/sbin/route del default")
        if (rval == 0):
            return True
        return False

class Peer:
    def __init__(self,interface,ip,mac):
        self.interface=interface
        self.ip=ip
        self.mac=mac

class AllInterfaces:
    def __call__(self):
        devfile=open("/proc/net/dev","r")
        for line in devfile:
            match = re.match("^\s*([a-z]+[0-9]+):",line)
            if (match):
                yield match.groups()[0];

class InterfacePeers:
    def __init__(self,interface):
        self.command="/usr/bin/arp-scan -l -I " + interface
        self.interface=interface
    def __call__(self):
        arpscan = os.popen(self.command)
        for line in arpscan.readlines():
            match = re.match("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)\s",line)
            if (match):
                yield Peer(self.interface,match.groups()[0],match.groups()[1])

class AutoInterfaces:
    def __init__(self,testip):
        all = AllInterfaces()
        test = RouterTester(testip)
        self.routerinterface=None
        self.routers=[]
        maxroutercount=0;
        self.proposedparkip="INVALID"
        self.proposeddnsip="INVALID"
        for interface in all():
            routercount=0
            peercount=0
            routers=[]
            nonrouters=[]
            peers = InterfacePeers(interface)
            for peer in peers():
                peercount=peercount+1
                if test(peer):
                    routers.append(peer)
                    routercount = routercount +1
                else :
                    nonrouters.append(peer)
            if (routercount):
                if (routercount > maxroutercount):
                    maxroutercount=routercount
                    self.routerinterface=interface
                    self.routers=routers
                    if len(nonrouters) > 0:
                        self.proposedparkip=nonrouters[0].ip
                    if len(nonrouters) > 1:
                        self.proposeddnsip=nonrouters[1].ip
    def routerinterface(self):
        return self.routerinterface
    def routers(self):
        for router in self.routers:
            yield router
    def getparkproposal(self):
        return self.proposedparkip
    def getdnsproposal(self):
        return self.proposeddnsip
    def clientinterfaces(self):
        all = AllInterfaces()
        for interface in all():
            if (interface != self.routerinterface):
                yield interface   

class IfConfig:
    def __init__(self,interface):
        ifconfig = os.popen("/sbin/ifconfig " + str(interface))
        self.ips=None
        self.ip=None
        for line in ifconfig.readlines():
            match = re.match(".*inet\s+addr:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*Mask:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",line) 
            if (match):
                self.ip=match.groups()[0]
                self.ips=IPy.IP(match.groups()[0]).make_net(match.groups()[1])
    def __call__(self):
        for ip in self.ips:
            yield ip
    def getIp(self):
        return self.ip
    def getNet(self):
        return str(self.ips)

class PbConfig:
    def __init__(self,autoip,jsonfile):
        self.jsonfile=jsonfile
        self.validgroups=[]
        self.proposedmyip=None
        self.gateways={}
        if os.path.isfile(jsonfile):
            self.auto=None
        else:
            self.auto=AutoInterfaces(autoip)
    def __generateGateways(self):
        gateways=[]
        counter=1
        for router in self.auto.routers:
            gw={};
            gw["name"] = "gateway"+str(counter)
            gw["tableno"] = counter
            counter=counter+1
            gw["ip"]=router.ip
            self.gateways["ip"]=1
            gw["allowedgroups"] = self.validgroups
            gateways.append(gw)
        gw={}
        gw["allowedgroups"] = self.validgroups
        gw["name"] = "parkip"
        gw["ip"]=self.auto.getparkproposal()
        gw["tableno"]=counter
        gateways.append(gw)
        return gateways
    def __generateDevices(self):
        clientifs=[]
        for interface in self.auto.clientinterfaces():
            ifc=IfConfig(interface)
            iface={}
            iface["device"]=interface
            iface["groupname"]=interface+"group"
            iface["ip"]=ifc.getIp()
            iface["net"]=ifc.getNet()
            if (iface["ip"]) :
                clientifs.append(iface)
                self.validgroups.append(iface["groupname"])
        interfaces={}
        interfaces["clients"] = clientifs
        iface={}
        ifr=IfConfig(self.auto.routerinterface)
        iface["device"]=self.auto.routerinterface
        iface["ip"]=ifr.getIp()
        iface["net"]=ifr.getNet()
        iface["groupname"]="loop"
        interfaces["routers"] = iface
        self.proposedmyip=ifr.getIp()
        return interfaces
    def __generateLocalDomainEntry(self):
        entry={}
        entry["serverip"] = self.auto.getdnsproposal()
        if self.proposedmyip:
            entry["myip"] = self.proposedmyip
        else:
            entry["myip"] = "INVALID"
        return entry
    def __generateLocalDomains(self):
        localdns={}
        localdns["LOCAL"] = self.__generateLocalDomainEntry()
        localdns["VPN"] = self.__generateLocalDomainEntry()
        localdns["10.IN-ADDR.ARPA"] = self.__generateLocalDomainEntry()
        localdns["16.172.IN-ADDR.ARPA"] = self.__generateLocalDomainEntry()
        localdns["168.192.IN-ADDR.ARPA"] = self.__generateLocalDomainEntry()
        return localdns
    def __call__(self):
        if not self.auto:
            return False
        config={}
        config["gateways"] = self.__generateGateways()
        config["devices"] = self.__generateDevices()
        config["localdns"] = self.__generateLocalDomains()
        config["disabled"] = 1
        outfile=open(self.jsonfile,"w")
        outfile.write(json.dumps(config,sort_keys=True,indent=4))
        outfile.close()
        os.chmod(self.jsonfile,0755)
        return True

internetip="8.8.8.8"
configfile="/etc/pbrouting.json"

newconfig=PbConfig(internetip,configfile)
if newconfig():
    print "New " + configfile + " generated."
    if os.system("/usr/bin/pbr-checkconfig.py"):
        print "NOTE: You should edit " + configfile + ", fix the above problems and run pbr-checkconfig.py to validate your config is now valid.."
else:
    print "ERROR: existing " + configfile + " is in the way."
