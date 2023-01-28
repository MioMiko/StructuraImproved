import armor_stand_geo_class_2 as asgc
import armor_stand_class
import structure_reader
import animation_class
from config import setting_gui
import render_controller_class as rcc
import manifest
from shutil import copyfile
import os
from zipfile import ZipFile,ZIP_DEFLATED
import glob
import shutil
import ntpath
import json
import re

skip_unsupported_block = False
debug = False

with open("lookups/nbt_defs.json") as f:
    nbt_def = json.load(f)
with open("config/config.json") as f:
    conf = json.load(f)
with open(f"config/lang/lang_ref.json") as f:
    lang_ref = json.load(f)
with open(f"config/lang/{lang_ref[conf['lang']]}.json") as f:
    lang = json.load(f)

def process_block(block_states,block_entity):
    rot = None
    top = False
    lit = False
    data = "0"
    skip = False
    variant = "default"

    # variant and lit determine the texture of blocks together
    for key in nbt_def["block_entity_variant"]:
        if key in block_entity.keys():
            variant = str(block_entity[key])
            break
    else:
        for key in nbt_def["variant"]:
            if key in block_states.keys():
                variant = str(block_states[key])
                break

    for key in nbt_def["lit"]:
        if key in block_states.keys():
            lit = bool(block_states[key])
            break

    for key in nbt_def["block_entity_rot"]:
        if key in block_entity.keys():
            rot = str(block_entity[key])
            break
    else:
        for key in nbt_def["rot"]:
            if key in block_states.keys():
                try:
                    rot = int(block_states[key])
                except:
                    rot = str(block_states[key])
                break

    # top and data determines the offset of block together
    for key in nbt_def["top"]:
        if key in block_states.keys():
            top = bool(block_states[key])
            break

    for key in nbt_def["block_entity_data"]:
        if key in block_entity.keys():
            data = str(block_entity[key])
            break
    else:
        for key in nbt_def["data"]:
            if key in block_states.keys():
                try:
                    data = str(int(block_states[key]))
                except:
                    data = str(block_states[key])
                break

    for key in nbt_def["skip"]:
        if key in block_states.keys():
            skip = bool(block_states[key])
            break

    # exception
    if "id" in block_entity:
        if block_entity["id"] == "Skull":
            if block_entity["SkullType"] == 5:
                data = "dragon"
            if rot == 1:
                rot = str(block_entity["Rotation"])
                data += "_standing"
        elif block_entity["id"] == "Hopper":
            variant = str(rot)

    if debug:
        print([rot, top, variant, lit, data, skip])
    return [rot, top, variant, lit, data, skip]





def generate_pack(pack_name,models_object={},makeMaterialsList=False, icon="lookups/pack_icon.png"):
    """
This is the funciton that makes a structura pack:
pack_name : the name of the pack, this will be stored the the manafest.JSON as well as the name of the mcpack file
models : 'NAME_TAG': {offsets: [x, y, z],opacity: percent,structure: file.mcstructure},
makeMaterialsList : sets wether a material list shall be output.
    """


    visual_name = pack_name
    if len("".join(list(models_object.keys()))) > 1:
        fileName="{} Nametags.txt".format(pack_name)
        with open(fileName,"w") as text_file:
            text_file.write("These are the nametags used in this file\n")
            for name in models_object.keys():
                text_file.write("{}\n".format(name))


    ## makes a render controller class that we will use to hide models
    rc=rcc.render_controller()
    ##makes a armor stand entity class that we will use to add models 
    armorstand_entity = armor_stand_class.armorstand()
    ##manifest is mostly hard coded in this function.
    manifest.export(visual_name)

    ## repeate for each structure after you get it to work
    #creats a base animation controller for us to put pose changes into
    animation = animation_class.animations()
    longestY=0
    update_animation=True
    for model_name in models_object.keys():
        offset=models_object[model_name]["offsets"]
        rc.add_model(model_name)
        armorstand_entity.add_model(model_name)
        copyfile(models_object[model_name]["structure"], "{}/{}.mcstructure".format(pack_name,model_name))
        if debug:
            print(models_object[model_name]['offsets'])
        #reads structure
        struct2make = structure_reader.process_structure(models_object[model_name]["structure"])
        #creates a base armorstand class for us to insert blocks
        armorstand = asgc.armorstandgeo(model_name,alpha = models_object[model_name]['opacity'],offsets=models_object[model_name]['offsets'])

        #gets the shape for looping
        [xlen, ylen, zlen] = struct2make.get_size()
        if ylen > longestY:
            update_animation=True
            longestY = ylen
        else:
            update_animation=False
        for y in range(ylen):
            #creates the layer for controlling. Note there is implied formating here
            #for layer names
            armorstand.make_layer(y)
            #adds links the layer name to an animation
            if update_animation:
                animation.insert_layer(y)
            for x in range(xlen):
                for z in range(zlen):
                    #gets block
                    block,block_entity = struct2make.get_block(x, y, z)
                    blk_name = block["name"].replace("minecraft:", "")
                    blockProp = process_block(block["states"],block_entity)
                    rot = blockProp[0]
                    top = blockProp[1]
                    variant = blockProp[2]
                    lit = blockProp[3]
                    data = blockProp[4]
                    skip = blockProp[5]

                    if debug:
                        print(blk_name)
                    ##  If java worlds are brought into bedrock the tools some times
                    ##   output unsupported blocks, will log.

                    if not skip:
                        if skip_unsupported_block:
                            try:
                                armorstand.make_block(x, y, z, blk_name, rot = rot, top = top,variant = variant, lit=lit, data=data)
                            except:
                                print(lang["unsupported_block"])
                                print(lang["block_info"].format(x,y,z,blk_name,variant))
                        else:
                            armorstand.make_block(x, y, z, blk_name, rot = rot, top = top,variant = variant, lit=lit, data=data)
        ## this is a quick hack to get block lists, doesnt consider vairants.... so be careful
        if makeMaterialsList:
            allBlocks = struct2make.get_block_list()
            fileName="{}-{} block list.txt".format(visual_name,model_name)
            with open(fileName,"w") as text_file:
                text_file.write("This is a list of blocks, there is a known issue with variants, all variants are counted together\n")
                for name in allBlocks.keys():
                    commonName = name.replace("minecraft:","")
                    text_file.write("{}: {}\n".format(commonName,allBlocks[name]))
        
        # call export fuctions
        armorstand.export(pack_name)
        animation.export(pack_name)

        ##export the armorstand class
        armorstand_entity.export(pack_name)

    # Copy my icons in
    copyfile(icon, "{}/pack_icon.png".format(pack_name))
    # Adds to zip file a modified armor stand geometry to enlarge the render area of the entity
    larger_render = "lookups/armor_stand.larger_render.geo.json"
    larger_render_path = "{}/models/entity/{}".format(pack_name, "armor_stand.larger_render.geo.json")
    copyfile(larger_render, larger_render_path)
    # the base render controller is hard coded and just copied in


    rc.export(pack_name)
    ## get all files
    file_paths = []
    for directory,_,_ in os.walk(pack_name):
        file_paths.extend(glob.glob(os.path.join(directory, "*.*")))

    ## add all files to the mcpack file  
    with ZipFile(f"{conf['save_path']}{pack_name}.mcpack", 'w',ZIP_DEFLATED) as zip: 
        # writing each file one by one 
        for file in file_paths:
            print(file)
            zip.write(file)
    ## delete all the extra files.
    shutil.rmtree(pack_name)
    print("Pack Making Completed")


if __name__=="__main__":
    ## this is all the gui stuff that is not needed if you are calling this as a CLI

    from tkinter import messagebox,Message,Toplevel
    from tkinter import StringVar, Button, Label, Entry, Tk, Checkbutton, END, ACTIVE
    from tkinter import filedialog, Scale,DoubleVar,HORIZONTAL,IntVar,Listbox, ANCHOR


    def showabout():
        about = Toplevel()
        with open("LICENSE") as f:
            License = f.read()
        with open("LICENSE-Structura") as f:
            License_Structura = f.read()
        about.title(lang["about"])
        msg = Message(about,text=lang["about_content"].format(License,License_Structura))
        msg.pack()
        about.mainloop()

    def showsetting():
        setting_gui(conf,"config/config.json",lang)
        print("idhhf")

    def browseStruct():
        #browse for a structure file.
        FileGUI.set(
            filedialog.askopenfilename(
                filetypes=(("Structure File", "*.mcstructure *.MCSTRUCTURE"),),
                initialdir=f"{conf['default_structure_path']}"
            )
        )
    def browseIcon():
        #browse for a structure file.
        icon_var.set(filedialog.askopenfilename(filetypes=(
            ("Icon File", "*.png *.PNG"), )))

    def box_checked():
        if check_var.get() == 0:
            modle_name_entry.grid_forget()
            modle_name_lb.grid_forget()
            deleteButton.grid_forget()
            listbox.grid_forget()
            saveButton.grid_forget()
            modelButton.grid_forget()
            cord_lb.grid_forget()
            x_entry.grid_forget()
            y_entry.grid_forget()
            z_entry.grid_forget()
            transparency_lb.grid_forget()
            transparency_entry.grid_forget()
            r = 4
            advanced_check.grid(row=r, column=0)
            export_check.grid(row=r, column=1)
            saveButton.grid(row=r, column=2)
            r += 1
            # updateButton.grid(row=r, column=2)
        else:
            saveButton.grid_forget()
            r = 4
            modle_name_entry.grid(row=r, column=1)
            modle_name_lb.grid(row=r, column=0)
            modelButton.grid(row=r, column=2)
            r += 1
            cord_lb.grid(row=r, column=0,columnspan=3)
            r += 1
            x_entry.grid(row=r, column=0)
            y_entry.grid(row=r, column=1)
            z_entry.grid(row=r, column=2)
            r += 1
            transparency_lb.grid(row=r, column=0)
            transparency_entry.grid(row=r, column=1,columnspan=2)
            r += 1
            listbox.grid(row=r,column=1, rowspan=3)
            deleteButton.grid(row=r,column=2)
            r += 4
            advanced_check.grid(row=r, column=0)
            export_check.grid(row=r, column=1)
            saveButton.grid(row=r, column=2)
            r += 1
            # updateButton.grid(row=r, column=2)

    def add_model():
        valid=True
        if len(FileGUI.get()) == 0:
            messagebox.showerror(lang["error"], lang["need_structure"])
            valid=False
        if model_name_var.get() in list(models.keys()):
            messagebox.showerror(lang["error"], lang["same_nametag"])
            valid=False

        if valid:
            name_tag = model_name_var.get()
            push_model(
                name_tag,
                (100-sliderVar.get())/100,
                [xvar.get(),yvar.get(),zvar.get()],
                FileGUI.get()
            )
            listbox.insert(END,name_tag)

    def push_model(name,opacity,offset,structure):
        global models
        models[name] = {
            "offsets": offset,
            "opacity": opacity,
            "structure": structure
        }


    def delete_model():
        items = listbox.curselection()
        if len(items)>0:
            models.pop(listbox.get(ACTIVE))
        listbox.delete(ANCHOR)


    def runFromGui():
        ##wrapper for a gui.
        global models, offsets
        pack_name:str = packName.get()
        stop = False

        if check_var.get() == 0:
            if len(FileGUI.get()) == 0:
                stop = True
                messagebox.showerror(lang["error"], lang["need_structure"])
            if len(pack_name) == 0:
                pack_name = re.sub(r"(?:.*[/\\])?(?:mystructure_)?(.+).mcstructure",r"\1",FileGUI.get())
        else:
            if len(list(models.keys())) == 0:
                stop = True
                messagebox.showerror(lang["error"], lang["need_models"])

            if len(pack_name) == 0:
                messagebox.showerror(lang["error"], lang["need_packname"])
        if not conf["overwrite_same_packname"]:
            tmp = pack_name
            i = 1
            while os.path.isfile(f"{conf['save_path']}{pack_name}.mcpack"):
               pack_name = f"{tmp}({i})"
               i += 1
        if len(icon_var.get()) > 0:
            pack_icon=icon_var.get()
        else:
            pack_icon="lookups/pack_icon.png"
        if not stop:
            if not(check_var.get()):
                push_model(
                    "",
                    0.8,
                    [0,0,0],
                    FileGUI.get()
                )
            if debug:
                print(models)
            generate_pack(
                pack_name,
                models_object = models,
                makeMaterialsList = (export_list.get()==1),
                icon = pack_icon
            )
        packName.set('')



    offsets={}
    models={}
    root = Tk()
    root.resizable(False,False)
    root.title("StructuraImproved")
    FileGUI = StringVar()
    packName = StringVar()
    icon_var = StringVar()
    icon_var.set("lookups/pack_icon.png")
    sliderVar = DoubleVar()
    sliderVar.set(20)
    model_name_var = StringVar()

    xvar = DoubleVar()
    xvar.set(0)
    yvar = DoubleVar()
    zvar = DoubleVar()
    zvar.set(0)

    check_var = IntVar()
    export_list = IntVar()

    info = Button(root,text=u"\u24D8",font=("",10,"bold"),bd=0,width=1,command=showabout)
    setting = Button(root,text=u"\u2699",font=("",10,"bold"),bd=0,width=1,command=showsetting)
    listbox=Listbox(root)
    file_entry = Entry(root, textvariable=FileGUI)
    packName_entry = Entry(root, textvariable=packName)
    modle_name_lb = Label(root, text=lang["name_tag"])
    modle_name_entry = Entry(root, textvariable=model_name_var)
    cord_lb = Label(root, text=lang["offset"])
    x_entry = Entry(root, textvariable=xvar, width=5)
    y_entry = Entry(root, textvariable=yvar, width=5)
    z_entry = Entry(root, textvariable=zvar, width=5)

    icon_lb = Label(root, text=lang["icon_file"])
    icon_entry = Entry(root, textvariable=icon_var)
    IconButton = Button(root, text=lang["browse"], command=browseIcon)

    file_lb = Label(root, text=lang["structure_file"])
    packName_lb = Label(root, text=lang["packname"])
    packButton = Button(root, text=lang["browse"], command=browseStruct)
    advanced_check = Checkbutton(root, text=lang["advanced"], variable=check_var, onvalue=1, offvalue=0, command=box_checked)
    export_check = Checkbutton(root, text=lang["make_lists"], variable=export_list, onvalue=1, offvalue=0)

    deleteButton = Button(root, text=lang["remove_model"], command=delete_model)
    saveButton = Button(root, text=lang["make_pack"], command=runFromGui)
    modelButton = Button(root, text=lang["add_model"], command=add_model)

    # updateButton = Button(root, text="Update Blocks", command=updater.getLatest)
    transparency_lb = Label(root, text=lang["transparency"])
    transparency_entry = Scale(root,variable=sliderVar, length=200, from_=0, to=100,tickinterval=10,orient=HORIZONTAL)

    r = 0
    info.grid(row=r, column=2,sticky="ne")
    setting.grid(row=r, column=3,sticky="nw")
    r += 1
    file_lb.grid(row=r, column=0)
    file_entry.grid(row=r, column=1)
    packButton.grid(row=r, column=2)
    r += 1
    icon_lb.grid(row=r, column=0)
    icon_entry.grid(row=r, column=1)
    IconButton.grid(row=r, column=2)
    r += 1
    packName_lb.grid(row=r, column=0)
    packName_entry.grid(row=r, column=1)

    box_checked()

    root.mainloop()
    root.quit()
