from pathlib import Path

import nonebot
from pydantic import BaseSettings, Extra

driver = nonebot.get_driver()


# @driver.on_startup
# async def resources_check():
#     from nonebot_plugin_bh3_elysian_realm import elysian_realm
#     await elysian_realm.init()

class Config(BaseSettings, extra=Extra.ignore):
    nickname_path = Path(__file__).parent / "resources" / "nickname.json"
    image_path = Path(__file__).parent / "resources" / "images"


plugin_config = Config.parse_obj(driver.config)
