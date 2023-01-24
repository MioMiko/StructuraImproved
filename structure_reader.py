import nbtlib
import numpy as np

loaded = {}
class process_structure:
    def __init__(self, file):
        global loaded
        if type(file) is dict:
            self.NBTfile = file
        else:
            self.NBTfile = nbtlib.load(file, byteorder='little')
        loaded=self.NBTfile

        if "" in self.NBTfile.keys():
            self.NBTfile = self.NBTfile[""]

        self.blocks = list(map(int, self.NBTfile["structure"]["block_indices"][0]))
        self.size = list(map(int, self.NBTfile["size"]))
        self.palette = self.NBTfile["structure"]["palette"]["default"]["block_palette"]
        self.block_entities = self.NBTfile["structure"]["palette"]["default"]["block_position_data"]
        self.get_blockmap()

    def get_blockmap(self):
        self.cube = np.zeros((self.size[0],self.size[1],self.size[2],2), int)
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
            if "block_entity_data" in self.block_entities[str(index[1])]:
                block_entity = self.block_entities[str(index[1])]["block_entity_data"]
        return self.palette[int(index[0])],block_entity

    def get_size(self):
        return self.size

    def get_block_list(self, ignored_blocks=[]):
        block_counter = {}
        for block_id in self.blocks:
            if self.palette[block_id]["name"] not in ignored_blocks:
                block_name = self.palette[block_id]["name"]
                if block_name in block_counter.keys():
                    block_counter[block_name] += 1
                else:
                    block_counter[block_name] = 1
        return block_counter


#testFileName="ShulkerSandwich.mcstructure"
#excludedBlocks=["minecraft:structure_block","minecraft:air"]
#test=process_structure(testFileName)
# block_count=test.get_block_list(excludedBlocks)
# for i in block_count.keys():
##    print("{}: {}".format(i,block_count[i]))
# print(test.get_block(10,1,8))
