#!/usr/bin/env python
# -*- coding: utf-8 -*-

# You must initialize the gobject/dbus support for threading
# before doing anything.
import gobject
import os
import time

gobject.threads_init()

from dbus import glib
glib.init_threads()

# Create a session bus.
import dbus
bus = dbus.SessionBus()

remote_object = bus.get_object("org.kde.kstars", "/KStars/Ekos/Scheduler")
iface = dbus.Interface(remote_object, 'org.kde.kstars.Ekos.Scheduler')
iface.loadScheduler("/home/stellarmate/Pictures/daily.esl")
