"""generate animation.json"""

import json
from pathlib import Path

ROOT = Path(__file__).parent


class Animation:
    """Control the scale animation when pose is changed"""

    __slots__ = ("sizing","default_size")

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

    def __init__(self):
        self.default_size = {
            "format_version": "1.8.0",
            "animations": {"animation.armor_stand.ghost_blocks.scale": {
                "loop": True,
                "bones": {"ghost_blocks": {"scale": 0.08}}}}}

        pathtofile = "res/vanilla/armor_stand.animation.json"
        self.sizing = json.loads((ROOT / pathtofile).read_text("utf-8"))

    def insert_layer(self, y):
        name = f"layer_{y}"
        self.sizing["animations"][self.poses[12]]["bones"][name] = {"scale": 12.5}
        self.sizing["animations"][self.poses[y%12]]["bones"][name] = {"scale": 12.5}

    def export(self, zip_file):
        path_to_ani = "animations/armor_stand.animation.json"
        zip_file.writestr(path_to_ani, json.dumps(self.sizing, indent=2))
        path_to_rc = "animations/armor_stand.ghost_blocks.scale.animation.json"
        zip_file.writestr(path_to_rc, json.dumps(self.default_size, indent=2))
