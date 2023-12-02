from pathlib import Path

import pytest
from nonebug import App
from pytest_mock import MockerFixture
from nonebug_saa import should_send_saa
from nonebot_plugin_saa import MessageFactory
from nonebot.adapters.onebot.v11 import Bot as OBV11Bot
from nonebot.adapters.onebot.v11 import Message as OBV11Message

from tests.utils import fake_group_message_event_v11


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


@pytest.mark.asyncio
async def test_got_introduction(app: App, mocker: MockerFixture):
    import nonebot_plugin_saa as saa

    from nonebot_plugin_bh3_elysian_realm.plugins import elysian_realm

    print(Path(__file__).parent / "Human.jpg")
    image = saa.Image(Path(__file__).parent / "Human.jpg")
    mocker.patch(image)

    async with app.test_matcher(elysian_realm) as ctx:
        v11bot = ctx.create_bot(base=OBV11Bot)
        v11event = fake_group_message_event_v11(message=OBV11Message("/乐土人律"))

        # todo: find a better way to mock
        ctx.receive_event(v11bot, v11event)
        should_send_saa(
            ctx,
            MessageFactory(image),
            v11bot,
            event=v11event,
        )
        ctx.should_finished()
