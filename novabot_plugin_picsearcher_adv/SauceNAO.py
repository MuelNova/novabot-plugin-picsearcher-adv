import re
from typing import List

from PicImageSearch import SauceNAO, Network

from .ASCII2D import ASCII2DSearch
from .config import config
from .utils import get_source, handle_img, shorten_url


async def SauceNAOSearch(url: str, mode: str, hide_img: bool) -> List[str]:
    saucenao_db = {
        "all": 999,
        "pixiv": 5,
        "danbooru": 9,
    }
    saucenao = SauceNAO(
        client=Network(proxies=config.proxy),
        api_key=config.saucenao_api_key,
        hide=config.saucenao_nsfw_hide_level,
        db=saucenao_db[mode],
    )
    res = await saucenao.search(url)
    final_res = []
    if res and res.raw:
        selected_res = res.raw[0]
        ext_urls = selected_res.origin["data"].get("ext_urls")
        # 如果结果为 pixiv ，尝试找到原始投稿，避免返回盗图者的投稿
        if selected_res.index_id == saucenao_db["pixiv"]:
            pixiv_res_list = list(
                filter(
                    lambda x: x.index_id == saucenao_db["pixiv"]
                              and x.url
                              and abs(x.similarity - selected_res.similarity) < 5,
                    res.raw,
                )
            )
            if len(pixiv_res_list) > 1:
                selected_res = min(
                    pixiv_res_list,
                    key=lambda x: int(re.search(r"\d+", x.url).group()),  # type: ignore
                )
        # 如果地址有多个，优先取 danbooru
        elif ext_urls and len(ext_urls) > 1:
            for i in ext_urls:
                if "danbooru" in i:
                    selected_res.url = i
        _hide_img = hide_img or selected_res.hidden
        thumbnail = await handle_img(selected_res.thumbnail, _hide_img)
        if selected_res.origin["data"].get("source"):
            source = await shorten_url(selected_res.origin["data"]["source"])
        else:
            source = await shorten_url(await get_source(selected_res.url))
        _url = await shorten_url(selected_res.url)
        res_list = [
            f"-- SauceNAO（{selected_res.similarity}%）--",
            thumbnail,
            selected_res.title,
            f"作者：{selected_res.author}" if selected_res.author else "",
            _url,
            f"来源：{source}" if source else "",
        ]
        if res.long_remaining < 10:
            final_res.append(f"⚠️️ SauceNAO 24h 内仅剩 {res.long_remaining} 次使用次数")
        final_res.append("\n".join([i for i in res_list if i != ""]))
        if selected_res.similarity < 60:
            final_res.append(f"相似度 {selected_res.similarity}% 过低，自动使用 Ascii2D 进行搜索")
            final_res.extend(await ASCII2DSearch(url, hide_img))
    else:
        final_res.append("SauceNAO 暂时无法使用，自动使用 Ascii2D 进行搜索")
        final_res.extend(await ASCII2DSearch(url, hide_img))
    return final_res
