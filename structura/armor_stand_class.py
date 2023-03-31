"""export armor_stand.entity.json"""

import json


class Entity:
    # control the entity.json file

    __slots__ = ("stand","geos","textures")

    def __init__(self):
        with open("lookups/vanilla/armor_stand.entity.json",encoding="utf-8") as f:
            self.stand = json.load(f)

        desc = self.stand["minecraft:client_entity"]["description"]
        desc["materials"]["ghost_blocks"] = "entity_alphablend"
        desc["animations"]["scale"] = "animation.armor_stand.ghost_blocks.scale"
        desc["scripts"]["animate"].append("scale")
        desc["render_controllers"].append("controller.render.armor_stand.ghost_blocks")
        desc["textures"]["default"] = "textures/entity/armor_stand"
        desc["geometry"]["default"] = "geometry.armor_stand.larger_render"

        self.geos = desc["geometry"]
        self.textures =  desc["textures"]

    def add_model(self, name):
        prog_name = "ghost_blocks_{}".format(name.replace(" ","_").lower())
        self.geos[prog_name] = f"geometry.armor_stand.{prog_name}"
        self.textures[prog_name] = f"textures/entity/{prog_name}"

    def export(self, zip_file):
        path = "entity/armor_stand.entity.json"
        zip_file.writestr(path,json.dumps(self.stand, indent=2))
