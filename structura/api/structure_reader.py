import json
from pathlib import Path
from typing import Optional

import nbtlib
import numpy as np

ROOT = Path(__file__).parent

BlockName = str # block name without "minecraft:"
Rotation = str  # rotation of the block
Variant = str   # texture variant of the block
Lit = bool      # a bool further describe the texture variant
Data = str      # other data, determine the shape and uv variant of the block
BlockInfo = tuple[BlockName, Rotation, Variant, Lit, Data]

def nbt_to_str(nbt):
    if isinstance(nbt,int):
        return str(int(nbt))
    if isinstance(nbt,str):
        return str(nbt)
    if isinstance(nbt,float):
        return str(float(nbt))

class StructureProcessor:
    """
    Read the structure file and draw the block info

    Attributes:
        cube (numpy.ndarray):
            a list of index mapping to palette. each elem represent to a block
        palette (nbtlib.List[nbtlib.Compound]):
            stores block information
        block_entities (nbtlib.Compound[str, nbtlib.Compound])
            stores block entity data
            Key: the index of the block in flattened cube attribute
    """

    __slots__ = ("index","size","palette","block_entities","cube")

    nbt_def = json.loads((ROOT / "res/nbt_defs.json").read_text("utf-8"))

    def __init__(self, file: nbtlib.File | str | bytes | Path):

        if isinstance(file, nbtlib.File):
            nbt = file
        else:
            nbt = nbtlib.load(file, byteorder='little')

        self.size = nbt["size"]
        self.cube = np.array(nbt["structure"]["block_indices"][0],dtype=np.int32).reshape(self.size)
        self.block_entities = nbt["structure"]["palette"]["default"]["block_position_data"]
        self.palette = tuple(map(self._process_palette, nbt["structure"]["palette"]["default"]["block_palette"]))
        self.index = np.arange(0, np.prod(self.size), 1, np.int32).reshape(self.size)

    def iter_block(self) -> tuple[BlockInfo, tuple[int, int, int]]:
        """
        A generator function iterate the block info by z,y,x order
        Some blocks didn't need rendering will be skipped
        """
        xlen, ylen, zlen = self.size
        for x in range(xlen):
            for y in range(ylen):
                for z in range(zlen):
                    pos = (x, y, z)
                    if (block_info := self.get_block(pos)) is None:
                        continue
                    yield (block_info, pos)

    def get_block(self, pos) -> Optional[BlockInfo]:
        """get the block info by given position"""

        block_info = self.palette[self.cube[pos]]
        if block_info is None:
            return None
        block_entity_index = str(self.index[pos])
        if block_entity_index in self.block_entities:
            block_entity = self.block_entities[block_entity_index].get("block_entity_data")
            if block_entity:
                block_info = self._process_block_entity(block_info, block_entity)
        return block_info

    @classmethod
    def _process_palette(cls, block_palette) -> Optional[BlockInfo]:
        rot = None
        lit = False
        data = "0"
        variant = "default"

        blk_name = block_palette["name"].replace("minecraft:", "")
        block_states = block_palette["states"]

        if blk_name == "air":
            return None

        if not block_states:
            return (blk_name, rot, variant, lit, data)

        for key in cls.nbt_def["skip"]:
            if key in block_states and block_states[key]:
                return None

        # variant and lit determine the texture of blocks together
        for key in cls.nbt_def["variant"]:
            if key in block_states:
                variant = nbt_to_str(block_states[key])
                break

        for key in cls.nbt_def["lit"]:
            if key in block_states:
                lit = bool(block_states[key])
                break

        for key in cls.nbt_def["rot"]:
            if key in block_states:
                rot = nbt_to_str(block_states[key])
                break

        # data determines the offset of block together
        for key in cls.nbt_def["data"]:
            if key in block_states:
                data = nbt_to_str(block_states[key])
                break

        for key in cls.nbt_def["top"]:
            if key in block_states and block_states[key]:
                data += "_top"
                break

        # hardcoded exceptions
        if blk_name == "hopper" and rot != 0:
            data = "side"

        return (blk_name, rot, variant, lit, data)

    @classmethod
    def _process_block_entity(cls, block_info, block_entity) -> BlockInfo:
        blk_name, rot, variant, lit, data = block_info

        for key in cls.nbt_def["block_entity_variant"]:
            if key in block_entity:
                variant = nbt_to_str(block_entity[key])
                break

        for key in cls.nbt_def["block_entity_rot"]:
            if key in block_entity:
                rot = nbt_to_str(block_entity[key])
                break

        for key in cls.nbt_def["block_entity_data"]:
            if key in block_entity:
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

        return (blk_name, rot, variant, lit, data)
