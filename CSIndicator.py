#!/usr/bin/env python3

#############################################################################
# This is a work in progress.
#
# TODO:
#   + Make AppIndicator3 menu dynamic:
#       https://askubuntu.com/questions/751608/how-can-i-write-a-dynamically-updated-panel-app-indicator
#   + Convert contextswitch.sh Bash script to Python
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

class CSCreateContextDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Create Context", parent, 0, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.set_default_size(150, 100)
        label = Gtk.Label("Context name:")
        self.entry = Gtk.Entry()
        self.entry.set_text("New context")
        
        box = self.get_content_area()
        box.add(label)
        box.add(self.entry)
        self.show_all()

    def get_text(self):
        return self.entry.get_text()

class CSConfirmDialog(Gtk.Dialog):
    def __init__(self, parent, msg):
        Gtk.Dialog.__init__(self, "Confirm", parent, 0, (Gtk.STOCK_NO, Gtk.ResponseType.NO, Gtk.STOCK_YES, Gtk.ResponseType.YES))
        self.set_default_size(150, 100)
        label = Gtk.Label(msg)
        
        box = self.get_content_area()
        box.add(label)
        self.show_all()

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
        
        item_new = Gtk.MenuItem('New...')
        item_new.connect('activate', self.new_context)
        menu.append(item_new)
        
        item_del = Gtk.MenuItem('Delete...')
        item_del.connect('activate', self.del_context)
        menu.append(item_del)
        
        menu_sep = Gtk.SeparatorMenuItem()
        menu.append(menu_sep)
        
        item_quit = Gtk.MenuItem('Quit')
        item_quit.connect('activate', self.quit)
        menu.append(item_quit)

        menu.show_all()
        return menu

    def del_context(self, menu_item):
        (stdout, stderr) = self.run_command("cat " + os.environ['HOME'] + "/.contextswitch")
        curr_context = stdout.decode("utf-8").rstrip()
        del_dialog = CSConfirmDialog(None, "Are you sure you want to delete '" + curr_context + "'?")
        response = del_dialog.run()
        if response == Gtk.ResponseType.YES:
            self.run_command("rm -rf " + os.environ['HOME'] + "/.config/contextswitch/" + curr_context)
            self.run_command("rm -f " + os.environ['HOME'] + "/.contextswitch")
            self.show_message(curr_context + " deleted. \n\nNo context is currently loaded.")

        del_dialog.destroy()

    def new_context(self, menu_item):
        new_dialog = CSCreateContextDialog(None)
        response = new_dialog.run()
        if response == Gtk.ResponseType.OK:
            (stdout, stderr) = self.run_command(self.contextswitch_path + " " + new_dialog.get_text())
            self.show_message(stdout.decode("utf-8"))
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancelled.")
        new_dialog.destroy()

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
