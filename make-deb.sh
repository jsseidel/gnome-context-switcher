#!/bin/bash

mkdir -p ./install_files/opt/gnome-context-switcher
mkdir -p ./install_files/usr/share/applications
cp gnome-context-switcher.py gnome-context-switcher.png ./install_files/opt/gnome-context-switcher/.
cp gnome-context-switcher.desktop ./install_files/usr/share/applications/.
dpkg-buildpackage
rm -rf ./install_files
