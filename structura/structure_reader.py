import nbtlib
import json
import numpy as np

debug = False

class structure_processor:
    # read the structure file and draw the block info

    __slots__ = ("NBTfile","index","size","palette","block_entities","cube")
    """
    cube is a list of index mapping to palette by z,y,x order
    palette is a list of block information
    """

    with open("lookups/nbt_defs.json",encoding="utf-8") as f:
        nbt_def = json.load(f)

    def __init__(self, file):
        if type(file) is dict:
            self.NBTfile = file
        else:
            self.NBTfile = nbtlib.load(file, byteorder='little')

        if "" in self.NBTfile.keys():
            self.NBTfile = self.NBTfile[""]

        self.size = self.NBTfile["size"]
        self.cube = np.array(self.NBTfile["structure"]["block_indices"][0],dtype=np.int32)
        self.cube.shape = self.size
        self.block_entities = self.NBTfile["structure"]["palette"]["default"]["block_position_data"]

        self.palette = list(self.NBTfile["structure"]["palette"]["default"]["block_palette"])
        # process palette
        for i, block in enumerate(self.palette):
            self.palette[i] = (
                block["name"].replace("minecraft:",""),
                self.process_states(block["states"])
            )

        self.index = np.arange(0,np.prod(self.size),1,np.int32)
        self.index.shape = self.size

    def get_block(self, x, y, z):
        block_entity_index = str(self.index[x,y,z])
        block_info = self.palette[self.cube[x,y,z]]
        if block_entity_index in self.block_entities.keys():
            block_entity = self.block_entities[block_entity_index].get("block_entity_data")
            if block_entity:
                block_info = self.process_block_entity(block_info,block_entity)
        return block_info

    def process_states(self,block_states):
        rot = None
        top = False
        lit = False
        data = "0"
        skip = False
        variant = "default"

        if not block_states:
            return (rot, variant, lit, data, skip)

        # variant and lit determine the texture of blocks together
        for key in self.nbt_def["variant"]:
            if key in block_states.keys():
                variant = str(block_states[key])
                break

        for key in self.nbt_def["lit"]:
            if key in block_states.keys():
                lit = bool(block_states[key])
                break

        for key in self.nbt_def["rot"]:
            if key in block_states.keys():
                try:
                    rot = int(block_states[key])
                except:
                    rot = str(block_states[key])
                break

        # top and data determines the offset of block together
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
        return (rot, variant, lit, data, skip)


    def process_block_entity(self,block_info,block_entity):
        rot, variant, lit, data, skip = block_info[1]

        for key in self.nbt_def["block_entity_variant"]:
            if key in block_entity.keys():
                variant = str(block_entity[key])
                break

        for key in self.nbt_def["block_entity_rot"]:
            if key in block_entity.keys():
                rot = str(block_entity[key])
                break

        for key in self.nbt_def["block_entity_data"]:
            if key in block_entity.keys():
                data = str(block_entity[key])
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
        return (block_info[0],(rot, variant, lit, data, skip))
