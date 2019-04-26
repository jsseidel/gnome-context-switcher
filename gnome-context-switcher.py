#!/usr/bin/env python3

##############################################################################
# This is currently beta. Use at your own risk!
##############################################################################

import json
import os
import signal
import sys
import time

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk
from gi.repository import AppIndicator3
from gi.repository import Notify

from subprocess import Popen, PIPE

APPINDICATOR_ID = 'gnome-context-switcher-indicator'

class CSCreateContextDialog(Gtk.Dialog):
    """A dialog for creating a new context"""
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Create Context", parent, 0,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                    Gtk.STOCK_OK, Gtk.ResponseType.OK))
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
    """A simple YES or NO confirmation dialog"""
    def __init__(self, parent, msg):
        Gtk.Dialog.__init__(self, "Confirm", parent, 0,
                (Gtk.STOCK_NO, Gtk.ResponseType.NO,
                    Gtk.STOCK_YES, Gtk.ResponseType.YES))
        self.set_default_size(150, 100)
        label = Gtk.Label(msg)

        box = self.get_content_area()
        box.add(label)
        self.show_all()

class CSIndicator():
    def __init__(self):
        self.app = "Context Switcher"
        self.curr_message = ""
        self.curr_context = self.get_curr_context()
        self.config_dir = os.path.expanduser("~/.config/contextswitch")

        icon_path = "%s/gnome-context-switcher.png" % os.path.dirname(
                os.path.realpath(__file__))
        self.indicator = AppIndicator3.Indicator.new(APPINDICATOR_ID,
                os.path.abspath(icon_path),
                AppIndicator3.IndicatorCategory.OTHER)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.create_menu())

        Notify.init(APPINDICATOR_ID)

    def get_curr_context(self):
        """Returns the contents of the .contextswitch file, which
        holds the current context, even between instances.
        """
        context_file = os.path.expanduser("~/.contextswitch")
        if os.access(context_file, os.R_OK):
            return self.get_file_contents(context_file)

        return ""

    def record_curr_context(self):
        """Records the value of the currently loaded context
        in .contextswitch.
        """
        context_file = os.path.expanduser("~/.contextswitch")

        self.string_to_file(self.curr_context, context_file)

    def create_menu(self):
        """Builds a GTK menu by listing the contents of the
        contextswitch config directory. Every created context
        has a directory there.
        """
        menu = Gtk.Menu()

        # Create the config directory if it's not there
        if os.path.isdir(self.config_dir) == False:
            os.mkdir(self.config_dir)

        for dir in sorted(os.listdir(self.config_dir)):
            if dir != "." and dir != "..":
                item = Gtk.MenuItem(dir)
                item.connect('activate', self.choose_context)
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
        del_dialog = CSConfirmDialog(None, "Are you sure you want to delete"
                                           " '%s'?" % self.curr_context)
        response = del_dialog.run()
        if response == Gtk.ResponseType.YES:
            self.run_command("rm -rf %s/%s" %
                    (self.config_dir, self.curr_context))
            self.run_command("rm -f %s" %
                    os.path.expanduser("~/.contextswitch"))
            self.show_message("'%s' deleted. \n\n"
                              "No context is currently loaded." %
                              self.curr_context)
            self.indicator.set_menu(self.create_menu())
            self.curr_context = ""

        del_dialog.destroy()

    def new_context(self, menu_item):
        new_dialog = CSCreateContextDialog(None)
        response = new_dialog.run()
        if response == Gtk.ResponseType.OK:
            new_context = new_dialog.get_text()

            # A user might have a contextswitch.sh file in the old
            # context's config directory, which we'll need to run.
            fpath = "%s/%s/contextswitch.sh" % (
                    self.config_dir,self.curr_context)
            if self.is_exe(fpath):
                (stdout, stderr) = self.run_command("%s unload" % fpath)
                if stdout != "" or stderr != "":
                    self.show_message("%s\n\n%s" % (stdout, stderr))

            # Now we can save the new context
            self.save_context(new_dialog.get_text())
            self.indicator.set_menu(self.create_menu())
            self.curr_context = new_dialog.get_text()
            self.record_curr_context()
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancelled.")
        new_dialog.destroy()

    def choose_context(self, menu_item):
        context = menu_item.get_label()

        # If the current context is not the same as what the user
        # selected, the user is trying to change contexts. Otherwise,
        # the user is trying to save the current context.
        if context != self.curr_context:
            # A user can have a contextswitch.sh script in their
            # config directories that we need to run if executable

            # First we 'unload' the old context
            fpath = "%s/%s/contextswitch.sh" % (
                    self.config_dir,self.curr_context)
            if self.is_exe(fpath):
                (stdout, stderr) = self.run_command("%s unload" % fpath)
                if stdout != "" or stderr != "":
                    self.show_message("%s\n\n%s" % (stdout, stderr))

            # Next we 'load' the new context
            fpath = "%s/%s/contextswitch.sh" % (
                    self.config_dir, context)
            if self.is_exe(fpath):
                (stdout, stderr) = self.run_command("%s load" % fpath)
                if stdout != "" or stderr != "":
                    self.show_message("%s\n\n%s" % (stdout, stderr))

            # Now it's safe to switch contexts
            self.switch_context(context)
        else:
            self.save_context(context)

    def switch_context(self, context):
        err_msg = ""

        # Change desktop background
        background = self.get_file_contents("%s/%s/desktopbackground" %
                (self.config_dir, context))
        (stdout, stderr) = self.run_command(
                "gsettings set org.gnome.desktop.background picture-uri %s" %
                background)
        if stderr != "":
            err_msg = stderr

        # Change launcher
        launcher = self.get_file_contents("%s/%s/launcher" %
                (self.config_dir, context))
        (stdout, stderr) = self.run_command_array(
                ["gsettings", "set", "org.gnome.shell", "favorite-apps",
                    launcher])
        if stderr != "":
            err_msg = "%s\n\n%s" % (err_msg, stderr)

        self.curr_context = context
        self.record_curr_context()

        if err_msg != "":
            self.show_message("There was a problem:\n\n%s" % err_msg)
        else:
            self.show_message("Switched to context '%s'." % context)

    def save_context(self, context):
        err_msg = ""

        # Make a directory for the context in case one does not yet exist
        (stdout, stderr) = self.run_command("mkdir -p %s/%s" %
                (self.config_dir, context))
        if stderr != "":
            err_msg = stderr

        # Save the launcher status
        (stdout, stderr) = self.run_command(
                "gsettings get org.gnome.shell favorite-apps")
        if stderr != "":
            err_msg = "%s\n\n%s" % (err_msg, stderr)
        else:
            conf_path = "%s/%s/launcher" % (self.config_dir, context)
            self.string_to_file(stdout, conf_path)

        # Save the background picture
        (stdout, stderr) = self.run_command(
                "gsettings get org.gnome.desktop.background picture-uri")
        if stderr != "":
            err_msg = "%s\n\n%s" % (err_msg, stderr)
        else:
            conf_path = "%s/%s/desktopbackground" % (self.config_dir, context)
            self.string_to_file(stdout, conf_path)

        # Show a status message
        if err_msg != "":
            self.show_message(
                    "Problems were encountered while trying to save context"
                    "'%s':\n\n%s" % (context, err_msg))
        else:
            self.show_message("Saved context '%s'" % context)

    def show_message(self, message):
        Notify.Notification.new("Context Switch Messsage",
                message, None).show()

    def quit(self, menu_item):
        Notify.uninit()
        Gtk.main_quit()

    def get_file_contents(self, path):
        """Tries to extract and return the text contents of a given file.
        Returns an empty string if something goes wrong.
        """
        try:
            with open(path, 'r') as f:
                content = f.read()
                f.close()
                return content.rstrip()
        except IOError as x:
            self.show_message(x.strerror)
            return ""

    def string_to_file(self, s, path):
        """Writes the string s to the file at path."""
        try:
            with open(path, 'w') as f:
                f.write(s)
                f.close()
        except IOError as x:
            self.show_message(x.strerror)

    def is_exe(self, fpath):
        """Returns True if the given fpath is an executable file."""
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    def run_command_array(self, cmd_array):
        """Runs a command given in cmd_array and returns UTF-8 string results
        in stdout and stderr. Some commands contain arguments that are quoted
        and contain spaces, which won't work with a split function as below.
        """
        p = Popen(cmd_array, stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = p.communicate()
        return (stdout.decode("utf-8"), stderr.decode("utf-8"))

    def run_command(self, cmd):
        """Runs a string command and returns UTF-8 string results in stdout and
        stderr.
        """
        p = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = p.communicate()
        return (stdout.decode("utf-8"), stderr.decode("utf-8"))

if __name__ == "__main__":
    CSIndicator()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Gtk.main()
