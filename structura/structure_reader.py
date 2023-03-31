import json
import nbtlib
import numpy as np

debug = False

def nbt_to_str(nbt):
    if isinstance(nbt,int):
        return str(int(nbt))
    if isinstance(nbt,str):
        return str(nbt)
    if isinstance(nbt,float):
        return str(float(nbt))

class StructureProcessor:
    """read the structure file and draw the block info"""

    __slots__ = ("index","size","palette","block_entities","cube")
    """
    cube is a list of index mapping to palette by z,y,x order
    palette is a list of block information
    """

    with open("lookups/nbt_defs.json",encoding="utf-8") as f:
        nbt_def = json.load(f)

    def __init__(self, file):

        nbt = nbtlib.load(file, byteorder='little')

        self.size = nbt["size"]
        self.cube = np.array(nbt["structure"]["block_indices"][0],dtype=np.int32).reshape(self.size)
        self.block_entities = nbt["structure"]["palette"]["default"]["block_position_data"]
        self.palette = tuple(map(self._process_palette, nbt["structure"]["palette"]["default"]["block_palette"]))
        self.index = np.arange(0, np.prod(self.size), 1, np.int32).reshape(self.size)

    def get_block(self, x, y, z):
        """
        get the block info by given position

        Return:
            Option[Tuple[str, str, str, bool, str]]:
                elem 1: block name without "minecraft:"
                elem 2: rotation of the block
                elem 3: texture variant of the block
                elem 4: a bool furthur describe the texture variant
                elem 5: other data, determine the shape and uv variant of the block
                if the block does't needed processing, it returns None
        """

        block_entity_index = str(self.index[x,y,z])
        block_info = self.palette[self.cube[x,y,z]]
        if block_entity_index in self.block_entities.keys():
            block_entity = self.block_entities[block_entity_index].get("block_entity_data")
            if block_entity:
                block_info = self._process_block_entity(block_info,block_entity)
        return block_info

    @classmethod
    def _process_palette(cls, block_palette):
        rot = None
        lit = False
        data = "0"
        variant = "default"

        blk_name = block_palette["name"].replace("minecraft:", "")
        block_states = block_palette["states"]

        if not block_states:
            return (blk_name, rot, variant, lit, data)

        for key in cls.nbt_def["skip"]:
            if key in block_states.keys():
                if bool(block_states[key]):
                    return None

        # variant and lit determine the texture of blocks together
        for key in cls.nbt_def["variant"]:
            if key in block_states.keys():
                variant = nbt_to_str(block_states[key])
                break

        for key in cls.nbt_def["lit"]:
            if key in block_states.keys():
                lit = bool(block_states[key])
                break

        for key in cls.nbt_def["rot"]:
            if key in block_states.keys():
                rot = nbt_to_str(block_states[key])
                break

        # data determines the offset of block together
        for key in cls.nbt_def["data"]:
            if key in block_states.keys():
                data = nbt_to_str(block_states[key])
                break

        for key in cls.nbt_def["top"]:
            if key in block_states.keys():
                if block_states[key]:
                    data += "_top"
                    break

        return (blk_name, rot, variant, lit, data)

    @classmethod
    def _process_block_entity(cls, block_info, block_entity):
        blk_name, rot, variant, lit, data = block_info

        for key in cls.nbt_def["block_entity_variant"]:
            if key in block_entity.keys():
                variant = nbt_to_str(block_entity[key])
                break

        for key in cls.nbt_def["block_entity_rot"]:
            if key in block_entity.keys():
                rot = nbt_to_str(block_entity[key])
                break

        for key in cls.nbt_def["block_entity_data"]:
            if key in block_entity.keys():
                data = nbt_to_str(block_entity[key])
                break

        # exception
        if "id" in block_entity:
            if block_entity["id"] == "Skull":
                if block_entity["SkullType"] == 5:
                    data = "dragon"
                if rot == "1":
                    rot = nbt_to_str(block_entity["Rotation"])
                    data += "_standing"
            elif block_entity["id"] == "Hopper":
                variant = nbt_to_str(rot)

        if debug:
            print((rot, variant, lit, data))
        return (blk_name, rot, variant, lit, data)
