import json
import os


class armorstand:
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
        self.geos[prog_name] = "geometry.armor_stand.{}".format(prog_name)
        self.textures[prog_name] = "textures/entity/{}".format(prog_name)

    def export(self, pack_name):
        path = f"cache/{pack_name}/entity/armor_stand.entity.json"
        os.makedirs(os.path.dirname(path), exist_ok = True)

        with open(path,"w",encoding="utf-8") as json_file:
            json.dump(self.stand, json_file, indent=2)
