import os
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest


class TestContrastRepositoryUrl:
    """测试 contrast_repository_url 函数。"""

    @pytest.mark.asyncio
    async def test_repository_url_matches(self):
        from nonebot_plugin_bh3_elysian_realm.utils import contrast_repository_url

        """测试当远程URL匹配时返回True"""
        with patch("subprocess.check_output", return_value=b"https://example.com/repo.git\n"):
            result = await contrast_repository_url("https://example.com/repo.git", Path(os.getcwd()))
            assert result is True

    @pytest.mark.asyncio
    async def test_repository_url_does_not_match(self):
        from nonebot_plugin_bh3_elysian_realm.utils import contrast_repository_url

        """测试当远程URL不匹配时返回False"""
        with patch("subprocess.check_output", return_value=b"https://example.com/another_repo.git\n"):
            result = await contrast_repository_url("https://example.com/repo.git", Path(os.getcwd()))
            assert result is False

    @pytest.mark.asyncio
    async def test_repository_url_subprocess_error(self):
        from nonebot_plugin_bh3_elysian_realm.utils import contrast_repository_url

        """测试执行Git命令出现异常时返回False"""
        with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, ["git"])):
            result = await contrast_repository_url("https://example.com/repo.git", Path(os.getcwd()))
            assert result is False
