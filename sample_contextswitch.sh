#!/bin/bash

#
# This script should live in:
#    ~/.config/contextswitch/<context_name>/contextswitch.sh
#
# The idea behind this script is that different contexts have
# different workspaces, which are really just directories
# containing:
#   Desktop
#   Documents
#   Pictures
#   git
#
# and so on. When you switch contexts, you first unload the old
# context by removing the softlinks into the workspace directory.
#
# You then load a new context by creating soft links into the
# new workspace.
#
# This is just one way to handle changing directories using
# the Gnome context switcher.
#

CONTEXT=PersonalWorkspace

if [[ "$1" == "load" ]] ; then
    ln -s ~/$CONTEXT/git ~/git
    ln -s ~/$CONTENT/Documents ~/Documents
    ln -s ~/$CONTEXT/Pictures ~/Pictures
    # This is needed because nautilus will create a Desktop
    # directory if there isn't one, and if we don't remove
    # the empty directory, we end up with a link inside the
    # Desktop directory.
    if [[ -d ~/Desktop ]] ; then rmdir ~/Desktop ; fi
    ln -s ~/$CONTEXT/Desktop ~/Desktop
elif [[ "$1" == "unload" ]] ; then
    rm -f ~/git
    rm -f ~/Documents
    rm -f ~/Pictures
    rm -f ~/Desktop
fi

