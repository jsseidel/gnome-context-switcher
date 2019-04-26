# Gnome Context Switcher

Gnome Context Switcher is an effective but poor excuse for KDE's Activities
feature for Gnome. Changing contexts allows you to change desktop workflows
without changing users, which can be problematic, resulting in multple setups
for some applications and possible VPN issues.

Unlike switching between multiple desktops, Gnome Context Switcher allows you
to change Dock applications and have custom desktop backgrounds for each
context. 

## Features

+ Save any number of contexts
+ Saves Dock/Launcher settings and Desktop backgrounds by default
+ Can run custom script during loading/unloading of a context

## Install

Download [the latest release](https://github.com/jsseidel/gnome-context-switcher/releases).

```bash
sudo apt install ./gnome-context-switcher_1.0.0_amd64.deb
```

## Use

Set up your Desktop just the way you like for a particular context. Change the
background, set up an optimal set of applications on the Dock.

Next, click the indicator icon and select "New . . .". Choose a name for your
context and click the "OK" button. That's it!

Repeat the process to create as many contexts as you need.

To delete a context, click the indicator icon and select "Delete . . .".
Confirm by clicking "Yes."

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

