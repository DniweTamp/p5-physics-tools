# p5-physics-tools
Blender plugin and script I use to generate and edit physics in a format compatible with GFD Studio's yml import/export
There is zero error checking, so expect things to break a lot.
## Plugin installation instructions
Copy both folders in your blender addons folder and enable it in properties. 

If installed correctly, a new panel should appear in 3D Viewport's sidebar that lets you import/export and tweak different physics options
## Script usage instructions
Make sure you still have the yaml folder in your addons folder, the script needs it to be there to work.

Edit the export path in the very bottom of the script file. (I can't be bothered to add a browser window)

Select all bones you want to have physics ingame (Make sure they're in non-branching bone chains) and click the run script button. This will output 2 ymls with default settings for good enough physics, which you can import in GFD Studio.
