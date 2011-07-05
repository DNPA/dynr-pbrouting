#!/usr/bin/python

# Copyright (C) 2004-2006 Red Hat Inc. <http://www.redhat.com/>
# Copyright (C) 2005-2007 Collabora Ltd. <http://www.collabora.co.uk/>
# Copyright (C) 2011 Dutch national police agency (KLPD)
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use, copy,
# modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import sys
import gobject
import os
import json
import dbus
import dbus.service
import dbus.mainloop.glib
import IPy
import daemon

class ConfigHelper:
    def __init__(self,config):
        self.config=config
    def getWorkstationGroup(self,workstationip):
        try:
            wsip=IPy.IP(workstationip)
        except ValueError:
            return None
        for clientnet in self.config["devices"]["clients"]:
            netrange=IPy.IP(clientnet["net"])
            if (netrange.overlaps(wsip)):
                return clientnet["groupname"]
        return None
    def checkGroupAllowed(self,clientgroup,gatewayip):
        for gateway in self.config["gateways"]:
            if (gateway["ip"] == gatewayip):
                for group in gateway["allowedgroups"]:
                    if group == clientgroup:
                        return True
        return False
    def getTableNo(self,gwip):
        for gateway in self.config["gateways"]:
            if (gateway["ip"] == gwip):
                return gateway["tableno"]
    def getTable(self,wsip,gwip):
        group=self.getWorkstationGroup(wsip)
        if group:
            if self.checkGroupAllowed(group,gwip):
                return self.getTableNo(gwip)
        return 0
    

class GatewayManager(dbus.service.Object):
    def __init__(self,object_path,config):
        name = dbus.service.BusName("nl.dnpa.pbr.GatewayManager", dbus.SystemBus())
        self.confighelper=ConfigHelper(config)
        dbus.service.Object.__init__(self, dbus.SystemBus(), object_path)
    @dbus.service.method("nl.dnpa.pbr.GatewayManager",
                         in_signature='ss', out_signature='b')
    def setGateway(self, workstation, gateway):
        tableno=self.confighelper.getTable(workstation, gateway)
        if tableno == 0:
            print "denied"
            return False
        os.system("/sbin/ip rule del from " + workstation + "/32")
        os.system("/sbin/ip rule add from " + workstation + "/32 table " + str(tableno))
        return True

if __name__ == '__main__':
    if os.system("/usr/bin/pbr-checkconfig.py"):
        sys.exit(1)
    with daemon.DaemonContext():
        infile=open("/etc/pbrouting.json","r")
        config=json.load(infile)
        infile.close()    
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        name = dbus.service.BusName("nl.dnpa.pbr.GatewayManager", dbus.SystemBus())
        object = GatewayManager('/GatewayManager',config)
        mainloop = gobject.MainLoop()
        mainloop.run()
