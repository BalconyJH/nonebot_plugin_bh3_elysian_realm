from pathlib import Path

from nonebot import get_driver
from pydantic import Extra, BaseSettings


class Config(BaseSettings, extra=Extra.ignore):
    nickname_path = Path(__file__).parent / "resources" / "nickname.json"
    image_path = Path(__file__).parent / "resources" / "images"
    image_repository = "https://github.com/MskTmi/ElysianRealm-Data"


plugin_config = Config.parse_obj(get_driver().config)
