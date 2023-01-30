# StructuraImproved

简体中文丨[**English**](README)

Structura的灵感来自Litematica模组。它是一个可以用.mcstructure文件生成资源包的工具，这个资源包被称作投影。在这个资源包中，盔甲架模型被修改为被投影的方块。它会把结构文件中的所有方块作为模型中的骨骼。然后投影出“幽灵块”用于向玩家显示原本方块的位置。

这是一个基于Stuctura做出改进的工具，以期望更好的提供生存模式建造的体验，目前这个项目只支持1.16.40（这并不代表其他版本完全无法使用），一旦投影被制作出来，将在1.16以上所有版本通用。

改动:
- 抛弃原有通过官方文件terrain_texture.json和blocks.json查找方块贴图的方式，并使用lookups/block_ref.json替代
- 精细化了部分物品的模型
- 加入了红石显示功能，可以更清晰得看到漏斗侦测器等物品方向
- 中文支持

## 安装

首先需要下载源码

然后需要安装Python3.10-tk。</br>
根据你的操作系统选择安装方式:

Arch Linux:
```bash
sudo pacman -S python
```

接着你需要安装一些Python的依赖库:
```bash
pip install -r requirements.txt
```

运行StructuraImproved程序:
```bash
python structura.py
```
## 修改设置

### 语言设置
运行StructuraImproved后，点击右上角的齿轮图标，将弹出的框中将Language改为简体中文，再点击右下角的确认，StructuraImproved会自动关闭，重新启动即可加载配置。

其他的设置也应当被修改，因为可以在我设备上运行的设置并不能在所有人的设备上运行。

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
如果你错误地将两个文件名重复，它会直接覆盖原有的包，但是你可以在设置中改变它，此时它会自动为文件名添加一个序号来区分。

如果一切正常，您现在应该有一个mcpack文件。
![alt text](docs/pack_made.PNG?raw=true)

## 使用资源包
这个包就像任何资源包一样。要使用它，你必须确保它处于激活状态，以便在全局资源中启用它。
![alt text](docs/make_pack_active.PNG?raw=true)
该结构将出现在您加载的世界中的每个盔甲架周围。这就是我们能够使其在任何世界上工作的方式。所以拿出一个盔甲架，把它放下来看看你的结构。
![alt text](docs/example_full.png?raw=true)
你可以通过右击盔甲架来逐层浏览结构。这将最小化除“活动”层之外的所有层。然而对于大型结构，它一次会显示多层（相隔12个方块）
![alt text](docs/example_layer.png?raw=true)

## 目前企划
- 更容易辨识的楼梯和半砖
- 小瑕疵修复
