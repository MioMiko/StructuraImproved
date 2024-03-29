"""export armor_stand.entity.json"""

import json
from pathlib import Path

ROOT = Path(__file__).parent


class Entity:
    # control the entity.json file

    __slots__ = ("stand","geos","textures")

    def __init__(self):
        self.stand = json.loads((ROOT / "res/vanilla/armor_stand.entity.json")
                                .read_text("utf-8"))

        desc = self.stand["minecraft:client_entity"]["description"]
        desc["materials"]["ghost_blocks"] = "entity_alphablend"
        desc["animations"]["scale"] = "animation.armor_stand.ghost_blocks.scale"
        desc["scripts"]["animate"].append("scale")
        desc["render_controllers"].append("controller.render.armor_stand.ghost_blocks")
        desc["textures"]["default"] = "textures/entity/armor_stand"
        desc["geometry"]["default"] = "geometry.armor_stand.larger_render"
        for i in range(13):
            desc["textures"][f"pose_num_{i}"] = f"textures/entity/pose_num_{i}"
        desc["geometry"]["pose_num"] = "geometry.armor_stand.pose_num"
        desc["render_controllers"].append("controller.render.armor_stand.pose_num")

        self.geos = desc["geometry"]
        self.textures =  desc["textures"]

    def add_model(self, name):
        name = f"ghost_blocks_{name}"
        self.geos[name] = f"geometry.armor_stand.{name}"
        self.textures[name] = f"textures/entity/{name}"

    def export(self, zip_file):
        path = "entity/armor_stand.entity.json"
        zip_file.writestr(path,json.dumps(self.stand, indent=2))
