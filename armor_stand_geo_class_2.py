import json
from PIL import Image
import numpy as np
import copy
import os
from collections import Counter,deque

debug = False

class default_key_dict(dict):
    def __missing__(self,key):
        return self["default"]

class armorstandgeo:

    __slots__ = ("name","stand","offsets","alpha","geometry","uv_map",
                 "blocks","bones","material_list","uv_height","uv_deque")

    ## we load all of these items containing the mapping of blocks to the some property that is either hidden, implied or just not clear
    ## custom look up table i wrote to help with rotations, error messages dump if somehting has undefined rotations 
    with open("lookups/block_ref.json",encoding="utf-8") as f:
        block_ref = json.load(f)
    with open("lookups/block_rotation.json",encoding="utf-8") as f:
        block_rotations = json.load(f)
    with open("lookups/block_shapes.json",encoding="utf-8") as f:
        block_shapes = json.load(f)
    with open("lookups/block_uv.json",encoding="utf-8") as f:
        block_uv = json.load(f)
    with open("lookups/block_ref.json",encoding="utf-8") as f:
        block_ref = json.load(f)

    def __init__(self, name, alpha = 0.8,offsets=[0,0,0]):
        self.name = name.replace(" ","_").lower()
        self.stand = {}
        self.offsets = (offsets[0]+8,offsets[1],offsets[2]+7)
        self.alpha = alpha
        self.geometry = {}
        self.stand_init()
        self.uv_map = {}
        self.blocks = {}
        self.bones = []
        self.material_list=Counter()
        self.uv_height = 0
        self.uv_deque = deque()
        ## The stuff below is a horrible cludge that should get cleaned up. +1 karma to whomever has a better plan for this.
        # this is how i determine if something should be thin. it is ugly, but kinda works

    def stand_init(self):
        # helper function to initialize the dictionary that will be exported as the json object
        self.stand = {
            "format_version": "1.12.0",
            "minecraft:geometry": [{
                "description": {
                    "identifier": f"geometry.armor_stand.ghost_blocks_{self.name}",
                    "texture_width": 1,
                    "visible_bounds_offset": (0.0,1.5,0.0),
                    "visible_bounds_width" : 5120,
                    "visible_bounds_height" : 5120,
                },
                "bones": [{"name": "ghost_blocks","pivot": (-8,0,8)}]
            }]
        }
        self.geometry = self.stand['minecraft:geometry'][0]

    def export(self, pack_folder):
        ## This exporter just packs up the armorstand json files and dumps them where it should go. as well as exports the UV file
        # self.add_blocks_to_bones()
        self.geometry["description"]["texture_height"] = self.uv_height/16
        self.stand["minecraft:geometry"] = [self.geometry] ## this is insuring the geometries are imported, there is an implied refference other places.
        path_to_geo = "{}/models/entity/armor_stand.ghost_blocks_{}.geo.json".format(
            pack_folder,self.name)
        os.makedirs(os.path.dirname(path_to_geo), exist_ok=True)
        i = 0
        bones  = self.geometry["bones"]
        for index in range(len(self.geometry["bones"])):
            if "name" not in bones[index].keys():
                bones[index]["name"]="empty_row+{}".format(i)
                bones[index]["parent"]="ghost_blocks"
                bones[index]["pivot"] = (0.5,0.5,0.5)
                i += 1

        with open(path_to_geo, "w",encoding="utf-8") as json_file:
            json.dump(self.stand, json_file, indent = 2 if debug else None)
        texture_name = "{}/textures/entity/ghost_blocks_{}.png".format(
            pack_folder,self.name)
        os.makedirs(os.path.dirname(texture_name), exist_ok=True)
        self.save_uv(texture_name)


    def make_layer(self, y):
        # sets up a layer for us to refference in the animation controller later. Layers are moved during the poses 
        layer_name = "layer_{}".format(y)
        self.geometry["bones"].append(
            {"name": layer_name, "pivot": [-8, 0, 8], "parent": "ghost_blocks"})

    def add_material(self,name,variant,lit,data):
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
            for name,data_list in material.items():
                self.material_list[name] += default_key_dict(data_list)[data]
        else:
            name = name + (f"_{variant}" if variant != "default" else "") + \
                              ("_lit" if lit else "")
            self.material_list[name] += 1

    def make_block(self,x,y,z,block,make_list):
        # make_block handles all the block processing, This function does need cleanup and probably should be broken into other helperfunctions for ledgiblity.

        block_name = block[0]
        rot,variant,lit,data,skip = block[1]

        if debug:
            print(block_name,variant)

        block_ref = self.block_ref[block_name]
        if len(block_ref["definition"]) == 1:
            shape = block_ref["definition"][0]
            uv = block_ref["definition"][0]
            rot_type = block_ref["definition"][0]
        else:
            shape = block_ref["definition"][0]
            uv = block_ref["definition"][1]
            rot_type = block_ref["definition"][2]

        if make_list:
            self.add_material(block_name,variant,lit,data)

        if shape == "ignore":
            return

        ## hardcoded to true for now, but this is when the variants will be called
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
            rotation = [0, 0, 0]
            if debug:
                print("no rotation for {} found".format(block_name))

        block = {
            "name": f"block_{x}_{y}_{z}",
            "cubes": [],
            "pivot": block_shapes["center"],
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
            cube["pivot"] = (
                -x - self.offsets[0] + 0.5,
                y + self.offsets[1] + 0.5,
                z + self.offsets[2] + 0.5
            )
            cube["size"] = block_shapes["size"][i]
            cube["inflate"] = -0.03
            cube["rotation"] = rotation.copy()
            if "rot" in block_shapes.keys():
                for j in range(3):
                    cube["rotation"][j] += block_shapes["rot"][i][j]

            cube_uv = self.block_name_to_uv(block_ref,variant=variant,lit=lit,index=i)
            uv_offset = block_uv["offset"]
            cube_uv["up"]["uv"][0] += uv_offset["up"][uv_idx][0]
            cube_uv["up"]["uv"][1] += uv_offset["up"][uv_idx][1]
            cube_uv["down"]["uv"][0] += uv_offset["down"][uv_idx][0]
            cube_uv["down"]["uv"][1] += uv_offset["down"][uv_idx][1]
            cube_uv["east"]["uv"][0] += uv_offset["east"][uv_idx][0]
            cube_uv["east"]["uv"][1] += uv_offset["east"][uv_idx][1]
            cube_uv["west"]["uv"][0] += uv_offset["west"][uv_idx][0]
            cube_uv["west"]["uv"][1] += uv_offset["west"][uv_idx][1]
            cube_uv["north"]["uv"][0] += uv_offset["north"][uv_idx][0]
            cube_uv["north"]["uv"][1] += uv_offset["north"][uv_idx][1]
            cube_uv["south"]["uv"][0] += uv_offset["south"][uv_idx][0]
            cube_uv["south"]["uv"][1] += uv_offset["south"][uv_idx][1]
            uv_size = block_uv["uv_sizes"]
            cube_uv["up"]["uv_size"] = uv_size["up"][uv_idx]
            cube_uv["down"]["uv_size"] = uv_size["down"][uv_idx]
            cube_uv["east"]["uv_size"] = uv_size["east"][uv_idx]
            cube_uv["west"]["uv_size"] = uv_size["west"][uv_idx]
            cube_uv["north"]["uv_size"] = uv_size["north"][uv_idx]
            cube_uv["south"]["uv_size"] = uv_size["south"][uv_idx]

            cube["uv"] = cube_uv
            block["cubes"].append(cube)

        self.geometry["bones"].append(block)

    def append_uv_image(self, new_image_filename):
        # push uv to the deque
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

    def save_uv(self,name):
        # pop uv to make sprite and save it
        if self.uv_height == 0:
            print("No Blocks Were found")
        else:
            end = 0
            sprite = np.empty((self.uv_height, 16, 4),np.uint8)
            while self.uv_deque:
                uv = self.uv_deque.popleft()
                start = end
                end += uv.shape[0]
                sprite[start:end,:,:] = uv
            im = Image.fromarray(sprite)
            im.save(name)

    def block_name_to_uv(self, block_ref, variant = "",lit=False,index=0):
        # helper function maps the the section of the uv file to the side of the block
        temp_uv = {}
        texture_files = self.get_block_texture_paths(block_ref,variant,lit,index)

        for key,uv in texture_files.items():
            if uv not in self.uv_map.keys():
                self.uv_map[uv] = self.uv_height/16
                self.append_uv_image(f"lookups/uv/blocks/{uv}.png")
            temp_uv[key] = {"uv": [0, self.uv_map[uv]]}

        return temp_uv

    def get_block_texture_paths(self, block_ref, variant = "",lit=False, index = 0):
        # helper function for getting the texture locations from the vanilla files.
        if not (lit and (textureLayout := block_ref.get(variant+"_lit"))):
            textureLayout = default_key_dict(block_ref)[variant]
        textureLayout = textureLayout["textures"]
        textures = {}

        if type(textureLayout) is dict:
            if index >= (i := len(textureLayout["up"])):
                index = i - 1
            if "side" in textureLayout.keys():
                textures["east"] = textureLayout["side"][index]
                textures["west"] = textureLayout["side"][index]
                textures["north"] = textureLayout["side"][index]
                textures["south"] = textureLayout["side"][index]
            if "east" in textureLayout.keys():
                textures["east"] = textureLayout["east"][index]
            if "west" in textureLayout.keys():
                textures["west"] = textureLayout["west"][index]
            if "north" in textureLayout.keys():
                textures["north"] = textureLayout["north"][index]
            if "south" in textureLayout.keys():
                textures["south"] = textureLayout["south"][index]
            if "down" in textureLayout.keys():
                textures["down"] = textureLayout["down"][index]
            if "up" in textureLayout.keys():
                textures["up"] = textureLayout["up"][index]
        elif type(textureLayout) is list:
            if index >= (i := len(textureLayout)):
                index = i - 1
            textures["east"] = textureLayout[index]
            textures["west"] = textureLayout[index]
            textures["north"] = textureLayout[index]
            textures["south"] = textureLayout[index]
            textures["up"] = textureLayout[index]
            textures["down"] = textureLayout[index]

        return textures
