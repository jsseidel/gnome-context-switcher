VERS = $(shell cat VERSION)

all:
	$(info nothing to build)

install:
	mkdir -p install_files/opt/gnome-context-switcher
	mkdir -p install_files/usr/share/applications
	cp gnome-context-switcher.png gnome-context-switcher.py install_files/opt/gnome-context-switcher/.
	cp gnome-context-switcher.desktop install_files/usr/share/applications/.

version:
	$(info $(VERS))

##########################################################################################3
# Debian source package
#

debian_source:
	debuild -S

# gnome-context-switcher_1.0.0_source.changes
dput:
	dput -f ppa:jsseidel/gnome-context-switcher ../gnome-context-switcher_$(VERS)_source.changes
