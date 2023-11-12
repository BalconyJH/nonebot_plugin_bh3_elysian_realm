
import nonebot
import pytest
from nonebot.adapters.onebot.v11 import Adapter as V11Adapter


@pytest.fixture(scope="session", autouse=True)
def _load_bot():
    # 加载适配器
    driver = nonebot.get_driver()
    driver.register_adapter(V11Adapter)
