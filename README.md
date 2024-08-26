# Disclaimer
LBridge is still in beta, things may change in the future

For a quick rundown of the tool, check out this video: https://youtu.be/sEQZVipCowo?si=yCpYx7cGJvkMYmGe

# LBridge
LBridge is a Custom Megascans Plugin for Houdini Solaris. With this plugin you can export 3d Assets from Quixel Bridge straight into Houdini Solaris with one click. 

# Installation
To Install LBridge you need to do three things:

1. Download and Place the LBridge folder anywhere on your machine.
2. Place the LBridge.json file into "HOUDINI_PATH/packages". The default location on Windows is "C:\Program Files\Side Effects Software\YOUR_HOUDINI_VERSION\packages". If the "packages" file does not exist, create it.
3. Edit the JSON File with the text editor of your choice, and replace the "value" string with the path to the LBridge Folder.

That's it. Now if you restart Houdini, it should load the plugin.

# Quixel Bridge Setup
Before you can export to Houdini, in Bridge you have to go to Export Settings and set Export Target to "Custom Socket Export" with Socket Port "24981"
