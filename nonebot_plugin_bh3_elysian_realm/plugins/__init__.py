from pathlib import Path

from nonebot import on_command
import nonebot_plugin_saa as saa
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.internal.params import ArgPlainText

from nonebot_plugin_bh3_elysian_realm.config import plugin_config
from nonebot_plugin_bh3_elysian_realm.utils import git_pull, load_json, find_key_by_value

elysian_realm = on_command("乐土攻略", aliases={"乐土", "乐土攻略"}, priority=7)
update_elysian_realm = on_command("乐土更新", aliases={"乐土更新"}, priority=7, permission=SUPERUSER)
add_nickname = on_command("添加乐土昵称", aliases={"添加乐土昵称"}, priority=7, permission=SUPERUSER)


@elysian_realm.handle()
async def handle_first_receive(matcher: Matcher, args: Message = CommandArg()):
    if args.extract_plain_text():
        matcher.set_arg("role", args)


@elysian_realm.got("role", prompt="请指定角色")
async def got_introduction(nickname: str = ArgPlainText()):
    role = await find_key_by_value(load_json(plugin_config.nickname_path), nickname)
    if role is None:
        msg_builder = saa.Text("未找到指定角色")
        await msg_builder.send()
        await elysian_realm.finish()
    else:
        msg_builder = saa.Image(
            Path(plugin_config.image_path / f"{role}.jpg")
        )
        await msg_builder.finish()


@update_elysian_realm.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    result = await git_pull()
    if result is not None:
        msg_builder = saa.Text(result)
        await msg_builder.finish()
    else:
        await update_elysian_realm.finish("更新成功")
