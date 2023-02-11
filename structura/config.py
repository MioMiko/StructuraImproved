import tkinter as tk
from tkinter import ttk
import json

class setting_gui():
    def __init__(self,conf,save_path,lang):
        self.conf = conf
        self.path = save_path
        self.lang = lang

        setting = tk.Toplevel()
        self.setting = setting
        setting.title(lang["setting"])

        r = 0
        tk.Label(setting,text=lang["lang"]).grid(row=r,column=0)
        self.language = tk.StringVar()
        lang_option = ttk.Combobox(setting,textvariable=self.language)
        tmp = ("English","简体中文")
        lang_option["value"] = tmp
        lang_option.current(tmp.index(conf["lang"]))
        lang_option.grid(row=r,column=1)

        r += 1
        self.structure_path = tk.StringVar()
        self.structure_path.set(conf["default_structure_path"])
        tk.Label(setting,text=lang["structure_path"]).grid(row=r,column=0)
        tk.Entry(setting,textvariable=self.structure_path).grid(row=r,column=1)
        tk.Button(setting,command=self.browse_structure_path,text=lang["browse"]).grid(row=r,column=2)

        r += 1
        self.save_path = tk.StringVar()
        self.save_path.set(conf["save_path"])
        tk.Label(setting,text=lang["save_path"]).grid(row=r,column=0)
        tk.Entry(setting,textvariable=self.save_path).grid(row=r,column=1)
        tk.Button(setting,command=self.browse_save_path,text=lang["browse"]).grid(row=r,column=2)

        r += 1
        self.info_save_path = tk.StringVar()
        self.info_save_path.set(conf["info_save_path"])
        tk.Label(setting,text=lang["info_save_path"]).grid(row=r,column=0,columnspan=2)
        r += 1
        tk.Entry(setting,textvariable=self.info_save_path).grid(row=r,column=1)
        tk.Button(setting,command=self.browse_info_save_path,text=lang["browse"]).grid(row=r,column=2)

        r += 1
        self.icon_path = tk.StringVar()
        self.icon_path.set(conf["icon_path"])
        tk.Label(setting,text=lang["icon_path"]).grid(row=r,column=0)
        tk.Entry(setting,textvariable=self.icon_path).grid(row=r,column=1)
        tk.Button(setting,command=self.browse_icon_path,text=lang["browse"]).grid(row=r,column=2)

        r += 1
        self.is_overwrite = tk.BooleanVar()
        self.is_overwrite.set(conf["overwrite_same_packname"])
        tk.Checkbutton(setting, text=lang["overwrite_same_packname"], variable=self.is_overwrite).grid(row=r,column=0,columnspan=2)

        r += 1
        tk.Button(setting,text=lang["cancel"],command=setting.destroy).grid(row=r,column=1,sticky="se")
        tk.Button(setting,text=lang["confirm"],command=self.save_conf).grid(row=r,column=2)

    def browse_structure_path(self):
        self.structure_path.set(
            tk.filedialog.askdirectory(initialdir=self.conf["default_structure_path"]))

    def browse_save_path(self):
        self.save_path.set(
            tk.filedialog.askdirectory(initialdir=self.conf["save_path"]))

    def browse_info_save_path(self):
        self.info_save_path.set(
            tk.filedialog.askdirectory(initialdir=self.conf["info_save_path"]))

    def browse_icon_path(self):
        self.icon_path.set(
            tk.filedialog.askopenfilename(
                filetypes=(("Image File", "pack_icon.png"),),
                initialdir=self.conf["icon_path"]
            )
        )

    def save_conf(self):
        self.conf = {
            "lang": self.language.get(),
            "default_structure_path": self.structure_path.get(),
            "save_path": tmp if (tmp := self.save_path.get())[-1] == "/" else f"{tmp}/",
            "info_save_path": tmp if (tmp := self.info_save_path.get())[-1] == "/" else f"{tmp}/",
            "icon_path": self.icon_path.get(),
            "overwrite_same_packname": self.is_overwrite.get()
        }
        with open("config/config.json","w") as f:
            json.dump(self.conf,f)
        self.setting.quit()
