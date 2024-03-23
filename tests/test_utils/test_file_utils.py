from pathlib import Path
from unittest.mock import patch
from tempfile import NamedTemporaryFile

import pytest
import aiofiles
from httpx import Response, RequestError, TimeoutException


@pytest.mark.asyncio
class TestLoadJsonFiles:
    async def test_load_empty_file(self):
        from nonebot_plugin_bh3_elysian_realm.utils.file_utils import load_json

        with NamedTemporaryFile(delete=False, suffix=".json") as tmp_file:
            path = Path(tmp_file.name)
            result = await load_json(path)
            assert result == {}

    async def test_load_valid_json(self):
        from nonebot_plugin_bh3_elysian_realm.utils.file_utils import load_json

        file = Path(__file__).parent.parent / "test_res" / "test_nickname.json"
        result = await load_json(file)
        assert result != {}

    async def test_file_not_found(self):
        from nonebot_plugin_bh3_elysian_realm.utils.file_utils import load_json

        path = Path("/path/to/non/existent/file.json")
        with pytest.raises(expected_exception=FileNotFoundError, match="文件 .* 未找到。"):
            await load_json(path)

    @pytest.mark.asyncio
    async def test_load_json_with_invalid_data(self, temp_json_file):
        from nonebot_plugin_bh3_elysian_realm.utils.file_utils import load_json

        async with aiofiles.open(temp_json_file, mode="w", encoding="utf-8") as f:
            await f.write('{"invalid json": ')

        with pytest.raises(ValueError, match="文件 .* 解码错误。"):
            await load_json(temp_json_file)


@pytest.mark.asyncio
class TestSaveJsonFiles:
    async def test_save_empty_dict(self):
        from nonebot_plugin_bh3_elysian_realm.utils.file_utils import load_json, save_json

        with NamedTemporaryFile(delete=False, suffix=".json") as tmp_file:
            path = Path(tmp_file.name)
            save_json(path, {})
            assert await load_json(path) == {}

    async def test_save_valid_json(self):
        from nonebot_plugin_bh3_elysian_realm.utils.file_utils import load_json, save_json

        file = Path(__file__).parent.parent / "test_res" / "test_nickname.json"
        data = await load_json(file)
        with NamedTemporaryFile(delete=False, suffix=".json") as tmp_file:
            path = Path(tmp_file.name)
            save_json(path, data)
            assert await load_json(path) == data

    def test_file_not_found(self):
        from nonebot_plugin_bh3_elysian_realm.utils.file_utils import save_json

        file = Path(__file__)
        with pytest.raises(expected_exception=FileNotFoundError, match="文件 .* 不存在或不是一个JSON文件。"):
            save_json(file, {})

    async def test_illegal_dict(self, temp_json_file):
        from nonebot_plugin_bh3_elysian_realm.utils.file_utils import save_json

        def unserializable_function():
            pass  # pragma: no cover

        with pytest.raises(
            TypeError,
            match="Serialization error",
        ):
            save_json(temp_json_file, unserializable_function)  # type: ignore


class TestListJpgFiles:
    def test_list_jpg_files(self):
        from nonebot_plugin_bh3_elysian_realm.utils.file_utils import list_jpg_files

        path = Path(__file__).parent.parent / "test_res"
        assert list_jpg_files(path) == ["Human"]


@pytest.mark.asyncio
class TestStringToList:
    def test_string_to_list(self):
        from nonebot_plugin_bh3_elysian_realm.utils.file_utils import string_to_list

        assert string_to_list("a, b, c") == ["a", "b", "c"]
        assert string_to_list("a,b,c") == ["a", "b", "c"]
        assert string_to_list("a, b,c") == ["a", "b", "c"]
        assert string_to_list("a,b, c") == ["a", "b", "c"]
        assert string_to_list("a,b") == ["a", "b"]
        assert string_to_list("a") == ["a"]
        assert string_to_list("") == []
        assert string_to_list(" ") == []


@pytest.mark.asyncio
class TestFindKeyByValue:
    async def test_find_key_by_value(self):
        from nonebot_plugin_bh3_elysian_realm.utils.file_utils import load_json, find_key_by_value

        data = await load_json(Path(__file__).parent.parent / "test_res" / "test_nickname.json")
        assert await find_key_by_value(data, "人律") == "Human"
        assert await find_key_by_value(data, "人人") is None


@pytest.mark.asyncio
async def test_identify_empty_value_keys():
    from nonebot_plugin_bh3_elysian_realm.utils.file_utils import load_json, identify_empty_value_keys

    data = await load_json(Path(__file__).parent.parent / "test_res" / "test_nickname.json")
    assert await identify_empty_value_keys(data) == ["Vicissitude_Attack"]


@pytest.mark.asyncio
async def test_list_all_keys():
    from nonebot_plugin_bh3_elysian_realm.utils.file_utils import load_json, list_all_keys

    data = await load_json(Path(__file__).parent.parent / "test_res" / "test_nickname.json")
    assert await list_all_keys(data) == [
        "Human",
        "CosmicExpression_Mixed",
        "Vicissitude_Attack",
    ]


@pytest.mark.asyncio
async def test_merge_dicts():
    from nonebot_plugin_bh3_elysian_realm.utils.file_utils import load_json, merge_dicts

    data = await load_json(Path(__file__).parent.parent / "test_res" / "test_nickname.json")
    assert await merge_dicts(data, {"test": ["test"]}) == {
        "Human": ["人律", "爱律"],
        "Vicissitude_Attack": [],
        "CosmicExpression_Mixed": ["大格蕾修混合流"],
        "test": ["test"],
    }


@pytest.mark.asyncio
async def test_merge_dicts_with_update():
    from nonebot_plugin_bh3_elysian_realm.utils.file_utils import load_json, merge_dicts

    data = await load_json(Path(__file__).parent.parent / "test_res" / "test_nickname.json")
    assert await merge_dicts(data, {"Human": ["老婆"]}) == {
        "Human": ["老婆"],
        "Vicissitude_Attack": [],
        "CosmicExpression_Mixed": ["大格蕾修混合流"],
    }


@pytest.mark.asyncio
class TestCheckURL:
    @patch("httpx.Client.head")
    async def test_check_url_success_and_failure(self, mock_head):
        from nonebot_plugin_bh3_elysian_realm.utils import check_url

        # 测试返回 200 状态码
        mock_head.return_value = Response(200)
        result = await check_url("https://example.com", proxy_url="http://proxyserver:8080")
        assert result is True

        # 测试返回 404 状态码
        mock_head.return_value = Response(404)
        result = await check_url("https://example.com", proxy_url="http://proxyserver:8080")
        assert result is False

    @patch("httpx.Client.head")
    async def test_check_url_request_error(self, mock_head):
        from nonebot_plugin_bh3_elysian_realm.utils import check_url

        # 模拟抛出 RequestError
        mock_head.side_effect = RequestError(message="Mocked request error", request=None)

        # 测试处理 RequestError 的情况
        result = await check_url("https://example.com", proxy_url="http://proxyserver:8080")
        assert result is False

    @patch("httpx.Client.head")
    async def test_check_url_timeout_exception(self, mock_head):
        from nonebot_plugin_bh3_elysian_realm.utils import check_url

        # 模拟抛出 TimeoutException
        mock_head.side_effect = TimeoutException(message="Mocked timeout", request=None)

        # 测试处理 TimeoutException 的情况
        result = await check_url("https://example.com", proxy_url="http://proxyserver:8080")
        assert result is False
