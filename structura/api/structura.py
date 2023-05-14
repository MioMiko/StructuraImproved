"""
Main file contains the api to make the structura
"""
from collections import Counter
import json
import logging
import os
from pathlib import Path
import re
from zipfile import ZipFile,ZIP_DEFLATED

from .animation_class import Animation
from .armor_stand_geo_class_2 import Geometry
from .armor_stand_class import Entity
from . import manifest
from .render_controller_class import RenderController, BigModelRenderController
from .structure_reader import StructureProcessor

ROOT = Path(__file__).parent


class Structura:
    """
    Main class to generate structura pack
    """

    __slots__ = ("_lang_name", "_lang", "save_path", "info_save_path",
                 "overwrite_same_packname", "skip_unsupported_block", "logger")

    def __init__(self, *,
                 lang_name: str,
                 save_path: str | Path,
                 info_save_path: str | Path,
                 overwrite_same_packname: bool=False,
                 skip_unsupported_block:bool=True,
                 logger:logging.Logger=logging.getLogger("StructuraImproved")):
        """
        Init Structura with some basic configurations

        Args:

            lang_name (str):
                Language name which will be used to export name tags or material list files
                supported language:
                    en_US
                    zh_CN
                If the language is not supported, it will use en_US instead

            save_path (str | Path):
                The folder path where .mcpack will be stored

            info_save_path (str | Path):
                The info path where name tags and material list files will be stored
                It will creat a folder with the name of the pack
                then store name tags and material list files in it

            overwrite_same_pack (bool):
                If the mcpack file exists, it will raise a FileExistsError

            skip_unsupported_block (bool):
                Whether to skip or raise an exception when a block cannot be processed(for debug)

            logger:
                Set a logger (which is in builtin logging package)
                By default it will be set logging.getLogger("StructuraImproved")

        """
        self._lang_name = None
        self.lang = lang_name
        self.save_path = Path(save_path)
        self.info_save_path = Path(info_save_path)
        self.overwrite_same_packname = overwrite_same_packname
        self.skip_unsupported_block = skip_unsupported_block
        self.logger = logger

    @property
    def lang(self):
        return self._lang_name

    @lang.setter
    def lang(self, lang_name: str):
        if self._lang_name == lang_name:
            return
        try:
            self._lang = json.loads((ROOT / f"res/lang/{lang_name}.json").read_text("utf-8"))
        except FileNotFoundError:
            self._lang = json.loads((ROOT / "res/lang/en_US.json").read_text("utf-8"))
        self._lang_name = lang_name

    @staticmethod
    def draw_packname(file_name: str) -> str:
        """Return the name of .mcstructure file without suffix and mystrcture_ prefix"""
        return re.sub(r"(?:.*[/\\])?(?:mystructure_)?(.*).mcstructure",r"\1",file_name)

    def make_pack(self, pack_name: str,
                      models: dict[str,dict],
                      make_list: bool=False,
                      big_model: bool=False,
                      icon: Path=ROOT / "res/pack_icon.png") -> None:
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

        skip_unsupported_block = self.skip_unsupported_block
        lang = self._lang
        logger = self.logger

        logger.info(lang["start_making_pack"])


        if big_model:
            if len(models) > 13:
                raise ValueError("Too many models for big model mode(Max 13)")

        pack_path = self.save_path / f"{pack_name}.mcpack"
        if not self.overwrite_same_packname and pack_path.exists():
            tmp = pack_name
            i = 1
            pack_name = f"{tmp}({i})"
            while (self.save_path / f"{pack_name}.mcpack").exists():
                i += 1
                pack_name = f"{tmp}({i})"
            pack_path = self.save_path / f"{pack_name}.mcpack"

        multi_model = len(models) > 1

        info_save_path = self.info_save_path / pack_name

        # create info dir and export nametags file

        # check if non-empty model name in models and make a nametag file
        if not big_model and "" not in models or multi_model:
            os.makedirs(info_save_path, exist_ok=True)
            with open(info_save_path / lang["name_tags_filename"],
                      "w", encoding="utf-8") as text_file:
                text_file.write(lang["name_tags_contain"])
                for name in models.keys():
                    text_file.write(f"\n{name}")
        elif make_list:
            os.makedirs(info_save_path, exist_ok=True)

        all_material_list = Counter()

        with ZipFile(pack_path, "w", ZIP_DEFLATED) as zip_file:

            if big_model:
                rc = BigModelRenderController()
            else:
                rc = RenderController()
            entity = Entity()
            animation = Animation(big_model)
            manifest.export(pack_name, zip_file)

            for model_name, model in models.items():

                logger.debug(f"offset of {model_name}: {model['offsets']}")

                rc.add_model(model_name)
                entity.add_model(model_name)
                structure = StructureProcessor(model["structure"])
                geo = Geometry(model_name,model['opacity'],model["offsets"],big_model)

                if not big_model:
                    for y in range(min(structure.size[1], 12)):
                        # creates the layer for controlling.
                        geo.make_layer(y)
                        animation.insert_layer(y)

                # make geometry for each block
                for blk, pos in structure.iter_block():

                    logger.debug(f"{pos}: {blk}")
                    try:
                        geo.make_block(pos, blk, make_list)
                    except Exception as err:
                        logger.warning(lang["unsupported_block"])
                        logger.warning(lang["block_info"].format(*pos, blk[0], blk[2]))
                        if not skip_unsupported_block:
                            raise err

                if make_list:
                    if multi_model:
                        file_name = info_save_path / lang["material_list_filename"].format(model_name)
                        with open(file_name,"w",encoding="utf-8") as file:
                            file.write(f"{lang['block_name']},{lang['count']}\n")
                            for name,count in geo.material_list.most_common():
                                all_material_list[name] += count
                                name = lang["block_name_ref"].get(name,name)
                                file.write(f"{name},{count}\n")
                    else:
                        all_material_list = geo.material_list

                geo.export(zip_file)

            # endfor(models)

            animation.export(zip_file)
            entity.export(zip_file)
            rc.export(zip_file)

            if make_list:
                file_name = info_save_path / lang["all_material_list_filename"]
                with open(file_name,"w",encoding="utf-8") as file:
                    file.write(f"{lang['block_name']},{lang['count']}\n")
                    for name,count in all_material_list.most_common():
                        name = lang["block_name_ref"].get(name,name)
                        file.write(f"{name},{count}\n")

            try:
                zip_file.write(icon, "pack_icon.png")
            except FileNotFoundError as exc:
                raise FileNotFoundError("Icon file not found") from exc

            # A modified armor stand geometry to enlarge the render area of the entity
            zip_file.write(ROOT / "res/vanilla/armor_stand.larger_render.geo.json",
                           "models/entity/armor_stand.larger_render.geo.json")

            # A series of files intended to show the number of the current pose above armor stand
            zip_file.write(ROOT / "res/vanilla/armor_stand.pose_num.geo.json",
                           "models/entity/armor_stand.pose_num.geo.json")
            zip_file.write(ROOT / "res/vanilla/armor_stand.pose_num.render_controllers.json",
            "render_controllers/armor_stand.pose_num.render_controllers.json")
            for i in range(13):
                zip_file.write(ROOT / f"res/uv/others/{i}.png",
                               f"textures/entity/pose_num_{i}.png")

            logger.info(lang["pack_saved"].format(pack_path))

        # end open zip

        models.clear()

        logger.log(25, lang["pack_complete"])
