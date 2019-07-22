# Gnome Context Switcher

Gnome Context Switcher is similar to KDE's Activities feature. Changing
contexts allows you to change desktop workflows without changing users.

Unlike switching between multiple desktops, Gnome Context Switcher allows you
to change Dock applications and have custom desktop backgrounds for each
context. 

## Features

+ Save any number of contexts
+ Saves Dock/Launcher settings and Desktop backgrounds by default
+ Can run custom script during loading/unloading of a context

## Install

### PPA

```bash
sudo add-apt-repository ppa:jsseidel/gnome-context-switcher
sudo apt update
sudo apt install gnome-context-switcher
```

### Deb package

Download [the latest release](https://github.com/jsseidel/gnome-context-switcher/releases).

```bash
sudo apt install ./gnome-context-switcher_1.0.0_amd64.deb
```

## Use

### Create a new context

Set up your Desktop just the way you like for a particular context. Change the
background, set up an optimal set of applications on the Dock.

Next, click the indicator icon and select "New . . .". Choose a name for your
context and click the "OK" button. That's it!

Repeat the process to create as many contexts as you need.

### Delete a context

To delete a context, click the indicator icon and select "Delete . . .".
Confirm by clicking "Yes."

### Switch contexts

To switch a context, simply select it from the indicator menu.

### Save changes to the current context

After making changes to the current context, save it by selecting it from the
indicator menu.

### Running custom scripts

Contextswitch calls 2 scripts when it tries to load a context.

1. `~/.config/contextswitch/<CURRENT context>/contextswitch.sh unload`
2. `~/.config/contextswitch/<NEW context>/contextswitch.sh load`

You can use 1 or both scripts to perform initialization or shutdown tasks.

#### Examples

##### Saving desktop files

Save the contents of the current context's ~/Desktop directory to
~/.Desktop.somecontextname during the unloading phase and then copy
~/.Desktop.someothercontextname to ~/Desktop during the load phase.

##### Starting/Stopping a VPN

Start or stop a VPN during the load or unload phase.

##### Git identities

Here's one to set a git identity:

```
#!/bin/bash

if [[ "$1" == "load" ]] ; then
	git config --global user.name "Lastname, Firstname (foobar)"
	git config --global user.email "foobar@somecompany.com"
fi
```

