"""generating geo.json file and texture file for each model"""

from collections import Counter,deque
import json
import os
from typing import NewType
import numpy as np
from PIL import Image

debug = False

FilePath = NewType("FilePath",str)
Direction = NewType("FilePath",str)

class default_key_dict(dict):
    def __missing__(self,key):
        return self["default"]

class armorstandgeo:

    __slots__ = ("name","stand","offsets","alpha","geometry","uv_map",
                 "blocks","bones","material_list","uv_height","uv_deque")

    ## we load all of these items containing the mapping of blocks to the some property that is either hidden, implied or just not clear
    ## custom look up table i wrote to help with rotations, error messages dump if somehting has undefined rotations
    with open("lookups/block_rotation.json",encoding="utf-8") as f:
        block_rotations = json.load(f)
    with open("lookups/block_shapes.json",encoding="utf-8") as f:
        block_shapes = json.load(f)
    with open("lookups/block_uv.json",encoding="utf-8") as f:
        block_uv = json.load(f)
    with open("lookups/block_ref.json",encoding="utf-8") as f:
        block_ref = json.load(f)

    def __init__(self, name:str, alpha:float = 0.8, offsets=(0,0,0)):
        self.name = name.replace(" ","_").lower()
        self.stand = {}
        self.offsets = (offsets[0]+8,offsets[1],offsets[2]+7)
        self.alpha = alpha
        self.geometry = {}
        self._stand_init()
        self.uv_map: dict[FilePath,int] = {}
        self.blocks = {}
        self.bones = []
        self.material_list = Counter()
        self.uv_height = 0
        self.uv_deque = deque()

    def _stand_init(self) -> None:
        """helper function to initialize the dictionary that will be exported as the json object"""

        self.stand = {
            "format_version": "1.12.0",
            "minecraft:geometry": ({
                "description": {
                    "identifier": f"geometry.armor_stand.ghost_blocks_{self.name}",
                    "texture_width": 1,
                    "visible_bounds_offset": (0.0,1.5,0.0),
                    "visible_bounds_width" : 5120,
                    "visible_bounds_height" : 5120,
                },
                "bones": [{"name": "ghost_blocks","pivot": (-8,0,8)}]
            },)
        }
        self.geometry = self.stand['minecraft:geometry'][0]

    def export(self, pack_name):
        """
        This exporter just packs up the armorstand json files and dumps them where it should go
        As well as exports the UV file
        """

        self.uv_height = ((self.uv_height + 15) // 16) * 16
        self.geometry["description"]["texture_height"] = self.uv_height//16
        path_to_geo = (
            f"cache/{pack_name}/models/entity/armor_stand.ghost_blocks_{self.name}.geo.json")
        os.makedirs(os.path.dirname(path_to_geo), exist_ok=True)

        i = 0
        for block in self.geometry["bones"]:
            if "name" not in block.keys():
                block["name"] = f"empty_row+{i}"
                block["parent"] = "ghost_blocks"
                block["pivot"] = (0.5,0.5,0.5)
                i += 1

        with open(path_to_geo, "w", encoding="utf-8") as json_file:
            json.dump(self.stand, json_file, indent = 2 if debug else None)
        texture_path = f"cache/{pack_name}/textures/entity/ghost_blocks_{self.name}.png"
        os.makedirs(os.path.dirname(texture_path), exist_ok=True)
        self._save_uv(texture_path)

    def _save_uv(self, name):
        """pop uv to make sprite and save it"""

        if self.uv_height == 0:
            print("No Blocks Were found")
        else:
            end = 0
            sprite = np.empty((self.uv_height,16,4),np.uint8)
            while self.uv_deque:
                uv = self.uv_deque.popleft()
                start = end
                end += uv.shape[0]
                sprite[start:end,:,:] = uv
            im = Image.fromarray(sprite)
            im.save(name)

    def make_layer(self, y:int):
        """
        sets up a layer for us to refference in the animation controller later 
        Layers are moved during the poses
        """

        layer_name = f"layer_{y}"
        self.geometry["bones"].append(
            {"name": layer_name, "pivot": (-8, 0, 8), "parent": "ghost_blocks"})

    def _add_material(self,name,variant,lit,data):
        material = None
        block_ref = self.block_ref[name]
        if lit and variant+"_lit" in block_ref and \
                (material := block_ref[variant+"_lit"].get("material")):
            pass
        elif variant in block_ref and \
                (material := block_ref[variant].get("material")):
            pass
        elif  "default" in block_ref and \
                (material := block_ref["default"].get("material")):
            pass

        if material == "ignore":
            return

        if material:
            for material_name, data_list in material.items():
                self.material_list[material_name] += default_key_dict(data_list)[data]
        else:
            material_name = name + (
                            f"_{variant}" if variant != "default" else "") + (
                            "_lit" if lit else "")
            self.material_list[material_name] += 1

    def make_block(self ,x:int, y:int, z:int, block, make_list:bool) -> None:
        """
        Make_block handles all the block processing.
        This function does need cleanup and probably should be broken into other helperfunctions for ledgiblity.
        """

        block_name = block[0]
        rot,variant,lit,data,skip = block[1]
        del skip

        if debug:
            print(block_name,variant)

        block_ref = self.block_ref[block_name]
        if len(block_ref["definition"]) == 1:
            shape = uv = rot_type = block_ref["definition"][0]
        else:
            shape, uv, rot_type = block_ref["definition"]

        if make_list:
            self._add_material(block_name,variant,lit,data)

        if shape == "ignore":
            return

        # hardcoded exceptions
        if shape == "hopper" and rot != 0:
            data = "side"
        elif uv == "glazed_terracotta":
            data = str(rot)


        if debug and data != "0":
            print(data)

        block_uv = default_key_dict(self.block_uv[uv])[data]
        block_shapes = default_key_dict(self.block_shapes[shape])[data]

        if rot_type in self.block_rotations.keys():
            rotation = self.block_rotations[rot_type][str(rot)]
        else:
            rotation = (0, 0, 0)
            if debug:
                print(f"no rotation for {block_name} found")

        pivot = (
            -x - self.offsets[0] + 0.5,
            y + self.offsets[1] + 0.5,
            z + self.offsets[2] + 0.5
        )
        block = {
            "name": f"block_{x}_{y}_{z}",
            "cubes": [],
            "pivot": pivot,
            "rotation": rotation,
            "parent": f"layer_{y}"
        }

        uv_idx = 0
        for i in range(len(block_shapes["size"])):
            cube = {}
            if len(block_uv["uv_sizes"]["up"]) > i:
                uv_idx = i
            xoff = yoff = zoff = 0
            if "offsets" in block_shapes.keys():
                xoff,yoff,zoff = block_shapes["offsets"][i]
            cube["origin"] = (
                -x + xoff - self.offsets[0],
                y + yoff + self.offsets[1],
                z + zoff + self.offsets[2]
            )
            cube["pivot"] = list(pivot)
            if "pivot" in block_shapes:
                cube["pivot"][0] += block_shapes["pivot"][i][0]
                cube["pivot"][1] += block_shapes["pivot"][i][1]
                cube["pivot"][2] += block_shapes["pivot"][i][2]
            cube["size"] = block_shapes["size"][i]
            cube["inflate"] = -0.03
            if "rot" in block_shapes:
                cube["rotation"] = block_shapes["rot"][i]

            cube_uv = self._block_name_to_uv(block_ref,variant,lit,index=i)
            for direction, offset in block_uv["offset"].items():
                cube_uv[direction]["uv"][0] += offset[uv_idx][0]
                cube_uv[direction]["uv"][1] += offset[uv_idx][1]
            uv_size = block_uv["uv_sizes"]
            for direction in tuple(cube_uv):
                if uv_size[direction][uv_idx] is None:
                    cube_uv.pop(direction)
                    continue
                cube_uv[direction]["uv_size"] = uv_size[direction][uv_idx]

            cube["uv"] = cube_uv
            block["cubes"].append(cube)

        self.geometry["bones"].append(block)

    def _append_uv_image(self, new_image_filename):
        """
        push uv to the deque
        return the height of the uv in final sprite
        """

        image = Image.open(new_image_filename)
        impt = np.array(image)
        shape = list(impt.shape)
        if shape[1] > 16:
            shape[1] = 16
            impt=impt[:,0:16,:]
        # print(new_image_filename)
        # print(impt)
        image_array = np.ones((shape[0], 16, 4),np.uint8)*255
        image_array[0:shape[0], 0:shape[1], 0:impt.shape[2]] = impt
        image_array[:, :, 3] = image_array[:, :, 3] * self.alpha

        self.uv_height += shape[0]
        self.uv_deque.append(image_array)
        return self.uv_height - shape[0]

    def _block_name_to_uv(self, block_ref, variant="default", lit=False, index=0):
        """helper function maps the the section of the uv file to the side of the block"""

        temp_uv: [Direction,int] = {}
        texture_files: dict[Direction,FilePath] = (
            self._get_block_texture_paths(block_ref,variant,lit,index))

        for key,uv in texture_files.items():
            if uv not in self.uv_map:
                self.uv_map[uv] = self._append_uv_image(f"lookups/uv/blocks/{uv}.png")/16
            temp_uv[key] = {"uv": [0, self.uv_map[uv]]}

        return temp_uv

    def _get_block_texture_paths(self, block_ref, variant = "",lit=False, index = 0):
        """helper function for getting the texture file locations"""

        if not (lit and (texture_layout := block_ref.get(variant+"_lit"))):
            texture_layout = default_key_dict(block_ref)[variant]
        texture_layout = texture_layout["textures"]
        textures: dict[Direction,FilePath] = {}

        if isinstance(texture_layout,dict):
            if index >= (i := len(texture_layout["up"])):
                index = i - 1
            if "side" in texture_layout.keys():
                textures["east"] = texture_layout["side"][index]
                textures["west"] = texture_layout["side"][index]
                textures["north"] = texture_layout["side"][index]
                textures["south"] = texture_layout["side"][index]
            if "east" in texture_layout.keys():
                textures["east"] = texture_layout["east"][index]
            if "west" in texture_layout.keys():
                textures["west"] = texture_layout["west"][index]
            if "north" in texture_layout.keys():
                textures["north"] = texture_layout["north"][index]
            if "south" in texture_layout.keys():
                textures["south"] = texture_layout["south"][index]
            if "down" in texture_layout.keys():
                textures["down"] = texture_layout["down"][index]
            if "up" in texture_layout.keys():
                textures["up"] = texture_layout["up"][index]
        elif isinstance(texture_layout,list):
            if index >= (i := len(texture_layout)):
                index = i - 1
            textures["east"] = texture_layout[index]
            textures["west"] = texture_layout[index]
            textures["north"] = texture_layout[index]
            textures["south"] = texture_layout[index]
            textures["up"] = texture_layout[index]
            textures["down"] = texture_layout[index]

        return textures
