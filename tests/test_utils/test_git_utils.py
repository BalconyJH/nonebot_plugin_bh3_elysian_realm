import os
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest


class TestContrastRepositoryUrl:
    """测试 contrast_repository_url 函数。"""

    @pytest.mark.asyncio
    async def test_repository_url_matches(self):
        from nonebot_plugin_bh3_elysian_realm.utils import contrast_repository_url

        """测试当远程URL匹配时返回True"""
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=(b"https://example.com/repo.git\n", b""))
        mock_process.returncode = 0

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await contrast_repository_url("https://example.com/repo.git", Path(os.getcwd()))
            assert result is True

    @pytest.mark.asyncio
    async def test_repository_url_does_not_match(self):
        from nonebot_plugin_bh3_elysian_realm.utils import contrast_repository_url

        """测试当远程URL不匹配时返回False"""
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=(b"https://another-repo.com/repo.git\n", b""))
        mock_process.returncode = 0

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await contrast_repository_url("https://example.com/repo.git", Path(os.getcwd()))
            assert result is False

    @pytest.mark.asyncio
    async def test_repository_url_subprocess_error(self):
        from nonebot_plugin_bh3_elysian_realm.utils import contrast_repository_url

        """测试执行Git命令出现异常时返回False"""
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=(b"", b"fatal: not a git repository"))
        mock_process.returncode = 1

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await contrast_repository_url("https://example.com/repo.git", Path(os.getcwd()))
            assert result is False
