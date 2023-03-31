"""generate animation.json"""

import json


class Animation:
    """control the scale animation when change poses"""

    __slots__ = ("sizing",)

    poses = (
        "animation.armor_stand.no_pose",
        "animation.armor_stand.solemn_pose",
        "animation.armor_stand.athena_pose",
        "animation.armor_stand.brandish_pose",
        "animation.armor_stand.honor_pose",
        "animation.armor_stand.entertain_pose",
        "animation.armor_stand.salute_pose",
        "animation.armor_stand.riposte_pose",
        "animation.armor_stand.zombie_pose",
        "animation.armor_stand.cancan_a_pose",
        "animation.armor_stand.cancan_b_pose",
        "animation.armor_stand.hero_pose",
        "animation.armor_stand.default_pose"
    )

    default_size = {
        "format_version": "1.8.0",
        "animations": {"animation.armor_stand.ghost_blocks.scale": {
            "loop": True,
            "bones": {
            "ghost_blocks": {"scale": 1.28}}}}
    }

    def __init__(self):
        pathtofile = "lookups/vanilla/armor_stand.animation.json"
        with open(pathtofile, encoding="utf-8") as f:
            self.sizing = json.load(f)

    def insert_layer(self, y):
        name = f"layer_{y}"
        self.sizing["animations"][self.poses[12]]["bones"][name] = {"scale": 12.5}
        self.sizing["animations"][self.poses[y%12]]["bones"][name] = {"scale": 12.5}

    def export(self, zip_file):
        path_to_ani = "animations/armor_stand.animation.json"
        zip_file.writestr(path_to_ani, json.dumps(self.sizing, indent=2))
        path_to_rc = "animations/armor_stand.ghost_blocks.scale.animation.json"
        zip_file.writestr(path_to_rc, json.dumps(self.default_size, indent=2))
