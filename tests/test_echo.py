
import pytest
from nonebot.adapters.onebot.v11 import MessageEvent, Message
from nonebot.adapters.onebot.v11.event import Sender
from nonebug import App


@pytest.mark.asyncio
async def test_echo(app: App):
    from nonebot_plugin_bh3_elysian_realm import elysian_realm

    event = MessageEvent(
        time=1699759597,
        self_id=12345679,
        message=Message("/乐土 人律"),
        user_id=1234567,
        message_id=11111,
        raw_message="/乐土 人律",
        sub_type="test",
        message_type="test",
        sender=Sender(
            user_id=1234567,
        ),
        font=0,
        post_type="message",
    )

    async with app.test_matcher(elysian_realm) as ctx:
        bot = ctx.create_bot()
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "指定的角色是人律", result=None)
        ctx.should_finished(elysian_realm)
