import json
import os


class animations:

    __slots__ = ("default_size","sizing","poses")

    def __init__(self):
        self.default_size = {
            "format_version": "1.8.0",
            "animations": {"animation.armor_stand.ghost_blocks.scale": {
                "loop": True,
                "bones": {
                "ghost_blocks": {"scale": 1.28}}}}
        }
        pathtofile = "lookups/vanilla/armor_stand.animation.json"
        with open(pathtofile) as f:
            self.sizing = json.load(f)
        self.poses = (
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

    def insert_layer(self, y):
        name = f"layer_{y}"
        self.sizing["animations"][self.poses[12]]["bones"][name] = {"scale": 12.5}
        self.sizing["animations"][self.poses[y%12]]["bones"][name] = {"scale": 12.5}

    def export(self, pack_name):
        path_to_ani = f"cache/{pack_name}/animations/armor_stand.animation.json"
        path_to_rc = f"cache/{pack_name}/animations/armor_stand.ghost_blocks.scale.animation.json"

        os.makedirs(os.path.dirname(path_to_ani), exist_ok=True)

        with open(path_to_ani, "w") as json_file:
            json.dump(self.sizing, json_file, indent=2)
        with open(path_to_rc, "w") as json_file:
            json.dump(self.default_size, json_file, indent=2)
