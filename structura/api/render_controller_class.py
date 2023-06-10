"""generte render_controller.json"""

import json

RCNAME = "controller.render.armor_stand.ghost_blocks"

def init_rc():
    return {
        "format_version": "1.8.0",
        "render_controllers": {
            RCNAME: {
                "materials": ({"*": "Material.ghost_blocks"},),}}}

class RenderController:
    """control which model to display when nametag is changed"""

    __slots__ = ("rc","geometry","textures")

    def __init__(self):
        self.rc = init_rc()
        self.geometry = "{}"
        self.textures = "{}"

    def add_model(self, model_name, name):
        new_geo = f"query.get_name == '{model_name}' ? Geometry.ghost_blocks_{name} : ({{}})"
        self.geometry = self.geometry.format(new_geo)
        new_texture = f"query.get_name == '{model_name}' ? Texture.ghost_blocks_{name} : ({{}})"
        self.textures = self.textures.format(new_texture)

    def export(self, zip_file):
        self.geometry = self.geometry.format("Geometry.default")
        self.textures = self.textures.format("Texture.default")
        self.rc["render_controllers"][RCNAME]["geometry"] = self.geometry
        self.rc["render_controllers"][RCNAME]["textures"] = (self.textures,)

        rcpath = ("render_controllers/"
                  "armor_stand.ghost_blocks.render_controllers.json")
        zip_file.writestr(rcpath, json.dumps(self.rc, indent=2))

class BigModelRenderController:
    """control which model to display when pose is changed"""

    __slots__ = ("rc","geometry","textures")

    def __init__(self):
        self.rc = init_rc()
        rc = self.rc["render_controllers"][RCNAME]
        rc["arrays"] = {
            "textures": {"Array.textures": []},
            "geometries": {"Array.geometry": []},
        }
        rc["geometry"] = "Array.geometry[variable.armor_stand.pose_index]"
        rc["textures"] = ("Array.textures[variable.armor_stand.pose_index]",)
        self.textures = rc["arrays"]["textures"]["Array.textures"]
        self.geometry = rc["arrays"]["geometries"]["Array.geometry"]

    def add_model(self, _, name):
        self.geometry.append(f"Geometry.ghost_blocks_{name}")
        self.textures.append(f"Texture.ghost_blocks_{name}")

    def export(self, zip_file):
        if (length := len(self.geometry)) < 13:
            self.geometry.extend(("Geometry.default",)*(13-length))
            self.textures.extend(("Texture.default",)*(13-length))
        rcpath = ("render_controllers/"
                  "armor_stand.ghost_blocks.render_controllers.json")
        zip_file.writestr(rcpath, json.dumps(self.rc, indent=2))
