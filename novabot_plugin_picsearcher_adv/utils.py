import base64
import re
from typing import Optional

import aiohttp
from nonebot.adapters.onebot.v11 import MessageEvent, Bot
from nonebot.rule import Rule
from pyquery import PyQuery
from yarl import URL

from .config import config


async def _is_reply(event: MessageEvent) -> bool:
    return bool(event.reply)


async def _has_event_img(event: MessageEvent) -> bool:
    return bool([i for i in event.reply.message if i.type == 'image']) if event.reply \
        else bool([i for i in event.message if i.type == 'image'])


async def _is_at_bot(bot: Bot, event: MessageEvent) -> bool:
    return bool([i for i in event.original_message if i.type == "at" and i.data["qq"] == bot.self_id])


def extract_first_img_url(event: MessageEvent) -> Optional[str]:
    return next(map(lambda x: x.data['url'], filter(lambda x: x.type == 'image', list(event.reply.message))), None) \
        if event.reply else \
        next(map(lambda x: x.data['url'], filter(lambda x: x.type == 'image', list(event.message))), None)


async def handle_img(
        url: str,
        hide_img: bool,
        cookies: Optional[str] = None,
) -> str:
    if not hide_img:
        if img_base64 := await get_pic_base64_by_url(url, cookies):
            return f"[CQ:image,file=base64://{img_base64}]"
    return f"预览图链接：{url}"


async def get_pic_base64_by_url(url: str, cookies: Optional[str] = None) -> str:
    headers = {"Cookie": cookies} if cookies else None
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url, proxy=config.proxy) as resp:
            if resp.status == 200:
                return base64.b64encode(await resp.read()).decode()
    return ""


async def shorten_url(url: str) -> str:
    pid_search = re.compile(
        r"(?:pixiv.+(?:illust_id=|artworks/)|/img-original/img/(?:\d+/){6})(\d+)"
    )
    if pid_search.search(url):
        return f"https://pixiv.net/i/{pid_search.search(url)[1]}"  # type: ignore
    if URL(url).host == "danbooru.donmai.us":
        return url.replace("/post/show/", "/posts/")
    return url


async def get_source(url: str) -> str:
    source = ""
    async with aiohttp.ClientSession() as session:
        if URL(url).host in ["danbooru.donmai.us", "gelbooru.com"]:
            async with session.get(url, proxy=config.proxy) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    source = PyQuery(html)(".image-container").attr(
                        "data-normalized-source"
                    )
        elif URL(url).host in ["yande.re", "konachan.com"]:
            async with session.get(url, proxy=config.proxy) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    source = PyQuery(html)("#post_source").attr("value")
    return source


REPLY_SEARCH_RULE = Rule(_is_reply) & _has_event_img & _is_at_bot
