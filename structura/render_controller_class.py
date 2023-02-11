import json
import os

class render_controller:

    __slots__ = ("rc","geometry","textures")
    rcname = "controller.render.armor_stand.ghost_blocks"

    def __init__(self):
        self.rc = {
            "format_version": "1.8.0",
            "render_controllers": {
                self.rcname: {
                    "materials": [{"*": "Material.ghost_blocks"}],
                }
            }
        }

        self.geometry = "{}"
        self.textures = "{}"

    def add_model(self,name_raw):
        name = name_raw.replace(" ","_").lower()
        new_geo = f"query.get_name == '{name_raw}' ? Geometry.ghost_blocks_{name} : ({{}})"
        self.geometry = self.geometry.format(new_geo)
        new_texture = f"query.get_name == '{name_raw}' ? Texture.ghost_blocks_{name} : ({{}})"
        self.textures = self.textures.format(new_texture)

    def export(self, pack_name):
        self.geometry = self.geometry.format("Geometry.default")
        self.textures = self.textures.format("Texture.default")
        self.rc["render_controllers"][self.rcname]["geometry"] = self.geometry
        self.rc["render_controllers"][self.rcname]["textures"] = [self.textures]

        rc = "armor_stand.ghost_blocks.render_controllers.json"
        rcpath = f"cache/{pack_name}/render_controllers/{rc}"
        os.makedirs(os.path.dirname(rcpath), exist_ok = True)

        with open(rcpath, "w+") as json_file:
            json.dump(self.rc, json_file, indent=2)
