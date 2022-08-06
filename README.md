<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>



<div align="center">



# novabot-plugin-picsearcher-adv

_✨ picsearcher，但是魔改了 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/Nova-Noir/novabot-plugin-picsearcher-adv.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/novabot-plugin-picsearcher-adv">
    <img src="https://img.shields.io/pypi/v/novabot-plugin-picsearcher-adv.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">

</div>

## 📖 介绍

魔改自 [YetAnotherPicSearch](https://github.com/NekoAria/YetAnotherPicSearch)，用法相同~~（毕竟基本是 Copy 的）~~

更改了部分逻辑，不再支持多图搜索，不再拥有合并转发功能

## 💿 安装

<details>
<summary>使用 nb-cli 安装</summary>
在 Nova-Bot 的根目录下打开命令行, 输入以下指令即可安装



```sh
nb plugin install novabot-plugin-picsearcher-adv
```

</details>

<details>
<summary>使用包管理器安装</summary>
在 Nova-Bot 的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令



<details>
<summary>pip</summary>



```sh
pip install novabot-plugin-picsearcher-adv
```

</details>

<details>
<summary>pdm</summary>



```sh
pdm add novabot-plugin-picsearcher-adv
```

</details>

<details>
<summary>poetry</summary>



```sh
poetry add novabot-plugin-picsearcher-adv
```

</details>

<details>
<summary>conda</summary>



```sh
conda install novabot-plugin-picsearcher-adv
```

</details>

打开 Nova-Bot 的 `bot.py` 文件, 在其中写入

```python
nonebot.load_plugin('novabot_plugin_word-bank')
```

</details>

<details>
<summary>从 github 安装</summary>
在 Nova-Bot 项目的插件目录下, 打开命令行, 输入以下命令克隆此储存库




```sh
git clone https://github.com/Nova-Noir/novabot-plugin-picsearcher-adv.git
```

打开 Nova-Bot 项目的 `bot.py` 文件, 在其中写入

```python
nonebot.load_plugin('path.to.novabot.novabot-plugin-picsearcher-adv.novabot_plugin_picsearcher_adv')
```

> 在默认情况下，它应该是
>
> ```python
> nonebot.load_plugin('novabot.plugins.novabot-plugin-picsearcher-adv.novabot_plugin_picsearcher_adv')
> ```
>
> 

</details>

## ⚙️ 配置

|      配置项      | 必填 | 默认值 |                          说明                          |
| :--------------: | :--: | :----: | :----------------------------------------------------: |
| SAUCENAO_API_KEY |  否  |   无   | [SauceNAO](https://saucenao.com/) 搜图使用的 `API_KEY` |
|      PROXY       |  否  |   无   |                          代理                          |

## 🎉 使用

### 指令表

|    指令    |  权限  | 需要@ |    范围    |     说明     |
| :--------: | :----: | :---: | :--------: | :----------: |
|   `搜图`   | 所有人 |  否   | 群聊、私聊 | 打开搜图模式 |
| *回复图片* | 所有人 |  是   | 群聊、私聊 |   回复搜图   |

在两个指令的使用中，都可以在消息正文中添加对应的参数来客制化搜图

| 搜图模式（每条消息仅可指定一种） | 说明                                 |
| -------------------------------- | ------------------------------------ |
| `--all`                          | 默认，使用 `SauceNAO` 全部数据库搜索 |
| `--pixiv`                        | 使用 `SauceNAO` pixiv 数据库搜索     |
| `--danbooru`                     | 使用 `SauceNAO` danbooru 数据库搜索  |
| `--doujin`                       | 使用 `Soutubot` NHentai 数据库搜索   |
| `--anime`                        | 使用 `TraceMoe` 数据库搜索           |
| `--a2d`                          | 使用 `ASCII2D` 数据库搜索            |
| `--iqdb`                         | 使用 `iqdb` 数据库搜索               |

| 搜图参数        | 说明             |
| --------------- | ---------------- |
| `-p`, `--purge` | 不使用缓存搜索   |
| `-h`, `--hide`  | 搜图结果隐藏图片 |

> 可能的例子：
>
> ​	`搜图 --anime -h`
>
> ​	`搜图 --pixiv -p -h`
>
> ​	`[回复图片] @bot --doujin`


