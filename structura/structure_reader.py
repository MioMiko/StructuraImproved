import nbtlib
import json
import numpy as np

debug = False

class process_structure:
# read the structure file and draw the block info

    __slots__ = ("NBTfile","blocks","size","palette","block_entities","cube")

    with open("lookups/nbt_defs.json",encoding="utf-8") as f:
        nbt_def = json.load(f)

    def __init__(self, file):
        if type(file) is dict:
            self.NBTfile = file
        else:
            self.NBTfile = nbtlib.load(file, byteorder='little')

        if "" in self.NBTfile.keys():
            self.NBTfile = self.NBTfile[""]

        self.blocks = list(map(int, self.NBTfile["structure"]["block_indices"][0]))
        self.size = list(map(int, self.NBTfile["size"]))
        self.palette = self.NBTfile["structure"]["palette"]["default"]["block_palette"]
        self.block_entities = self.NBTfile["structure"]["palette"]["default"]["block_position_data"]

        # get block map
        self.cube = np.empty((self.size[0],self.size[1],self.size[2],2), int)
        i = 0
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                for z in range(self.size[2]):
                    self.cube[x][y][z] = (self.blocks[i],i)
                    i += 1

    def get_block(self, x, y, z):
        index = self.cube[x, y, z]
        block_entity = {}
        if str(index[1]) in self.block_entities.keys():
            block_entity = self.block_entities[str(index[1])].get("block_entity_data",{})
        block_palette = self.palette[int(index[0])]
        return (
            block_palette["name"].replace("minecraft:",""),
            self.process_block(block_palette["states"],block_entity)
        )

    def process_block(self,block_states,block_entity):
        rot = None
        top = False
        lit = False
        data = "0"
        skip = False
        variant = "default"

        # variant and lit determine the texture of blocks together
        for key in self.nbt_def["block_entity_variant"]:
            if key in block_entity.keys():
                variant = str(block_entity[key])
                break
        else:
            for key in self.nbt_def["variant"]:
                if key in block_states.keys():
                    variant = str(block_states[key])
                    break

        for key in self.nbt_def["lit"]:
            if key in block_states.keys():
                lit = bool(block_states[key])
                break

        for key in self.nbt_def["block_entity_rot"]:
            if key in block_entity.keys():
                rot = str(block_entity[key])
                break
        else:
            for key in self.nbt_def["rot"]:
                if key in block_states.keys():
                    try:
                        rot = int(block_states[key])
                    except:
                        rot = str(block_states[key])
                    break

        # top and data determines the offset of block together
        for key in self.nbt_def["block_entity_data"]:
            if key in block_entity.keys():
                data = str(block_entity[key])
                break
        else:
            for key in self.nbt_def["data"]:
                if key in block_states.keys():
                    try:
                        data = str(int(block_states[key]))
                    except:
                        data = str(block_states[key])
                    break

        for key in self.nbt_def["top"]:
            if key in block_states.keys():
                if block_states[key]:
                    data += "_top"
                    break

        for key in self.nbt_def["skip"]:
            if key in block_states.keys():
                skip = bool(block_states[key])
                break

        # exception
        if "id" in block_entity:
            if block_entity["id"] == "Skull":
                if block_entity["SkullType"] == 5:
                    data = "dragon"
                if rot == 1:
                    rot = str(block_entity["Rotation"])
                    data += "_standing"
            elif block_entity["id"] == "Hopper":
                variant = str(rot)

        if debug:
            print((rot, variant, lit, data, skip))
        return (rot, variant, lit, data, skip)
