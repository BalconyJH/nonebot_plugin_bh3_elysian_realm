import pytest
from nonebug import App
from nonebot import get_driver
from pytest_mock import MockerFixture
from nonebug_saa import should_send_saa
from nonebot_plugin_saa import MessageFactory
from nonebot.adapters.onebot.v11 import Bot as OBV11Bot
from nonebot.adapters.onebot.v11 import Message as OBV11Message

from tests.utils import fake_group_message_event_v11


@pytest.mark.asyncio
async def test_update_elysian_realm(app: App, mocker: MockerFixture):
    from nonebot_plugin_bh3_elysian_realm.plugins import update_elysian_realm

    mocker.patch.object(get_driver().config, "superusers", {"10"})

    async with app.test_matcher(update_elysian_realm) as ctx:
        v11bot = ctx.create_bot(base=OBV11Bot)
        v11event = fake_group_message_event_v11(message=OBV11Message("/乐土更新"), sender={"role": "owner"})

        ctx.receive_event(v11bot, v11event)
        ctx.should_call_send(v11event, "更新成功")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_none_nickname(app: App):
    from nonebot_plugin_bh3_elysian_realm.plugins import elysian_realm

    async with app.test_matcher(elysian_realm) as ctx:
        v11bot = ctx.create_bot(base=OBV11Bot)  # noqa: F811
        v11event = fake_group_message_event_v11(message=OBV11Message("/乐土人人"))

        ctx.receive_event(v11bot, v11event)
        should_send_saa(
            ctx,
            MessageFactory("未找到指定角色"),
            v11bot,
            event=v11event,
        )
        ctx.should_finished()
