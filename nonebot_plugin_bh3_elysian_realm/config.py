from pathlib import Path

from nonebot import get_driver
from pydantic import Extra, BaseSettings


class Config(BaseSettings, extra=Extra.ignore):
    nickname_path = Path(__file__).parent / "resources" / "nickname.json"
    image_path = Path(__file__).parent / "resources" / "images"
    image_repository = "https://github.com/MskTmi/ElysianRealm-Data"
    user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/86.0.4240.111 Safari/537.36")
    cookie = ""


plugin_config = Config.parse_obj(get_driver().config)
