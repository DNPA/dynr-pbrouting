#!/bin/bash
fakeroot dpkg-deb --build dynr-pbrouting dynr-pbrouting_`grep Version dynr-pbrouting/DEBIAN/control |sed -e 's/.* //'`_`grep Architecture dynr-pbrouting/DEBIAN/control |sed -e 's/.* //'`.deb
