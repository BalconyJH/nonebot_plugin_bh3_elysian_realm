from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.internal.matcher import Matcher
from nonebot.internal.params import ArgPlainText
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot_plugin_bh3_elysian_realm.nickname_parser import find_key_by_value
from .config import plugin_config
from nonebot_plugin_saa import MessageFactory, Text, Image

__plugin_meta__ = PluginMetadata(
    name="乐土攻略",
    description="乐土攻略",
    type="application",
    usage="""
    [XX乐土] 指定角色乐土攻略
    [乐土更新] 更新乐土攻略
    """.strip(),
    extra={
        "author": "BalconyJH <balconyjh@gmail.com>",
    },
    supported_adapters={
        "~onebot.v11",
        "~onebot.v12",
    },
)

from .resources import find_image

elysian_realm = on_command("乐土攻略", aliases={"乐土", "乐土攻略"}, priority=7)
update_elysian_realm = on_command("乐土更新", aliases={"乐土更新"}, priority=7, permission=SUPERUSER)


@elysian_realm.handle()
async def handle_function(matcher: Matcher, args: Message = CommandArg()):
    if args.extract_plain_text():
        matcher.set_arg("role", args)


@elysian_realm.got("role", prompt="请指定角色")
async def got_introduction(role: str = ArgPlainText()):
    nickname = await find_key_by_value(plugin_config.nickname_path, role)
    if nickname is None:
        msg_builder = MessageFactory(Text("未找到指定角色"))
        await msg_builder.finish()
    else:
        msg_builder = MessageFactory(Image(await find_image(nickname)))
        await msg_builder.finish()
