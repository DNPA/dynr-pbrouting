#!/usr/bin/python
import re
import json
import os
import sys
import curses
configpath="/etc/pbrouting.json"
curses.setupterm()
setaf = curses.tigetstr('setaf')
if not setaf:
    setaf=""
FAIL = curses.tparm(setaf, curses.COLOR_RED)
WARNING = curses.tparm(setaf, curses.COLOR_MAGENTA)
OKGREEN = curses.tparm(setaf, curses.COLOR_GREEN)
ENDC = curses.tigetstr('sgr0')

if (not os.path.isfile(configpath)):
    print FAIL + "ERROR: you must first run pbr-setup.py to generate a configuration." + ENDC
    sys.exit(1)
try:
    infile=open(configpath,"r")
except IOError:
    print FAIL + "ERROR: Unexpected IO error trying to open existing config " + configpath + ENDC
    sys.exit(2)
try:
    conf=json.load(infile)
except ValueError:
    print FAIL + "ERROR: The content of " + configpath + " is not valid json." + ENDC
    sys.exit(3)
infile.close()
if not conf.has_key("gateways"):
    print FAIL + "ERROR: " + configpath + " does not contain a 'gateways' section." + ENDC
    sys.exit(33)
gateways=conf["gateways"]
if (not gateways):
    print FAIL + "ERROR: " + configpath + " has an empty 'gateways' section." + ENDC
    sys.exit(4)
if not conf.has_key("devices"):
    print FAIL + "ERROR:" + configpath + " does not contain a 'devices' section." + ENDC
    sys.exit(34)
devices=conf["devices"]
if (not devices):
    print FAIL + "ERROR:" + configpath + " has an empty 'devices' section." + ENDC
    sys.exit(5)
if not devices.has_key("clients"):
    print FAIL + "ERROR: " + configpath + " does not contain a 'devices::clients' section." + ENDC
    sys.exit(35)
clients=devices["clients"]
if (not clients):
    print FAIL + "ERROR: " + configpath + " has an empty 'devices::clients' section." + ENDC
    sys.exit(6)
if (len(clients) < 1):
    print FAIL + "ERROR: " + configpath + " has an empty 'devices.clients' section." + ENDC
    sys.exit(7)
realdevices=clients
if not devices.has_key("routers"):
    print FAIL + "ERROR: " + configpath + " does not contain a 'devices::routers' section." + ENDC
    sys.exit(36)
routerdev=devices["routers"]
if (not routerdev):
    print FAIL + "ERROR: " + configpath + " contains an empty 'devices::routers' section." + ENDC
    sys.exit(8)
realdevices.append(routerdev)
if not conf.has_key("localdns"):
    print FAIL + "ERROR: " + configpath + " does not contain a 'localdns' section." + ENDC
    sys.exit(37)
localdomains=conf["localdns"]
if (not localdomains) :
    print FAIL + "ERROR: " + configpath + " does not contain a 'localdns' section." + ENDC
    sys.exit(28)
unique={}
unique["device"] = {}
unique["groupname"] = {}
unique["ip"] = {}
unique["net"] = {}
for realdevice in realdevices:
    if (not realdevice.has_key("device")):
        print FAIL + "ERROR: " + configpath + " contains a device definition without a device." + ENDC
        sys.exit(9)
    name=realdevice["device"]
    if (not realdevice.has_key("groupname")):
        print FAIL + "ERROR: " + configpath + " no groupname defined for " + name + " device." + ENDC
        sys.exit(11)
    group=realdevice["groupname"]
    if (not realdevice.has_key("ip")):
        print FAIL + "ERROR: " + configpath + " no ip defined for " + name + " device." + ENDC
        sys.exit(12)
    ip=realdevice["ip"]
    if (not realdevice.has_key("net")):
        print FAIL + "ERROR: " + configpath + " no net defined for " + name + " device." + ENDC
        sys.exit(13)
    net=realdevice["net"]
    if (unique["device"].has_key(name)):
        print FAIL + "ERROR: device " + name + " is defined more than once." + ENDC
        sys.exit(14)
    unique["device"][name]=1
    if (unique["groupname"].has_key(group)):
        print FAIL + "ERROR: the group " + group + "is defined on more than one network device." + ENDC
        sys.exit(15) 
    unique["groupname"][group]=1
    if (unique["ip"].has_key(ip)):
        print FAIL + "ERROR: the ip " +  ip + " is defined on more than one network devices." + ENDC
        sys.exit(16)
    unique["ip"][ip]=1
    if (unique["net"].has_key(net)):
        print FAIL + "ERROR: the network " + net + " is defined on more than one network device." + ENDC
        sys.exit(17)
    unique["net"][net]=1
    match=re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",str(ip))
    if (not match) :
        print FAIL + "ERROR: device " + name + " has an invalid IP defined for it." + ENDC
        sys.exit(18)
    match=re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$",str(net))
    if (not match):
        print FAIL + "ERROR: device " + name + " has an invalid NET defined for it." + ENDC
        sys.exit(19)
if (len(gateways) < 1):
    print FAIL + "ERROR: " + configpath + " not a single gateway defined." + ENDC
unique["tableno"]={}
unique["name"]={}
for gateway in gateways:
    if (not gateway.has_key("ip")):
        print FAIL + "ERROR: " + configpath + " gateway defined without an IP." + ENDC
        sys.exit(20)
    ip=gateway["ip"]
    if (not gateway.has_key("name")):
        print FAIL + "ERROR: " + configpath + " gateway " + ip + " has no name defined for it." + ENDC
        sys.exit(21)
    if (not gateway.has_key("tableno")):
        print FAIL + "ERROR: " + configpath + " gateway " + ip + " has no tableno defined for it." + ENDC
        sys.exit(22)
    if (unique["ip"].has_key(ip)):
        print FAIL + "ERROR: " + configpath + " gateway " + ip + " is defined more than once." + ENDC
        sys.exit(23)
    unique["ip"][ip]=1
    if (unique["tableno"].has_key(gateway["tableno"])):
        print FAIL + "ERROR: " + configpath + " gateway " + ip + " has a non uniqueu table number defined for it." + ENDC
        sys.exit(24)
    unique["tableno"][gateway["tableno"]]=1
    if (unique["name"].has_key(gateway["name"])):
        print FAIL + "ERROR: " +configpath + " gateway " + ip + " has a non unique name defined for it." + ENDC
        sys.exit(25)
    unique["name"][gateway["name"]]=1
    match=re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",ip)
    if (not match):
        if (ip == "INVALID"):
            print WARNING + "WARNING: " + configpath + " stil has an INVALID definition for the IP adress of " + gateway["name"] + "." + ENDC
            print WARNING + "         You will need to fix this manualy before dynr-pbrouting can succesfully be started."  + ENDC
        else :
            print FAIL + "ERROR: " + configpath + " gateway " + gateway["name"] + " has an invalid IP: '" + ip + "'" + ENDC
        sys.exit(26)
    for group in gateway["allowedgroups"]:
        if (not unique["groupname"].has_key(group)):
            print FAIL +"ERROR: " + configpath + " gateway " + ip + " is defined of the group " + group + " that has no definition with any network device." + ENDC
            sys.exit(27)
for domain in localdomains:
    ipinfo=localdomains[domain]
    if not ipinfo.has_key("myip"):
        print FAIL +"ERROR: " + configpath + " has got a localdns section defined with no 'myip' subsection." + ENDC
        sys.exit(32)
    if not ipinfo.has_key("serverip"):
        print FAIL +"ERROR: " + configpath + " has got a localdns section defined with no 'serverip' subsection." + ENDC
    myip=ipinfo["myip"]
    match=re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",myip)
    if (not match):
        print FAIL +"ERROR: " + configpath + " contains an invalid IP address for myip in a localdns section." + ENDC
        sys.exit(29)
    serverip=ipinfo["serverip"]
    match=re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",serverip)
    if (not match):
        print FAIL +"ERROR: " + configpath + " contains an invalid IP address for serverip in a localdns section." + ENDC
        sys.exit(30)
if not conf.has_key("disabled"):
    print WARNING + "WARNING: " + configpath + " has no 'disabled' section defined for it." + ENDC
disabled=conf["disabled"]
if disabled == 1:
    print WARNING + "WARNING: " + configpath + " is still set to 'disabled'. Validate the config is OK and set disabled to '0'." + ENDC
    sys.exit(31) 
print OKGREEN + "OK: Everything is iree." + ENDC
sys.exit(0)
