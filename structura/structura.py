from collections import Counter
import json
import os
import re
from zipfile import ZipFile,ZIP_DEFLATED

os.chdir(os.path.dirname(__file__))

from animation_class import Animation
from armor_stand_geo_class_2 import Geometry
from armor_stand_class import Entity
import manifest
from render_controller_class import RenderController
from structure_reader import StructureProcessor

skip_unsupported_block = True
debug = False

# load config
with open("config/config.json",encoding="utf-8") as f:
    conf = json.load(f)
with open("config/lang/lang_ref.json",encoding="utf-8") as f:
    lang_ref = json.load(f)
with open(f"config/lang/{lang_ref[conf['lang']]}.json",encoding="utf-8") as f:
    lang = json.load(f)

def draw_packname(file_name: str) -> str:
    return re.sub(r"(?:.*[/\\])?(?:mystructure_)?(.*).mcstructure",r"\1",file_name)

def generate_pack(pack_name, models, make_list:bool=False,
                  icon:str="lookups/pack_icon.png") -> None:
    """
    This is the funciton that makes a structura pack:

    Arguments:

        pack_name: the name of the pack
            This will be stored the the manafest.json as well as the name of the mcpack file

        models: a dict contains the models info
            Key(str): name tag of the model
            Value(dict): {
                offsets: (x, y, z),
                opacity: percent,
                structure: .mcstructure file name
            },

        make_list: sets wether a material list shall be output

        icon: the icon file path
    """

    print("Start Making Pack.")

    multi_model = len(models) > 1

    info_save_path = os.path.join(conf["info_save_path"],pack_name)

    # create info dir and export nametags file
    if "".join(tuple(models.keys())) != "":
        os.makedirs(info_save_path, exist_ok=True)
        file_name=f"{info_save_path}/{lang['name_tags_filename']}"
        with open(file_name,"w",encoding="utf-8") as text_file:
            text_file.write(lang["name_tags_contain"])
            for name in models.keys():
                text_file.write(f"\n{name}")
    elif make_list:
        os.makedirs(info_save_path, exist_ok=True)

    all_material_list = Counter()

    pack_path = os.path.join(conf["save_path"],f"{pack_name}.mcpack")
    with ZipFile(pack_path, "w", ZIP_DEFLATED) as zip_file:

        rc = RenderController()
        entity = Entity()
        animation = Animation()
        manifest.export(pack_name, zip_file)

        for model_name,model in models.items():

            if debug:
                print(model['offsets'])

            rc.add_model(model_name)
            entity.add_model(model_name)
            structure = StructureProcessor(model["structure"])
            geo = Geometry(model_name,model['opacity'],model["offsets"])

            xlen, ylen, zlen = structure.size

            for y in range(ylen):
                # creates the layer for controlling. Note there is implied formating here
                geo.make_layer(y)
                animation.insert_layer(y)

                # make geometry for each block
                for x in range(xlen):
                    for z in range(zlen):

                        if (blk := structure.get_block(x, y, z)) is None:
                            continue

                        try:
                            geo.make_block(x,y,z,blk,make_list)
                        except Exception as err:
                            print(lang["unsupported_block"])
                            print(lang["block_info"].format(x,y,z,blk[0],blk[2]))
                            if not skip_unsupported_block:
                                raise err

            # endfor(ylen)

            if make_list:
                if multi_model:
                    file_name = f"{info_save_path}/{lang['material_list_filename']}".format(model_name)
                    with open(file_name,"w",encoding="utf-8") as file:
                        file.write(f"{lang['block_name']},{lang['count']}\n")
                        for name,count in geo.material_list.most_common():
                            all_material_list[name] += count
                            name = lang["block_name_ref"].get(name,name)
                            file.write(f"{name},{int(count)}\n")
                else:
                    all_material_list = geo.material_list

            geo.export(zip_file)

        # endfor(models)

        animation.export(zip_file)
        entity.export(zip_file)
        rc.export(zip_file)

        if make_list:
            file_name = f"{info_save_path}/{lang['all_material_list_filename']}"
            with open(file_name,"w",encoding="utf-8") as file:
                file.write(f"{lang['block_name']},{lang['count']}\n")
                for name,count in all_material_list.most_common():
                    name = lang["block_name_ref"].get(name,name)
                    file.write(f"{name},{int(count)}\n")

        zip_file.write(icon, "pack_icon.png")

        # A modified armor stand geometry to enlarge the render area of the entity
        larger_render = "lookups/armor_stand.larger_render.geo.json"
        larger_render_path = "models/entity/armor_stand.larger_render.geo.json"
        zip_file.write(larger_render, larger_render_path)

        print(f"Pack Saved To {pack_path}")

    # end open zip

    models.clear()

    print(f"\033[1;32m{lang['pack_complete']}\033[0m")





if __name__=="__main__":
    ## this is all the gui stuff that is not needed if you are calling this as a CLI

    from _tkinter import TclError
    from tkinter import messagebox,Message,Toplevel,\
            StringVar, Button, Label, Entry, Tk, Checkbutton, END, ACTIVE,\
            filedialog, Scale,DoubleVar,HORIZONTAL,IntVar,Listbox, ANCHOR
    from config import setting_gui


    def showabout():
        about = Toplevel()
        with open("../LICENSE",encoding="utf-8") as f:
            License = f.read()
        with open("../LICENSE-Structura",encoding="utf-8") as f:
            License_Structura = f.read()
        about.title(lang["about"])
        msg = Message(about,text=lang["about_content"].format(License,License_Structura))
        msg.pack()

    def showsetting():
        setting_gui(conf,"config/config.json",lang)
        print("idhhf")

    def browseStruct():
        FileGUI.set(
            filedialog.askopenfilename(
                filetypes=(("Structure File", "*.mcstructure *.MCSTRUCTURE"),),
                initialdir=f"{conf['default_structure_path']}"
            )
        )
    def browseIcon():
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
        pack_name:str = packName.get()
        stop = False

        if len(models) == 0 or check_var.get() == 0:
            if len(FileGUI.get()) == 0:
                stop = True
                messagebox.showerror(lang["error"], lang["need_structure"])
            if len(pack_name) == 0:
                pack_name = draw_packname(FileGUI.get())
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
            if len(pack_name) == 0:
                messagebox.showerror(lang["error"], lang["need_packname"])

        if not conf["overwrite_same_packname"]:
            tmp = pack_name
            i = 1
            while os.path.isfile(os.path.join(conf["save_path"],f"{pack_name}.mcpack")):
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
                    models=models,
                    make_list=(export_list.get()==1),
                    icon=pack_icon
                )
            except Exception as err:
                print(f"\a\033[1;31m{err}\033[0m")
                messagebox.showerror(lang["error"], err)
            else:
                packName.set('')
                listbox.delete(0,END)


    try:
        root = Tk()
    except TclError:
        print("Opps, it looks like you don't have a desktop environment.\n"
              "Trying to use command line tool.")
        from main_cli import main
        main()

    models = {}
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

    info = Button(root,text="\u24D8",font=("",10,"bold"),bd=0,width=1,command=showabout)
    setting = Button(root,text="\u2699",font=("",10,"bold"),bd=0,width=1,command=showsetting)
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
    advanced_check = Checkbutton(root, text=lang["advanced"],
                                 variable=check_var, onvalue=1, offvalue=0,
                                 command=box_checked)
    export_check = Checkbutton(root, text=lang["make_lists"],
                               variable=export_list, onvalue=1, offvalue=0)

    deleteButton = Button(root, text=lang["remove_model"], command=delete_model)
    saveButton = Button(root, text=lang["make_pack"], command=runFromGui)
    modelButton = Button(root, text=lang["add_model"], command=add_model)

    # updateButton = Button(root, text="Update Blocks", command=updater.getLatest)
    transparency_lb = Label(root, text=lang["transparency"])
    transparency_entry = Scale(root, variable=sliderVar,
                               length=200, from_=0, to=100,tickinterval=10,
                               orient=HORIZONTAL)

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
