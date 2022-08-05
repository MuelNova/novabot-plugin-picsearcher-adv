import asyncio
from dataclasses import dataclass
from typing import Optional, AnyStr, List, Tuple

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
from nonebot import require
from nonebot.log import logger
from nonebot_plugin_apscheduler import scheduler
from playwright._impl._api_structures import FilePayload
from playwright._impl._api_types import TimeoutError
from playwright.async_api import Page, Browser

from novabot.core import get_firefox_browser
from .utils import handle_img

require("nonebot_plugin_apscheduler")

browser: Optional[Browser] = None
page: Optional[Page] = None


@dataclass
class SoutuBotResult:
    thumbnail: str
    language: str
    urls: List[str]
    fullname: str
    accuracy: float


@scheduler.scheduled_job('cron', minute="0/5", second='0')
async def get_soutubot_page() -> bool:
    global page
    global browser
    if page and await is_soutubot_available():
        return True
    if not browser:
        browser = await get_firefox_browser()
    logger.debug("Trying to get Page from `soutubot.moe`...")
    js = "Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"
    context = await browser.new_context()
    await context.add_init_script(js)
    new_page = await context.new_page()
    await new_page.goto("https://soutubot.moe")
    cf_clearance = ""
    for _ in range(300):
        if cf_cookies := filter(lambda x: x.get('name') == 'cf_clearance', await context.cookies()):
            try:
                cf_clearance = next(cf_cookies)
                break
            except StopIteration:
                pass
        await asyncio.sleep(0.1)
    if not cf_clearance:
        await new_page.close()
        logger.debug("Failed to get the Page from `soutubot.moe`...")
        return False
    page = new_page
    logger.debug(cf_clearance)
    logger.debug("Get Page from `soutubot.moe` success!")
    return True


async def is_soutubot_available(timeout: int = 3000) -> bool:
    if not page:
        return False
    try:
        logger.debug("Checking availability for `Soutubot.moe`...")
        await page.wait_for_selector("text=NH全部语言搜索", timeout=timeout)
    except TimeoutError:
        return False
    logger.debug("Checking availability for `Soutubot.moe` success!")
    return True


async def soutubot_from_url(url: str, nums: Optional[int] = None) -> Tuple[str, Optional[List[SoutuBotResult]]]:
    r = requests.get(url)
    if r.status_code != 200:
        return "Error Image Url Found!", None
    content = r.content
    if content.startswith(b"\xff\xd8\xff"):
        file = FilePayload(name="img.jpg", mimeType="image/jpeg", buffer=content)
    elif content.startswith(b"\x89\x50\x4E\x47"):
        file = FilePayload(name="img.png", mimeType="image/png", buffer=content)
    else:
        return "Invalid Image Found!", None
    if not await is_soutubot_available():
        await get_soutubot_page()
    if await is_soutubot_available():
        try:
            await page.wait_for_selector("text=NH全部语言搜索", timeout=45000)
            async with page.expect_file_chooser() as fc:
                await page.click(".inputBox")
                file_chooser = await fc.value
                await file_chooser.set_files(file)
            await page.click("text=NH全部语言搜索")
            await page.wait_for_url(r"https://soutubot.moe/html/*")
            results = parse(await page.content(), nums)
            reesult_url = page.url
            await page.goto("https://soutubot.moe")
            return reesult_url, results
        except TimeoutError:
            return "Timeout Happened! Try Later!", None
    else:
        return "Page is not ready!", None


def parse(html: AnyStr, nums: Optional[int] = None) -> Optional[List[SoutuBotResult]]:
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find_all("tr")

    results = []

    if len(tables) < 2:
        return None
    if not nums or nums >= len(tables):
        nums = len(tables)
    else:
        nums += 1
    for i in tables[1:nums]:
        img = i.find_next("img")
        thumbnail = img.attrs.get('src')
        accuracy = float(str(img.find_next("td").string))
        if accuracy < 40:  # basically that won't be right.
            break
        names_tag = img.find_next("td").find_next("td")
        language = str(names_tag.next_element)[:2] if isinstance(names_tag.next_element, NavigableString) else 'Unknown'
        urls = list(map(lambda x: x.attrs.get('href'),
                        filter(lambda x: isinstance(x, Tag) and x.name == 'a',
                               names_tag.contents)))
        fullname = names_tag.text.replace("via soutubot.moe", " - via soutubot.moe")
        results.append(SoutuBotResult(thumbnail, language, urls, fullname, accuracy))
    return results


async def SoutubotSearch(url: str, hide_img: bool = False) -> List[str]:
    url, results = await soutubot_from_url(url, 1)
    if not results:
        return [f"使用 Soutubot 时发生错误:\n{url}"]
    message = f"-- Soutubot({results[0].accuracy}%) --\n"
    message += await handle_img(results[0].thumbnail, hide_img)
    message += f"{results[0].fullname}\n" \
               f"url(s):\n\n" \
               + "\n".join(results[0].urls) \
               + f"\n\nFull Result: {url}"
    return [message]
