from typing import Optional

from nonebot import get_driver
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    cache_expire: int = 7  # Day(s)
    proxy: Optional[str] = None
    hide_img_when_tracemoe_r18: bool = True
    saucenao_api_key: Optional[str] = None
    saucenao_nsfw_hide_level: int = 0


config = Config.parse_obj(get_driver().config)
