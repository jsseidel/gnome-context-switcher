#!/usr/bin/env python3

#############################################################################
# This is a work in progress.
#
# TODO:
#   + Make AppIndicator3 menu dynamic:
#       https://askubuntu.com/questions/751608/how-can-i-write-a-dynamically-updated-panel-app-indicator
#   + Convert contextswitch.sh Bash script to python
#   + Add ability to create new contexts in the AppIndicator3 menu
#   + Add ability to delete contexts in the AppIndicator3 menu
#############################################################################

__all__ = ('CSIndicator')

import os
import signal
import json
import sys

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk
from gi.repository import AppIndicator3
from gi.repository import Notify

from subprocess import Popen, PIPE

APPINDICATOR_ID = 'ContextSwitcherIndicator'

class CSIndicator():
    def __init__(self, contextswitch_path):
        self.contextswitch_path = contextswitch_path
        self.app = "Context Switcher"
        icon_path = os.path.dirname(os.path.realpath(__file__)) + "/csindicator.png"
        self.indicator = AppIndicator3.Indicator.new(APPINDICATOR_ID, os.path.abspath(icon_path), AppIndicator3.IndicatorCategory.OTHER)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.create_menu())

        Notify.init(APPINDICATOR_ID)
        self.curr_message = ""

    def create_menu(self):
        menu = Gtk.Menu()

        for dir in os.listdir(os.environ['HOME'] + "/.config/contextswitch"):
            if dir != "." and dir != "..":
                item = Gtk.MenuItem(dir)
                item.connect('activate', self.selection_made)
                menu.append(item)

        menu_sep = Gtk.SeparatorMenuItem()
        menu.append(menu_sep)

        item_quit = Gtk.MenuItem('Quit')
        item_quit.connect('activate', self.quit)
        menu.append(item_quit)

        menu.show_all()
        return menu

    def selection_made(self, menu_item):
        context = menu_item.get_label()
        (stdout, stderr) = self.run_command(self.contextswitch_path + " " + context)
        self.show_message(stdout.decode("utf-8"))

    def show_message(self, message):
        Notify.Notification.new("Context Switch Messsage", message, None).show()

    def quit(self, menu_item):
        Notify.uninit()
        Gtk.main_quit()

    def run_command(self, cmd):
        p = Popen(cmd.split(), stdout=PIPE)
        return p.communicate()

if __name__ == "__main__":
    err = False
    if len(sys.argv) == 1:
        err = True
    elif os.path.isfile(sys.argv[1]) and os.access(sys.argv[1], os.X_OK):
        CSIndicator(sys.argv[1])
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        Gtk.main()
    else:
        sys.stderr.write("'" + sys.argv[1] + "' isn't found or isn't executable\n")
        err = True

    if err:
        sys.stderr.write("Usage: CSIndicator.py <path to contextswitch.sh>\n")
