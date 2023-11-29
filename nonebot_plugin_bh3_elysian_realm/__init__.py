from nonebot import require, get_driver
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

from nonebot_plugin_bh3_elysian_realm.utils import on_startup

require("nonebot_plugin_localstore")
require("nonebot_plugin_saa")

driver = get_driver()

__plugin_meta__ = PluginMetadata(
    name="乐土攻略",
    description="崩坏3乐土攻略",
    type="application",
    usage="""
    [乐土XX] 指定角色乐土攻略
    [乐土更新] 更新乐土攻略
    """.strip(),
    extra={
        "author": "BalconyJH <balconyjh@gmail.com>",
    },
    supported_adapters=inherit_supported_adapters("nonebot_plugin_saa"),
)


@driver.on_startup
async def _():
    """启动前检查"""
    await on_startup()
