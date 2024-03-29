# StructuraImproved

简体中文丨[**English**](README)

Structura的灵感来自Litematica模组，它是一个可以用.mcstructure文件生成资源包的工具，这个资源包被称作投影。在这个资源包中，盔甲架模型被修改为被投影的方块，以此投影出“幽灵方块”用于向玩家显示原本方块的位置。

这是一个基于Stuctura做出改进的工具，以期望更好的提供生存模式建造的体验。([原项目地址](https://github.com/RavinMaddHatter/Structura))

## 改动:
- 精细化了部分物品的模型
- 加入了红石显示功能，可以更清晰得看到漏斗侦测器等物品方向
- 更容易辨识的楼梯和半砖
- 更好的材料表输出功能
- 中文支持

## 支持版本
- 1.16.40
- 1.17.30
- 1.18.31
- 1.19.50

以上版本是我测试这个工具的版本，并不意味着这个工具只能在以上版本运行，一旦投影被制作，将在1.16.40以上所有版本通用。

## 安装

首先需要下载源码

然后需要安装Python3.11。</br>
根据你的操作系统选择安装方式:

安卓(Termux):
```bash
pkg install python
```

Arch Linux:
```bash
sudo pacman -S python python-pip
```

接着需要安装一些Python的依赖库:
```bash
pip install -r requirements.txt
```

进入项目根目录并运行StructuraImproved程序:
```bash
python structura
```
如果Tkinter包或桌面环境缺失，命令行工具将会启动(见命令行工具)

## 修改设置

当程序第一次运行时，会在项目根目录生成一个config文件夹，里面记录了程序的设置，更新时注意不要覆盖。

### 语言设置
运行StructuraImproved后，点击右上角的齿轮图标，将弹出的框中将Language改为简体中文，再点击右下角的确认，StructuraImproved会自动关闭，重新启动即可加载配置。

## 生成.mcstructure文件

首先，你必须获得一个结构方块。但它需要在启用作弊的存档中完成，只需在聊天栏输入`/give @s structure_block`即可获得一个结构方块。
![alt text](docs/give_structure.png?raw=true)
接下来使用GUI配置
![alt text](docs/select_structure.PNG?raw=true)
接下来单击底部的导出按钮以生成保存文件。将其命名为您想要的任何名称，而不是位置，稍后您将需要它。
![alt text](docs/export_structure.PNG?raw=true)

## 将结构转换为 .mcpack 文件
启动StructuraImproved。
![alt text](docs/launch_structura.PNG?raw=true)
接下来使用浏览按钮打开之前导出的结构，或手动输入路径。
![alt text](docs/browse_file.PNG?raw=true)
输入生成后资源包的名称。
![alt text](docs/name.PNG?raw=true)
如果你错误地将两个投影包名重复，它会自动为文件名添加一个序号来区分，你可以在设置中改变它，此时它将会直接覆盖原有的投影。

如果一切正常，您现在应该有一个mcpack文件。
![alt text](docs/pack_made.PNG?raw=true)

## 使用资源包
这个包就像任何资源包一样。要使用它，你必须确保它处于激活状态。
![alt text](docs/make_pack_active.PNG?raw=true)
该结构将出现在您加载的世界中的每个盔甲架周围。这就是我们能够使其在任何世界上工作的方式。所以拿出一个盔甲架，把它放下来看看你的结构。
![alt text](docs/example_full.png?raw=true)
潜行右击盔甲架来逐层浏览结构。这将最小化除“活动”层之外的所有层。然而对于大型结构，它一次会显示多层（相隔12个方块）。
![alt text](docs/example_layer.png?raw=true)

## 命令行工具
对于无法使用桌面环境的用户，StructuraImproved提供了一个命令行工具。

使用命令行工具：
```shell
python structura cli
```

如下是一个简单的演示：
```
set makelist true  # 设置制作材料列表
add "" -s "结构文件.mcstructure"  # 添加一个命名为空的模型并指定结构文件
make  # 开始制作投影
```

## 版权声明
所有StructuraImproved的自制贴图均采用[知识共享CC BY 4.0协议](https://creativecommons.org/licenses/by/4.0/)授权。
