# ContextSwitch

Contextswitch is an effective but poor excuse for KDE's activities feature that works in both Unity (as of 16.10) and macOS (as of Sierra).

Contextswitch is a simple BASH script that saves and restores working "contexts" so that you don't have to create multiple users in order to change desktop backgrounds, chance Dock/Launcher applications, etc.

It has the added benefit of allowing you to change workflows without losing your Cisco AnyConnect VPN because you're not changing users.

## Features

+ Save any number of contexts
+ Saves Dock/Launcher settings and Desktop backgrounds by default
+ Can run custom script during loading/unloading of a context

## How to use it

First, clone the repository and put the script somewhere sane (e.g. ~/bin).

Now, set up your Desktop just the way you like for a particular context. Change the background, set up an optimal set of applications on the Dock or Launcher.

Now, do `contextswitch work`, where `work` is the name of the context you're saving.

Create as many as you need. If the context doesn't exist, `contextswitch` will create it for y ou.

To switch contexts, use `contextswitch foo` where foo is an existing context. If `foo` is already loaded, contextswitch will save the current state as `foo`.

### Running custom scripts

Contextswitch calls 2 scripts when it tries to load a context.

1. `~/.config/contextswitch/%lt;CURRENT context&gt;/contextswitch.sh unload`
2. `~/.config/contextswitch/%lt;NEW context&gt;/contextswitch.sh load`

You can use 1 or both scripts to perform initialization or shutdown tasks. For example, you could save the contents of the current context's ~/Desktop directory to ~/.Desktop.somecontextname during the unloading phase and then copy ~/.Desktop.someothercontextname to ~/Desktop during the load phase.

Or, you could, for example, start or stop a VPN during the right phase.

It's up to you.

