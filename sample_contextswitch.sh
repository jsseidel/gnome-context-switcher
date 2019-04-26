#!/bin/bash

#
# This script should live in:
#    ~/.config/contextswitch/<context_name>/contextswitch.sh
#
# The idea behind this script is that different contexts have different
# workspaces, which are really just directories containing:
#
#   Desktop
#   Documents
#   Pictures
#   git
#
# and so on. When you switch contexts, you first unload the old context by
# removing the softlinks into the workspace directory.
#
# You then load a new context by creating soft links into the
# new workspace.
#
# For this to work properly, you need to set up the softlinks exactly the way
# they are expected to be here BEFORE you switch contexts, otherwise you get
# things like links to the Desktop on your actual desktop.
#
# This is just one way to handle changing directories using the Gnome context
# switcher.
#

CONTEXT=PersonalWorkspace

if [[ "$1" == "load" ]] ; then
	ln -s ~/$CONTEXT/git ~/git
	ln -s ~/Dropbox/Documents ~/Documents
	ln -s ~/$CONTEXT/Pictures ~/Pictures
	ln -s ~/$CONTEXT/Desktop ~/Desktop
	ln -s ~/$CONTEXT/Music ~/Music
	ln -s ~/$CONTEXT/Videos ~/Videos
elif [[ "$1" == "unload" ]] ; then
	rm -f ~/git
	rm -f ~/Documents
	rm -f ~/Pictures
	rm -f ~/Desktop
	rm -f ~/Music
	rm -f ~/Videos
fi

# We kill nautilus-desktop here because we switched backgrounds
# and Desktop directories
killall nautilus-desktop
sleep 2
nohup nautilus-desktop --new-window </dev/null 1>/dev/null 2>&1 &


