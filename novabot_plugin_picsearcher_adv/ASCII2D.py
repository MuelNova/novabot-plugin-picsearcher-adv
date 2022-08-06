from typing import List

from PicImageSearch import Ascii2D, Network
from PicImageSearch.model import Ascii2DResponse

from .config import config
from .utils import handle_img, shorten_url


async def ASCII2DSearch(url: str, hide_img: bool) -> List[str]:
    client = Network(proxies=config.proxy)
    ascii2d_color = Ascii2D(client=client)
    ascii2d_bovw = Ascii2D(bovw=True, client=client)
    color_res = await ascii2d_color.search(url)
    if not color_res or not color_res.raw:
        return ["Ascii2D 暂时无法使用"]
    # 针对 QQ 图片链接反盗链做处理
    if color_res.raw[0].hash == "5bb9bec07e71ef10a1a47521d396811d":
        url = f"https://images.weserv.nl/?url={url}"
        color_res = await ascii2d_color.search(url)
        bovw_res = await ascii2d_bovw.search(url)
    else:
        bovw_res = await ascii2d_bovw.search(url)

    async def get_final_res(res: Ascii2DResponse) -> List[str]:
        if not res.raw[0].url:
            res.raw[0] = res.raw[1]
        thumbnail = await handle_img(res.raw[0].thumbnail, hide_img)
        _url = await shorten_url(res.raw[0].url) if res.raw[0] else ""
        res_list = [
            thumbnail,
            res.raw[0].title or "",
            f"作者：{res.raw[0].author}" if res.raw[0].author else "",
            f"来源：{_url}" if _url else "",
            f"搜索页面：{res.url}",
        ]
        return [i for i in res_list if i != ""]

    color_final_res = await get_final_res(color_res)
    bovw_final_res = await get_final_res(bovw_res)
    if color_final_res[:-1] == bovw_final_res[:-1]:
        return ["-- Ascii2D 色合検索&特徴検索 --\n" + "\n".join(color_final_res)]

    return [
        f"-- Ascii2D 色合検索 --\n" + "\n".join(color_final_res),
        f"-- Ascii2D 特徴検索 --\n" + "\n".join(bovw_final_res),
    ]
