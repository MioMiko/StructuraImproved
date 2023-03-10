import os
os.chdir(os.path.dirname(__file__))

import armor_stand_geo_class_2 as asgc
import armor_stand_class
import structure_reader
import animation_class
import render_controller_class as rcc
import manifest
from shutil import copyfile,rmtree
from zipfile import ZipFile,ZIP_DEFLATED
from collections import Counter
import json
import re

skip_unsupported_block = True
debug = False

# load config
with open("config/config.json",encoding="utf-8") as f:
    conf = json.load(f)
with open("config/lang/lang_ref.json",encoding="utf-8") as f:
    lang_ref = json.load(f)
with open(f"config/lang/{lang_ref[conf['lang']]}.json",encoding="utf-8") as f:
    lang = json.load(f)
os.makedirs("cache", exist_ok=True)

def generate_pack(pack_name,models_object={},multi_model=False,makeMaterialsList=False, icon="lookups/pack_icon.png"):
    """
This is the funciton that makes a structura pack:
pack_name : the name of the pack, this will be stored the the manafest.JSON as well as the name of the mcpack file
models : 'NAME_TAG': {offsets: [x, y, z],opacity: percent,structure: file.mcstructure},
makeMaterialsList : sets wether a material list shall be output.
    """


    info_save_path = os.path.join(conf["info_save_path"],pack_name)

    # create info dir and export nametags file
    if "".join(tuple(models_object.keys())) != "":
        os.makedirs(info_save_path, exist_ok=True)
        fileName=f"{info_save_path}/{lang['name_tags_filename']}"
        with open(fileName,"w",encoding="utf-8") as text_file:
            text_file.write(lang["name_tags_contain"])
            for name in models_object.keys():
                text_file.write("\n{}".format(name))
    elif makeMaterialsList:
        os.makedirs(info_save_path, exist_ok=True)


    rc= rcc.render_controller()
    armorstand_entity = armor_stand_class.armorstand()
    manifest.export(pack_name)

    animation = animation_class.animations()
    all_material_list = Counter()
    for model_name,model in models_object.items():

        if debug:
            print(model['offsets'])
        rc.add_model(model_name)
        armorstand_entity.add_model(model_name)
        struct2make = structure_reader.structure_processor(model["structure"])
        armorstand = asgc.armorstandgeo(model_name,model['opacity'],model["offsets"])

        xlen,ylen,zlen = struct2make.size

        for y in range(ylen):
            #creates the layer for controlling. Note there is implied formating here
            armorstand.make_layer(y)
            animation.insert_layer(y)
            for x in range(xlen):
                for z in range(zlen):

                    block = struct2make.get_block(x, y, z)

                    if block[1][4]:
                        continue
                    try:
                        armorstand.make_block(x,y,z,block,makeMaterialsList)
                    except Exception as err:
                        print(lang["unsupported_block"])
                        print(lang["block_info"].format(x,y,z,block[0],block[1][1]))
                        if not skip_unsupported_block:
                            raise err

        # endfor(ylen)

        if makeMaterialsList:
            if multi_model:
                fileName=f"{info_save_path}/{lang['material_list_filename']}".format(model_name)
                with open(fileName,"w",encoding="utf-8") as file:
                    file.write(f"{lang['block_name']},{lang['count']}\n")
                    for name,count in armorstand.material_list.most_common():
                        all_material_list[name] += count
                        name = lang["block_name_ref"].get(name,name)
                        file.write(f"{name},{int(count)}\n")
            else:
                all_material_list = armorstand.material_list

        armorstand.export(pack_name)
        animation.export(pack_name)
        armorstand_entity.export(pack_name)

    # endfor(models)

    if makeMaterialsList:
        fileName=f"{info_save_path}/{lang['all_material_list_filename']}"
        with open(fileName,"w",encoding="utf-8") as file:
            file.write(f"{lang['block_name']},{lang['count']}\n")
            for name,count in all_material_list.most_common():
                name = lang["block_name_ref"].get(name,name)
                file.write(f"{name},{int(count)}\n")

    copyfile(icon, f"cache/{pack_name}/pack_icon.png")

    # Adds to zip file a modified armor stand geometry to enlarge the render area of the entity
    larger_render = "lookups/armor_stand.larger_render.geo.json"
    larger_render_path = f"cache/{pack_name}/models/entity/armor_stand.larger_render.geo.json"
    # the base render controller is hard coded and just copied in
    copyfile(larger_render, larger_render_path)

    rc.export(pack_name)

    # compress

    os.chdir(f"cache/{pack_name}")

    with ZipFile(os.path.join(conf["save_path"],f"{pack_name}.mcpack"),"w",ZIP_DEFLATED) as zip: 
        for dire,_,files in os.walk("./"):
            for f in files:
                f = os.path.join(dire, f)
                print(f)
                zip.write(f)

    os.chdir("../../")

    rmtree(f"cache/{pack_name}")

    models_object.clear()

    print(lang["pack_complete"])


if __name__=="__main__":
    ## this is all the gui stuff that is not needed if you are calling this as a CLI

    from tkinter import messagebox,Message,Toplevel,\
            StringVar, Button, Label, Entry, Tk, Checkbutton, END, ACTIVE,\
            filedialog, Scale,DoubleVar,HORIZONTAL,IntVar,Listbox, ANCHOR
    from config import setting_gui


    def showabout():
        about = Toplevel()
        with open("LICENSE",encoding="utf-8") as f:
            License = f.read()
        with open("LICENSE-Structura",encoding="utf-8") as f:
            License_Structura = f.read()
        about.title(lang["about"])
        msg = Message(about,text=lang["about_content"].format(License,License_Structura))
        msg.pack()

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
        if len(FileGUI.get()) == 0:
            messagebox.showerror(lang["error"], lang["need_structure"])
            return
        if model_name_var.get() in list(models.keys()):
            messagebox.showerror(lang["error"], lang["same_nametag"])
            return

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
        global models
        pack_name:str = packName.get()
        stop = False
        multi_model = False

        if len(models) == 0 or check_var.get() == 0:
            multi_model = False
            if len(FileGUI.get()) == 0:
                stop = True
                messagebox.showerror(lang["error"], lang["need_structure"])
            if len(pack_name) == 0:
                pack_name = re.sub(r"(?:.*[/\\])?(?:mystructure_)?(.+).mcstructure",r"\1",FileGUI.get())
            if check_var.get():
                add_model()
            else:
                push_model(
                    "",
                    0.8,
                    [0,0,0],
                    FileGUI.get()
                )
        else:
            multi_model = True
            if len(pack_name) == 0:
                messagebox.showerror(lang["error"], lang["need_packname"])

        if not conf["overwrite_same_packname"]:
            tmp = pack_name
            i = 1
            while os.path.isfile(os.path.join(conf["save_path"],f"pack_name.mcpack")):
               pack_name = f"{tmp}({i})"
               i += 1
        if len(icon_var.get()) > 0:
            pack_icon=icon_var.get()
        else:
            pack_icon="lookups/pack_icon.png"

        if not stop:
            if debug:
                print(models)
            try:
                generate_pack(
                    pack_name,
                    models_object = models,
                    multi_model = multi_model,
                    makeMaterialsList = (export_list.get()==1),
                    icon = pack_icon
                )
            except Exception as err:
                print(f"\a\033[1;31m{err}\033[0m")
                messagebox.showerror(lang["error"], err)
            else:
                packName.set('')
                listbox.delete(0,END)


    models = {}
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
