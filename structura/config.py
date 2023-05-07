import json
from pathlib import Path

ROOT = Path(__file__).parent.resolve()


class _Config():

    __slots__=("conf", "std_lang_name", "lang", "_lang_ref")

    conf_path = ROOT / "config/config.json"

    def __init__(self):
        version = "1.0.0"
        default_conf = {
            "version": version,
            "lang": "English",
            "save_path": "../mcpacks",
            "info_save_path": "../packinfos",
            "icon_path": "api/res/pack_icon.png",
            "default_structure_path": ".",
            "overwrite_same_packname": False,
        }
        try:
            self.conf = conf = json.loads((self.conf_path).read_text("utf-8"))
        except FileNotFoundError:
            self.conf = conf = default_conf
            self.conf_path.write_text(json.dumps(conf), encoding="utf-8")

        if "version" not in conf:
            conf["version"] = "0.0.0"
        if self._Version(conf["version"]) < self._Version(version):
            keys = default_conf.keys() - conf.keys()
            if keys:
                for k in keys:
                    conf[k] = default_conf[k]
                for k in conf.keys() - default_conf.keys():
                    del conf[k]
            conf["version"] = default_conf["version"]
            self.save()

        self._lang_ref = json.loads((ROOT /
                "config/lang/lang_ref.json").read_text("utf-8"))
        try:
            self.std_lang_name = self._lang_ref[self.conf["lang"]]
        except KeyError:
            self.std_lang_name = "en-US"
        self.lang = json.loads((ROOT /
            f"config/lang/{self.std_lang_name}.json").read_text("utf-8"))

    def save(self):
        """Save configuration"""
        self.conf_path.write_text(json.dumps(self.conf), encoding="utf-8")

    class _Version(object):

        __slots__ = ("_version",)

        VERSION_LEN = 3

        def __init__(self, version:str):
            try:
                self._version = tuple(map(int, version.split(".")))
            except ValueError as exc:
                raise ValueError("Uncorrect version formar") from exc
            if len(self._version) != self.VERSION_LEN:
                raise ValueError("Uncorrect version formar")

        def __eq__(self, obj):
            return self._version == obj._version

        def __lt__(self, obj):
            for i in range(self.VERSION_LEN):
                if self._version[i] != obj._version[i]:
                    return self._version[i] < obj._version[i]
            return False

        def __le__(self, obj):
            return self < obj or self == obj

        def __str__(self):
            return ".".join(map(str,self._version))

        def __repr__(self):
            return f"Version({str(self)})"

config = _Config()
