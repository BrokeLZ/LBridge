# Disclaimer
LBridge is still in beta, things may change in the future.

Currently only Houdini Indie or NC are supported.

Documentation: https://docs.google.com/document/d/1Sb-wLT90WwU-ZzOnbctnEz3rQ6fUw2dDNmt3yN-Lhlc/edit?usp=sharing

# LBridge
LBridge is a custom Quixel Bridge Plugin for Houdini Solaris. It enables one-click export from Quixel Bridge to Houdini Solaris (USD) and offers extensive customization options, including texture format and color space conversion.

Features:
- One-click export to Houdini Solaris.
- Supports 3D Assets and 3D Plants from Quixel Bridge.
- Asset variants are detected and split out as USD variants.
- Exposes settings on HDA for fine-tuning imported assets.
- Can convert textures to formats like rat or exr and outputs color spaces like ACEScg or sRGB.

# Installation
Houdini Configuration:

1. Download and extract the provided ZIP file.
2. Place the LBridge Folder anywhere on your machine.
3. Place the LBridge.json file into "HOUDINI_PATH/packages". 
   The default location on Windows is:
   "C:\Program Files\Side Effects Software\YOUR_HOUDINI_VERSION\packages". 
   If the "packages" folder does not exist, create it.
4. Edit the JSON File with the text editor of your choice, and replace the "value" string with the path to the LBridge Folder from Step 2.

Quixel Bridge Configuration:

1. Open Quixel Bridge.
2. Go to Export Settings and set:
   - Export Target: Custom Socket Export.
   - Socket Port: 24981.


That's it. If you now restart Houdini, it should load the plugin and Bridge will target the right slot.


For questions or feedback, contact me on Discord: lorenz36.
