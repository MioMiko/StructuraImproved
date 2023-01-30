# StructuraImproved

English丨[**简体中文**](README-zh-cn.md)

Structura is inspired by Litematica. It is a tool that generates Resource packs from .mcstructure files. In this resource pack the armor stands were modified to render when off screen, and have all the blocks from your structure file as bones in their model. then "ghost blocks" are used to show the user where to place the real blocks.
This tool is based on Structura and improved to get better building expenrice in survival.Currently this tool only supports 1.16.40(not means totally unavailable in other versions).Once the mcpack file is generated,it will work in all ther versions above 1.16.40.

## Install

To start, you need to download the source code.

Then you definitely need to install python3.10-tk.</br>
Choose the method that suits you:

Arch Linux:
```bash
sudo pacman -S python
```

Then you need to install some python dependencies:
```bash
pip install -r requirements.txt
```

To start StructuraImproved:
```bash
python structura.py
```

## Setting

After StructuraImproved is launched,click the gear icon on the top right side.Then you will see a pop up window.You need to change the setting on it because the setting can run on my device may not run on everyone's devices.

## Generating an .mcstructure file

First you must get a structure block, as this is typically done from a creative copy with cheats enabled, simply execute `/give @s structure_block` to get a structure block.
![alt text](docs/give_structure.png?raw=true)
Next configure the structure using the GUI, selecte every block you wish to have in your armor stand. Note the largest size suported by a single structure block is 64x64x64 (without editing your worlds NBT data)
![alt text](docs/select_structure.PNG?raw=true)
Next click the export button at the bottom to produce a save prompt, this will allow you to save the structure to a file. Name it whatever you want and not the location, you will need it later.
![alt text](docs/export_structure.PNG?raw=true)

## Converting a structure into a .mcpack file
Start StructuraImproved.
![alt text](docs/launch_structura.PNG?raw=true)
Next open your exported structure from earlier using browse button, or type the path in manually.
![alt text](docs/browse_file.PNG?raw=true)
Enter a name for you structura pack.
![alt text](docs/name.PNG?raw=true)
If you mistakenly name two files the same it will be renamed automaticly with an index to differentiate.

If everything worked you should now have an mcpack file 
![alt text](docs/pack_made.PNG?raw=true)

## Using the pack
This pack is like any resource pack. To use it you must make sure it is active, enabling it in your global resources works well.
![alt text](docs/make_pack_active.PNG?raw=true)
The structure will appear around every armor stand in the worlds you load. It is how we are able to make it work on any world. So get out an armor stand and place it down to see your structure.
![alt text](docs/example_full.png?raw=true)
You can go through a structure layer by layer if you like by shift right clicking on the stand. This will minimize all layers except the "active" ones. I cannot add poses without adding a behavior pack so for large structures there will be mutiple layers displayed at a time (12 blocks apart)
![alt text](docs/example_layer.png?raw=true)
