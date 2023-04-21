"""
Main file contains the api to make the structura
"""
from collections import Counter
import json
import os
import re
from zipfile import ZipFile,ZIP_DEFLATED

os.chdir(os.path.dirname(__file__))

from animation_class import Animation
from armor_stand_geo_class_2 import Geometry
from armor_stand_class import Entity
import manifest
from render_controller_class import RenderController
from structure_reader import StructureProcessor

skip_unsupported_block = True
debug = False

# load config
with open("config/config.json",encoding="utf-8") as f:
    conf = json.load(f)
with open("config/lang/lang_ref.json",encoding="utf-8") as f:
    lang_ref = json.load(f)
with open(f"config/lang/{lang_ref[conf['lang']]}.json",encoding="utf-8") as f:
    lang = json.load(f)

def draw_packname(file_name: str) -> str:
    return re.sub(r"(?:.*[/\\])?(?:mystructure_)?(.*).mcstructure",r"\1",file_name)

def generate_pack(pack_name: str, models: dict[str,dict], make_list:bool=False,
                  icon:str="lookups/pack_icon.png") -> None:
    """
    This is the funciton that makes a structura pack:

    Args:

        pack_name (str): The name of the pack
            This will be stored the the manafest.json as well as the name of the mcpack file

        models (dict[str, dict]): a dict contains the models info
            Key: name tag of the model
            Value: {
                offsets (tuple[float, float, float]): (x, y, z),
                opacity (float): percent,
                structure (str): .mcstructure file name
            },

        make_list (bool): sets wether a material list shall be output

        icon (str): the icon file path
    """

    print("Start Making Pack.")

    multi_model = len(models) > 1

    info_save_path = os.path.join(conf["info_save_path"],pack_name)

    # create info dir and export nametags file

    # check if non-empty model name in models and make a nametag file
    if "" not in models or multi_model:
        os.makedirs(info_save_path, exist_ok=True)
        with open(f"{info_save_path}/{lang['name_tags_filename']}",
                  "w", encoding="utf-8") as text_file:
            text_file.write(lang["name_tags_contain"])
            for name in models.keys():
                text_file.write(f"\n{name}")
    elif make_list:
        os.makedirs(info_save_path, exist_ok=True)

    all_material_list = Counter()

    pack_path = os.path.join(conf["save_path"],f"{pack_name}.mcpack")
    with ZipFile(pack_path, "w", ZIP_DEFLATED) as zip_file:

        rc = RenderController()
        entity = Entity()
        animation = Animation()
        manifest.export(pack_name, zip_file)

        for model_name,model in models.items():

            if debug:
                print(model['offsets'])

            rc.add_model(model_name)
            entity.add_model(model_name)
            structure = StructureProcessor(model["structure"])
            geo = Geometry(model_name,model['opacity'],model["offsets"])

            for y in range(max(structure.size[1], 12)):
                # creates the layer for controlling. Note there is implied formating here
                geo.make_layer(y)
                animation.insert_layer(y)

            # make geometry for each block
            for blk, pos in structure.iter_block():

                if blk is None:
                    continue

                try:
                    geo.make_block(pos, blk, make_list)
                except Exception as err:
                    print(lang["unsupported_block"])
                    print(lang["block_info"].format(pos, blk[0], blk[2]))
                    if not skip_unsupported_block:
                        raise err

            # endfor(ylen)

            if make_list:
                if multi_model:
                    file_name = f"{info_save_path}/{lang['material_list_filename']}".format(model_name)
                    with open(file_name,"w",encoding="utf-8") as file:
                        file.write(f"{lang['block_name']},{lang['count']}\n")
                        for name,count in geo.material_list.most_common():
                            all_material_list[name] += count
                            name = lang["block_name_ref"].get(name,name)
                            file.write(f"{name},{int(count)}\n")
                else:
                    all_material_list = geo.material_list

            geo.export(zip_file)

        # endfor(models)

        animation.export(zip_file)
        entity.export(zip_file)
        rc.export(zip_file)

        if make_list:
            file_name = f"{info_save_path}/{lang['all_material_list_filename']}"
            with open(file_name,"w",encoding="utf-8") as file:
                file.write(f"{lang['block_name']},{lang['count']}\n")
                for name,count in all_material_list.most_common():
                    name = lang["block_name_ref"].get(name,name)
                    file.write(f"{name},{int(count)}\n")

        try:
            zip_file.write(icon, "pack_icon.png")
        except FileNotFoundError as exc:
            raise FileNotFoundError("Icon file not found") from exc

        # A modified armor stand geometry to enlarge the render area of the entity
        zip_file.write("lookups/vanilla/armor_stand.larger_render.geo.json",
                       "models/entity/armor_stand.larger_render.geo.json")

        # A series of files intended to show the number of the current pose above armor stand
        zip_file.write("lookups/vanilla/armor_stand.pose_num.geo.json",
                       "models/entity/armor_stand.pose_num.geo.json")

        zip_file.write("lookups/vanilla/armor_stand.pose_num.render_controllers.json",
        "render_controllers/armor_stand.pose_num.render_controllers.json")

        for i in range(13):
            zip_file.write(f"lookups/uv/others/{i}.png",
                           f"textures/entity/pose_num_{i}.png")

        print(f"Pack Saved To {pack_path}")

    # end open zip

    models.clear()

    print(f"\033[1;32m{lang['pack_complete']}\033[0m")
