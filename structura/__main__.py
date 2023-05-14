"""
Main file of StructuraImproved GUI
Start a cli if tkinter or desktop environment is missing
"""

import logging
from pathlib import Path
import sys

from api import Structura
from config import config
import logger

logger.init_logger()
logger = logging.getLogger("StructuraImproved")

# check if a cli should be started
def start_cli():
    from cli import main
    main()
    sys.exit()

if "cli" in sys.argv[1:]:
    start_cli()

try:
    from _tkinter import TclError
    from tkinter import (messagebox, Message, Toplevel, Frame,
        StringVar, Button, Label, Entry, Tk, Checkbutton, END, ACTIVE,
        filedialog, Scale, DoubleVar, HORIZONTAL, IntVar, Listbox, ANCHOR)
except ImportError:
    logger.warning("Opps, it looks like you didn't install Tkinter.\n"
                   "Trying to use command line tool.")
    start_cli()

try:
    root = Tk()
except TclError:
    logger.warning("Opps, it looks like you don't have a desktop environment.\n"
                   "Trying to use command line tool.")
    start_cli()

from setting_gui import SettingGui

ROOT = Path(__file__).parent

conf, lang = config.conf, config.lang
structura = Structura(lang_name=config.std_lang_name,
                      save_path=ROOT / conf["save_path"],
                      info_save_path=ROOT / conf["info_save_path"],
                      overwrite_same_packname=conf["overwrite_same_packname"],
                      skip_unsupported_block=conf["skip_unsupported_block"])

def showabout():
    about = Toplevel()
    with open(ROOT / "../LICENSE",encoding="utf-8") as f:
        License = f.read()
    with open(ROOT / "../LICENSE-Structura",encoding="utf-8") as f:
        License_Structura = f.read()
    about.title(lang["about"])
    msg = Message(about,text=lang["about_content"].format(License,License_Structura))
    msg.pack()

def showsetting():
    SettingGui()

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
        advance_frame.grid_forget()
    else:
        advance_frame.grid(row=4, column=0, columnspan=3)

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
    if len(items) > 0:
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
            pack_name = Structura.draw_packname(FileGUI.get())
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

    if len(icon_var.get()) > 0:
        pack_icon=icon_var.get()
    else:
        pack_icon = "api/res/pack_icon.png"

    if not stop:
        logger.debug(models)
        try:
            structura.make_pack(
                pack_name,
                models=models,
                make_list=(export_list.get()==1),
                big_model=False,
                icon=ROOT / pack_icon
            )
        except Exception as err:
            logger.exception(err)
            messagebox.showerror(lang["error"], err)
        else:
            packName.set('')
            listbox.delete(0,END)


models = {}
root.resizable(False,False)
root.title("StructuraImproved")
FileGUI = StringVar()
packName = StringVar()
icon_var = StringVar()
icon_var.set("api/res/pack_icon.png")
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

about_frame = Frame(root)
Button(about_frame, text="\u24D8", font=("",10,"bold"), bd=0,
              width=1, command=showabout).grid(row=0, column=0)
Button(about_frame, text="\u2699", font=("",10,"bold"), bd=0,
                 width=1, command=showsetting).grid(row=0,column=1)

file_entry = Entry(root, textvariable=FileGUI)
packName_entry = Entry(root, textvariable=packName)

advance_frame = Frame(root)
modle_name_lb = Label(advance_frame, text=lang["name_tag"])
modle_name_entry = Entry(advance_frame, textvariable=model_name_var)
listbox = Listbox(advance_frame)
delete_bt = Button(advance_frame, text=lang["remove_model"], command=delete_model)
save_bt = Button(root, text=lang["make_pack"], command=runFromGui)
add_bt = Button(advance_frame, text=lang["add_model"], command=add_model)
cord_lb = Label(advance_frame, text=lang["offset"])
x_entry = Entry(advance_frame, textvariable=xvar, width=5)
y_entry = Entry(advance_frame, textvariable=yvar, width=5)
z_entry = Entry(advance_frame, textvariable=zvar, width=5)
transparency_lb = Label(advance_frame, text=lang["transparency"])
transparency_entry = Scale(advance_frame, variable=sliderVar,
                           length=200, from_=0, to=100,tickinterval=10,
                           orient=HORIZONTAL)
r = 0
modle_name_entry.grid(row=r, column=1)
modle_name_lb.grid(row=r, column=0)
add_bt.grid(row=r, column=2)
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
delete_bt.grid(row=r,column=2)
r += 1

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

r = 0
about_frame.grid(row=r, column=2)
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
r += 2
advanced_check.grid(row=r, column=0)
export_check.grid(row=r, column=1)
save_bt.grid(row=r, column=2)

root.mainloop()
