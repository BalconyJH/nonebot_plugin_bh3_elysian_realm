import io
import zipfile
from nonebot import get_driver

import httpx

config = get_driver().config


async def cache_image_resources(path):
    async with httpx.AsyncClient(proxies=config.proxies) as client:
        # 获取 ZIP 文件
        response = await client.get(config.elysianrealm_image_resoureces)

        if response.status_code == 200:
            zip_data = io.BytesIO(response.content)

            with zipfile.ZipFile(zip_data) as myzip:
                myzip.extractall(path="nonebot_plugin_bh3_elysian_realm/resources/images")

        else:
            print(f"获取失败，状态码：{response.status_code}")
