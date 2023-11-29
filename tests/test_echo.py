import pytest
from nonebug import App
from nonebot.adapters.onebot.v11 import Bot, Message

from tests.utils import fake_group_message_event_v11


@pytest.mark.asyncio
async def test_echo(app: App):
    from nonebot_plugin_bh3_elysian_realm import elysian_realm

    async with app.test_matcher(elysian_realm) as ctx:
        bot = ctx.create_bot(base=Bot)  # noqa: F811
        event = fake_group_message_event_v11(message=Message("/乐土人律"))

        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "指定的角色是人律", result=None)
        ctx.should_finished()
