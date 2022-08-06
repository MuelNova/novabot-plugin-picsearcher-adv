"""
更加先进的 搜图 插件, 多数据库来源, 包含缓存, 更多可控参数

Default order of image searching:
    - SauceNAO
    -- ASCII2D ( NO API_KEY / API_KEY Limited / Accuracy < 60 )

USAGE: - `搜图 [Optional Search Arg] %IMG%`: 通过发送`搜图`, `可选参数` 以及 `图片` 来搜图
       - `[reply, message=%IMG%] @bot [Optional Search Arg]`: 通过回复带有 `图片` 的消息并带上 `@bot` 以及 `可选参数` 来搜图

Optional Search Arg:
    Mode:
        - `all`: (default) SauceNAO - all database
        - `pixiv`: SauceNAO - pixiv database
        - `danbooru`: SauceNAO - danbooru database
        - `doujin`: Soutubot
        - `anime`: TraceMoe
        - `a2d`: ASCII2D
        - `iqdb`: iqdb
    Option:
        - `p`, `purge`: search without cache
        - `h`, `hide`: hide the result image
"""
import re
from typing import Tuple, List

from nonebot.adapters.onebot.v11 import (
    Message,
    MessageEvent,
    MessageSegment,
    Bot,
    PrivateMessageEvent,
    GroupMessageEvent
)
from nonebot.params import CommandArg
from nonebot.typing import T_State

from novabot import on_message, on_command
from .ASCII2D import ASCII2DSearch
from .SauceNAO import SauceNAOSearch
from .Soutubot import SoutubotSearch
from .TraceMoe import TraceMoeSearch
from .cache import Cache, exist_in_cache, upsert_cache
from .iqdb import iqdbSearch
from .utils import REPLY_SEARCH_RULE, extract_first_img_url

reply_img_searcher = on_message("回复搜图", rule=REPLY_SEARCH_RULE, invisible=True, cd=10, priority=3)
img_searcher = on_command("搜图", aliases={("识图", "查图", "图片搜索")}, priority=2, cd=10)


def arg_parser(args: str) -> Tuple[str, bool, bool]:
    mode_args = ["pixiv", "danbooru", "doujin", "anime", "a2d", "iqdb"]
    mode = next((i for i in mode_args if f'--{i}' in args), 'all')
    purge = '--purge' in args or '-p' in args
    hide_img = '--hide' in args or '-h' in args
    return mode, purge, hide_img


@img_searcher.handle()
async def _(state: T_State, event: MessageEvent, args: Message = CommandArg()):
    state['args'] = arg_parser(args.extract_plain_text())
    if img := extract_first_img_url(event):
        state['img'] = img


@reply_img_searcher.handle()
@img_searcher.got("img", prompt="你想要查找哪张图片呢?")
async def _(state: T_State, event: MessageEvent, bot: Bot):
    if 'args' not in state:
        state['args'] = arg_parser(event.message.extract_plain_text())
    img = extract_first_img_url(event)

    results = await img_search(img, *state['args'])
    for message in results:
        message = f"{MessageSegment.reply(id_=event.message_id)}{message}"
        await bot.send_msg(
            user_id=event.user_id if isinstance(event, PrivateMessageEvent) else 0,
            group_id=event.group_id if isinstance(event, GroupMessageEvent) else 0,
            message=message,
        )


async def img_search(
        url: str,
        mode: str = 'all',
        purge: bool = False,
        hide_img: bool = False
) -> List[str]:
    md5 = re.search(r'[A-F\d]{32}', url)
    if not md5:
        raise ValueError("URL is not a valid link from `qpic.cn` !")
    _cache = Cache("data/novabot-plugin-imgsearch")
    if not purge and (result := exist_in_cache(_cache, f"{md5[0]}_{mode}")):
        return [f"** [Cache] **\n{i}" for i in result]

    if mode == 'a2d':
        results = await ASCII2DSearch(url, hide_img)
    elif mode == 'anime':
        results = await TraceMoeSearch(url, hide_img)
    elif mode == 'doujin':
        results = await SoutubotSearch(url, hide_img)
    elif mode == 'iqdb':
        results = await iqdbSearch(url, hide_img)
    else:
        results = await SauceNAOSearch(url, mode, hide_img)
    upsert_cache(_cache, f"{md5[0]}_{mode}", results)
    return results
