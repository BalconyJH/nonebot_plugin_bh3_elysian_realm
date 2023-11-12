import asyncio
import json
from pathlib import Path

Path = Path(__file__).parent / "resources" / "nickname.json"


async def find_key_by_value(json_file, value):
    """
    从 JSON 文件中查找给定值对应的键。

    参数:
        json_file (str): JSON 文件的路径。
        value (str): 要查找的值。

    返回:
        str: 找到的键，如果没有找到则返回 None。
    """
    try:
        with open(json_file, encoding="utf-8") as file:
            data = json.load(file)

        for key, values in data.items():
            if value in values:
                return key
        return None
    except FileNotFoundError:
        print(f"文件 {json_file} 未找到。")
        return None
    except json.JSONDecodeError:
        print(f"文件 {json_file} 不是有效的 JSON 格式。")
        return None


if __name__ == "__main__":
    print(asyncio.run(find_key_by_value(Path, "月下誓约普攻流")))
