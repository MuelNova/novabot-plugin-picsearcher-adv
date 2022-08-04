from typing import Optional
from pydantic import BaseModel, Extra
from nonebot import get_driver


class Config(BaseModel, extra=Extra.ignore):
    cache_expire: int = 7  # Day(s)
    proxy: Optional[str] = None
    hide_img_when_tracemoe_r18: bool = True
    SauceNAO_API_KEY: Optional[str] = None
    SauceNAO_nsfw_hide_level: int = 0


config = Config(**get_driver().config.dict())
