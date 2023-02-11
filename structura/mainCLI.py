import structura
import re
import traceback

debug = True


class para_count_check:
    def __init__(self,count):
        self.count = count
    def __call__(self,callback):
        def fun(para,*args,**kwards):
            if len(para) < self.count:
                raise Exception(f"Too less parameters, it takes at least {self.count} parameters.")
                return False
            return callback(para,*args,**kwards)
        return fun


@para_count_check(2)
def add_model(para):
    global model
    if para[1] in model.keys():
        raise Exception("Model name must be unique")
        return False
    model[para[1]] = {
        "structure": "",
        "offsets": [0,0,0],
        "opacity": 0.8
    }
    return modify_model(para)

@para_count_check(2)
def modify_model(para):
    global model
    i = 2
    while i < len(para):
        match para[i]:
            case "-s":
                i += 1
                if i >= len(para):
                    raise Exception("-s option takes no parameters.")
                    return False
                model[para[1]]["structure"] = para[i]
            case "-o":
                i += 1
                if i >= len(para):
                    raise Exception("-o option takes no parameters.")
                    return False
                if i + 2 >= len(para):
                    raise Exception("-o option takes too less parameters,need 3.")
                    return False
                model[para[1]]["offsets"] = [int(i) for i in para[i:i+3]]
                i += 2
            case "-a":
                i += 1
                if i >= len(para):
                    raise Exception("-a option takes no parameters.")
                    return False
                try:
                    alpha = int(para[i])
                except ValueError:
                    raise Exception("-a option need a integer from 0 to 100.")
                    return False
                if not 0 <= para[i] <= 100:
                    raise Exception("-a option need a integer from 0 to 100.")
                    return False
                model[para[1]]["structure"] = para[i]
            case _:
                raise Exception(f"Unknown parameter {para[i]}")
        i += 1
    return True

@para_count_check(2)
def del_model(para):
    try:
        model.pop(para[1])
        return True
    except:
        raise Exception("Model doesn't exist.")
        return False

def list_model():
    print(f"Packname:{pack_name},Makelist:{make_list},Icon:{icon}")
    print("%-20s,%-50s,%-16s,%-4s"%("model_name","structure","offsets","opacity"))
    for name,value in sorted(model.items(),key = lambda x:x[0]):
        print("%-20s,%-50s,%-16s,%-.4s"%(name,value["structure"],value["offsets"],value["opacity"]))

def clear_model():
    if "y" == input("Do you really want to clear all models(y/N):").lower():
        model.clear()
    else:
        return

@para_count_check(3)
def set_pack(para):
    global pack_name,make_list
    match para[1].lower():
        case "packname":
            pack_name = para[2]
        case "makelist":
            if para[2].lower() == "false":
                make_list = False
            elif para[2].lower() == "true":
                make_list = True
            else:
                raise Exception(f"Unknown value {para[2]}")
                return False
        case "icon":
            icon = para[2]
        case _:
            raise Exception(f"Unknown setting {para[1]}")
            return False
    return True

@para_count_check(2)
def load_file(para):
    global line
    if para[1] in file_stack:
        raise Exception("Recursive call detected")
    with open(para[1]) as f:
        file_stack.append(para[1])
        i = 0
        while True:
            cmd = f.readline()
            i += 1
            line = i
            if re.search(r"^\s*$",cmd):
                break
            while cmd[-1] == "\\":
                cmd = cmd[:-1] + " "
                cmd += input("> ")
            parse_line(cmd)
    file_stack.pop()

def make_pack():
    global pack_name
    if len(model) == 0:
        raise Exception("Please add model first.")
    multi_model = False
    if len(model) > 1:
        multi_model = True
        if pack_name == "":
            raise Exception("Please set a packname")
    else:
        name = tuple(model.keys())[0]
        if pack_name == "":
            pack_name = re.sub(r"(?:.*[/\\])?(?:mystructure_)?(.+).mcstructure",r"\1",model[name]["structure"])
    for name,value in model.items():
        if value["structure"] == "":
            raise Exception(f'Model "{name}" need a structure file')

    try:
        structura.generate_pack(pack_name,model,multi_model,make_list,icon)
    except Exception as err:
        traceback.print_exc()
        raise Exception(f"Pack make filed")
    else:
        pack_name = ""

def parse_line(line:str) -> bool:
    para = re.findall(r'".*?"|\S+',line)
    para = [i.strip('"') for i in para]
    if debug:
        print(para)
    match para[0].lower():
        case "add":
            add_model(para) 
        case "modify":
            modify_model(para)
        case "del":
            del_model(para)
        case "clear":
            clear_model()
        case "list":
            list_model()
        case "set":
            set_pack(para)
        case "make":
            make_pack()
        case "load":
            load_file(para)
        case "quit":
            quit()
        case _:
            raise Exception(f"Unknown command {para[0]}")

line = 0
file_stack = []
pack_name = ""
make_list = False
icon = "lookups/pack_icon.png"
model = {}
while True:
    cmd = input("> ")
    if re.search(r"^\s*$",cmd):
        continue
    while cmd[-1] == "\\":
        cmd = cmd[:-1] + " "
        cmd += input("> ")
    try:
        parse_line(cmd)
    except Exception as err:
        print(f"\a\033[1;31m{err}\033[0m")
        if file_stack:
            print(f"File Stack: {' > '.join(file_stack)} in line {line}")
            file_stack.clear()
