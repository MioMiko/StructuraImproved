"""
cli tool for StructiraImroved
class Cli(cmd.Cmd): Create a object of it to run the tool
"""

from cmd import Cmd
from pathlib import Path
import shlex
import sys
from traceback import print_exc

from api import Structura
from config import config

ROOT = Path(__file__).parent.resolve()

conf, lang = config.conf, config.lang
structura = Structura(lang_name=config.std_lang_name,
                      save_path=ROOT / conf["save_path"],
                      info_save_path=ROOT / conf["info_save_path"],
                      overwrite_same_packname=conf["overwrite_same_packname"])

class Para_Parser:
    """slpit the parameters and check the counts of it"""

    def __init__(self,count=0):
        self.count = count
    def __call__(self,callback):
        if self.count == -1:
            return lambda this, _, *args ,**kwards: callback(this, *args, **kwards)

        def fun(this,para,*args,**kwards):
            para = shlex.split(para,comments=True)
            if len(para) < self.count:
                raise Exception(f"Too less parameters, it takes at least {self.count} parameters.")
            return callback(this,para,*args,**kwards)
        return fun


class Cli(Cmd):

    intro = "Welcome to use StructuraImproved.Type *help* to list commands."
    prompt = "> "

    def __init__(self, *args, **kwards):
        self.models = {}
        self.pack_name = ""
        self.make_list = False
        self.big_model = False
        self.icon = conf["icon_path"]
        self.line = 0
        self.file_stack = []
        super().__init__(*args,**kwards)

    def emptyline(self):
        pass

    def precmd(self, line):
        if line == "EOF":
            sys.exit()
        return line

    def onecmd(self,line):
        try:
            return super().onecmd(line)
        except Exception as err:
            print(f"\a\033[1;31m{err}\033[0m")
            if self.file_stack:
                print(f"File Stack: {' > '.join(self.file_stack)} in line {self.line}")
                self.file_stack.clear()
            return False

    def default(self,line):
        raise Exception(f"Unknown command *{line.split(' ')[0]}*.")

    @Para_Parser(-1)
    def do_quit(self):
        return True

    def modify_model(self, para):
        if para[0] not in self.models:
            raise KeyError(f"No such model *{para[0]}*")
        i = 1
        while i < len(para):
            match para[i]:
                case "-s":
                    i += 1
                    if i >= len(para):
                        raise Exception("-s option takes no parameters.")
                    self.models[para[0]]["structure"] = para[i]
                case "-o":
                    i += 1
                    if i >= len(para):
                        raise Exception("-o option takes no parameters.")
                    if i + 2 >= len(para):
                        raise Exception("-o option takes too less parameters,need 3.")
                    self.models[para[0]]["offsets"] = [int(i) for i in para[i:i+3]]
                    i += 2
                case "-a":
                    i += 1
                    if i >= len(para):
                        raise Exception("-a option takes no parameters.")
                    try:
                        alpha = int(para[i])
                    except ValueError:
                        raise ValueError("-a option need a integer from 0 to 100.")
                    if not 0 <= alpha <= 100:
                        raise ValueError("-a option need a integer from 0 to 100.")
                    self.models[para[0]]["opacity"] = (100 - para[i]) / 100
                case option:
                    raise Exception(f"Unknown parameter *{option}*")
            i += 1

    @Para_Parser(1)
    def do_add(self,para):
        if para[0] in self.models:
            raise Exception("Model name must be unique")
        self.models[para[0]] = {
            "structure": "",
            "offsets": [0,0,0],
            "opacity": 0.8
        }
        self.modify_model(para)

    @Para_Parser(1)
    def do_modify(self,para):
        self.modify_model(para)

    @Para_Parser(1)
    def do_del(self,para):
        fail_model = []
        for name in para:
            try:
                self.models.pop(name)
            except KeyError:
                fail_model.append(name)
        if fail_model:
            raise Exception(f"Model *{','.join(fail_model)}* doesn't exist.")

    @Para_Parser(-1)
    def do_list(self):
        print(f"Packname:{self.pack_name},Makelist:{self.make_list},Icon:{self.icon}")
        print("%-20s,%-50s,%-16s,%-4s"%("model_name","structure","offsets","opacity"))
        for name,value in sorted(self.models.items()):
            print("%-20s,%-50s,%-16s,%-.4s"%(name,value["structure"],value["offsets"],value["opacity"]))

    @Para_Parser(-1)
    def do_clear(self):
        if "y" == input("Do you really want to clear all models(y/N):").lower():
            self.models.clear()

    @staticmethod
    def parse_bool(s:str) -> bool:
        if s.lower() == "false":
            return False
        if s.lower() == "true":
            return True
        raise ValueError(f"Unknown value {s}")

    @Para_Parser(2)
    def do_set(self, para):
        match para[0].lower():
            case "packname":
                self.pack_name = para[1]
            case "makelist":
                self.make_list = self.parse_bool(para[1])
            case "icon":
                self.icon = para[1]
            case "bigmodel":
                self.big_model = self.parse_bool(para[1])
            case _:
                raise Exception(f"Unknown setting {para[0]}")

    @Para_Parser(1)
    def do_load(self, para):
        if para[0] in self.file_stack:
            raise RuntimeError("Recursive call detected")
        with open(para[0]) as f:
            self.file_stack.append(para[0])
            i = 0
            while True:
                if not (cmd := f.readline()):
                    break
                i += 1
                self.line = i
                super().onecmd(cmd) # won't catch exception
        self.file_stack.pop()

    @Para_Parser(-1)
    def do_make(self):
        if len(self.models) == 0:
            raise Exception("Please add model first.")
        if len(self.models) > 1:
            if self.pack_name == "":
                raise Exception("Please set a packname")
        else:
            if self.pack_name == "":
                name = next(iter(self.models))
                self.pack_name = Structura.draw_packname(self.models[name]["structure"])
        for name, value in self.models.items():
            if value["structure"] == "":
                raise Exception(f'Model "{name}" need a structure file')

        try:
            structura.make_pack(self.pack_name, self.models,
                                self.make_list, self.big_model,
                                ROOT / self.icon)
        except Exception as exc:
            print_exc()
            raise RuntimeError(f"Pack make failed: {exc}") from exc

        self.pack_name = ""


    @Para_Parser(0)
    def do_help(self,arg):
        if len(arg) == 0:
            print(lang["help_summary"])
        for command in arg:
            print(lang.get(f"help_{command}",f"Unknown command *{command}*"))

def main():
    try:
        Cli().cmdloop()
    except KeyboardInterrupt:
        sys.exit()

if __name__ == "__main__":
    main()
