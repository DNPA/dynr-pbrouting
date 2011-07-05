#!/usr/bin/env python

# Copyright (C) 2004-2006 Red Hat Inc. <http://www.redhat.com/>
# Copyright (C) 2005-2007 Collabora Ltd. <http://www.collabora.co.uk/>
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
import dbus

def main():
    if len(sys.argv) < 3:
        print "Usage:"
        print "       pbr-setgateway.py <workstationip> <gatewayip>"
        print
        sys.exit(0)  
    bus = dbus.SystemBus()
    try:
        remote_object = bus.get_object("nl.dnpa.pbr.GatewayManager",
                                       "/GatewayManager")
        ok = remote_object.setGateway(sys.argv[1],sys.argv[2],
            dbus_interface = "nl.dnpa.pbr.GatewayManager")
    except dbus.DBusException:
        print "ERROR: Dbus operation not permitted (by default  members of the group 'pbrgwman' are allowed to send messages to the pbr daemon)." 
        print "You may need to do the following things to get this tool to work for the current user:"
        print " * Add the user to the group pbrgwman."
        print " * Restart the dbus service (or reboot your system."
        print " * (unless you rebooted) log out and log in again."
        sys.exit(1)
    if (not ok):
        print "ERROR: Operation failed. The supplied IP adresses were not in sysnc with those configured"
        sys.exit(2)
    else:
        print "OK"


if __name__ == '__main__':
    main()
