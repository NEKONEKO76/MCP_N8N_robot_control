# 用N8N+MCP的形式控制机械臂

N8N提供了数据流的可视化界面，MCP可以让大语言模型接入大量的第三方工具。本项目要做的是把机械臂的控制API封装，通过MCP协议接入大语言模型。这样就可以用任意大语言模型来控制机械臂了。而且得益于MCP，我们还可以给机械臂加上很多额外的功能(天气查询，新闻搜索等)。N8N的可视化界面也为我们理解MCP的工作流程提供了帮助。但是N8N的这种架构也让LLM和控制API的交互变得有点慢，所以本项目只适用于研究或者纠错阶段(大概)。反正我后续还会继续补充的。

## 环境配置

```python
import os
import json
import sys
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
```

python 3.12.10

## 制作使用MCP协议的第三方工具

这里使用了Anthropic公司提供的FastMCP工具包来制作第三方工具。文件中的Episode_API.py是用于控制机械臂的，因为其是用class的形式来实现的，直接用于制作工具有点麻烦，所以我们将其加工成函数的形式，写在了controller_wrapper.py这个文件中，可以通过调用函数并输入参数的形式直接控制机械臂。



## 在Claude Desktop上运行

在运行前我们需要设置MCP server的路径。在Claude Desktop中点击左上角File, Settings, Developer, Edit config. 

在command中输入我们希望使用的python版本(这里我用的conda创建的虚拟环境所以直接是对应环境文件夹下的python.exe)，arg中输入我们server.py所在的位置

```json
{
    "mcpServers": {
        "WeatherAndSearchAPI": {
            "command": "X:\\Anaconda\\envs\\MCP\\python.exe",
            "args": ["C:\\Users\\tt186\\Desktop\\armrobot\\N8N_MCP_CONTROL_ROBOT\\server.py"]
        }
    }
}
```

设置完成后保存，重启Claude。

然后再Claude中即可通过对话的形式来控制机械臂了，目前能做到的行为有打开夹爪，关闭夹爪，汇报当前坐标，移动末端执行器到指定位置，天气问答和新闻搜索。

## 机械臂控制的前置工作

我们使用的是恩培计算机视觉出的一款众筹机器人，整体价格在2000元以内，且可以实现一些精准度要求较高的任务，在学习领域是一款性价比比较高的机器人。(但是所用的行星减速器背隙还是较大的，但是我目前使用起来，由于重力的原因，背隙的影响没有那么大，如果任务对精准度要求较高可以选择ur5或者性价比较高的dummy机械臂，或者其他谐波减速器的机械臂，精准度会有显著的提升。)



启动本任务时还需要先启动配套的上位机软件，将USB to CAN 模块的开关拨到120R模式。然后在上位机中先执行归零操作。具体原理是每个关节都有个限位器，撞到限位器后电机电流激增，当电流超过设定数值后，我们即认为电机撞上了限位器，然后就会记录这个位置为0点。（如果不进行归零操作会损坏机械臂）

## N8N

N8N就是可以看到数据流的一个玩意儿，做可视化的，之前好像更多的是借助AI完成一些office的自动化任务。实现本次任务我借助的是如下的教程，很完整。仿照他搭建一个类似构造的东西即可。

[AI工作流+MCP：零代码打造最强AI Agent，一键接入海量工具 | N8N+MCP实战教程！](https://www.youtube.com/watch?v=c2Ecz0tI7IU)

然后我们在MCPagent中的配置使用STDIO

然后cmmande选择我们的所需环境 比如 `X:\Anaconda\envs\MCP\python.exe`

在arg中，我们填入server.py所在的文件夹路径，比如`C:\Users\tt186\Desktop\armrobot\N8N_MCP_CONTROL_ROBOT\server.py`

最后我们即可在N8N 中利用LLM控制机械臂了(MCP协议)得益于N8N的可视化，我们可以清楚的看到MCP的工作原理，还是挺有意思的一个项目。

另外N8N的文档的连接如下所示，

[nerding-io/n8n-nodes-mcp: n8n custom node for MCP](https://github.com/nerding-io/n8n-nodes-mcp)  MCP的官方文档

[modelcontextprotocol/servers: Model Context Protocol Servers](https://github.com/modelcontextprotocol/servers) MCP开源的一些第三方服务，给LLM加功能用的。

## PS

在.env环境中，我们需要填写用于查找天气和搜索新闻的API，这里我删掉了，自己去官网免费申请即可。





