import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Union, Optional

from tqdm import tqdm
import nonebot_plugin_saa as saa
from nonebot import logger, get_bot
from nonebot_plugin_saa import TargetQQPrivate
from nonebot_plugin_apscheduler import scheduler

from nonebot_plugin_bh3_elysian_realm.config import global_config, plugin_config


def load_json(json_file: Path) -> Dict:
    if not json_file.exists() or os.path.getsize(json_file) == 0:
        logger.warning(f"文件 {json_file} 为空或不存在。")
        return {}
    try:
        with json_file.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"文件 {json_file} 未找到。")
    except json.JSONDecodeError:
        logger.error(f"文件 {json_file} 解码错误。")
    raise FileNotFoundError


def save_json(json_file, data: Dict):
    try:
        with json_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except FileNotFoundError:
        logger.error(f"文件 {json_file} 未找到。")
    except json.JSONDecodeError:
        logger.error(f"文件 {json_file} 解码错误。")


async def find_key_by_value(data: Dict, value: str) -> Optional[str]:
    """
    从 JSON 文件中查找给定值对应的键。

    参数:
        json_file (str): JSON 文件的路径。
        value (str): 要查找的值。

    返回:
        str: 找到的键，如果没有找到则返回 None。
    """
    for key, values in data.items():
        if value in values:
            return key
    return None


async def identify_empty_value_keys(data: Dict) -> List[str]:
    """
    从 Dict 中查找值为空的键。

    参数:
        data (Dict): 要查找的 Dict。

    返回:
        List[str]: 找到的键列表。
    """
    empty_value_keys = []
    for key, values in data.items():
        if not values:
            empty_value_keys.append(key)
    return empty_value_keys


async def list_all_keys(data: Dict) -> List[str]:
    """
    列出 JSON 文件中的所有键。

    参数:
        json_file (str): JSON 文件的路径。

    返回:
        List[str]: JSON 文件中的所有键。
    """
    return list(data.keys())


async def git_pull() -> bool:
    clone_command = ["git", "pull"]

    if not os.path.exists(plugin_config.image_path):
        logger.error(f"目录 {plugin_config.image_path} 不存在")
        return False

    os.chdir(plugin_config.image_path)

    try:
        with subprocess.Popen(clone_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            stdout, stderr = process.communicate()

            if "Already up to date." in stdout:
                logger.info("图片资源已是最新版本")
                return True
            else:
                logger.info("图片资源开始更新")
                with tqdm(desc="更新中") as pbar:
                    for line in stderr.splitlines():
                        speed_match = re.search(r"\|\s*([\d.]+\s*[\w/]+/s)", line)
                        if speed_match:
                            speed = speed_match.group(1)
                            pbar.set_postfix_str(f"下载速度: {speed}")
                        pbar.update()
                logger.info("图片资源更新完成")
                return True

    except subprocess.CalledProcessError:
        logger.error("图片资源更新异常")
        return False


async def git_clone(repository_url: str = plugin_config.image_repository):
    clone_command = ["git", "clone", "--progress", "--depth=1", repository_url, plugin_config.image_path]

    try:
        if os.path.exists(plugin_config.image_path) and os.listdir(plugin_config.image_path):
            logger.error(f"目录 {plugin_config.image_path} 不为空")
            return
        if os.path.exists(plugin_config.image_path / ".gitkeep"):
            os.remove(plugin_config.image_path / ".gitkeep")
        with subprocess.Popen(clone_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            with tqdm(desc="克隆中") as pbar:
                if process.stderr is not None:
                    for line in process.stderr:
                        speed_match = re.search(r"\|\s*([\d.]+\s*[\w/]+/s)", line)
                        if speed_match:
                            speed = speed_match.group(1)
                            pbar.set_postfix_str(f"下载速度: {speed}")
                        pbar.update()
                        if "done." in line:
                            logger.info("乐土攻略获取完成")

    except subprocess.CalledProcessError as e:
        error_info = e.stderr
        if "fatal: destination path" in error_info:
            logger.warning(f"{error_info}\n{plugin_config.image_path}目录下已存在数据文件")
            return error_info
        else:
            logger.error(f"克隆异常:\n{error_info}")
            return error_info


async def contrast_repository_url(repository_url: str, path: Path) -> bool:
    """
    异步地检查指定目录是否为指定的 Git 仓库。

    此函数通过在指定目录执行 Git 命令来获取 Git 仓库的远程 URL。
    然后，它会将这个 URL 与提供的 URL 进行比较。

    参数:
        repository_url (str): 要检查的 Git 仓库的 URL。
        path (Path): 要检查的目录路径。

    返回:
        bool: 如果指定目录是指定的 Git 仓库，则返回 True；否则返回 False。

    异常:
        subprocess.CalledProcessError: 如果在执行 Git 命令时出错，将捕获此异常并返回 False。

    注意:
        这个函数假设 'git' 命令在系统路径上可用。
        如果指定目录不是 Git 仓库，或者 'git' 命令无法执行，函数将返回 False。
    """
    original_cwd = Path.cwd()
    try:
        os.chdir(path)
        remote_url = (
            subprocess.check_output(["git", "config", "--get", "remote.origin.url"], stderr=subprocess.STDOUT)
            .strip()
            .decode("utf-8")
        )
        if remote_url == repository_url:
            logger.debug("指定仓库地址与目录下仓库地址匹配")
            return True
        else:
            logger.debug(f"目录下仓库地址: {remote_url}")
            logger.debug(f"指定仓库地址: {repository_url}")
            return False
    except subprocess.CalledProcessError:
        return False
    finally:
        os.chdir(original_cwd)


def list_jpg_files(directory: Union[str, Path]) -> List[str]:
    """
    列出指定目录下的所有jpg文件的文件名（不包括子目录）。

    参数:
        directory (str): 要搜索的目录。

    返回:
        List: 包含所有找到的jpg文件名的列表。
    """
    return [os.path.splitext(file)[0] for file in os.listdir(directory) if file.endswith(".jpg")]


def string_to_list(input_str: str) -> list:
    """
    将使用[,]分割的字符串转换为列表。
    :param input_str: 输入字符串
    :return: 列表
    """
    return [item.strip() for item in input_str.split(",")] if input_str else []


async def update_nickname(raw_data: Dict, update_data: Dict) -> Dict:
    """更新nickname.json"""
    for key, value in update_data.items():
        if key not in raw_data:
            raw_data[key] = value
    return raw_data


class ResourcesVerify:
    """资源检查类"""

    def __init__(self):
        self.jpg_list = list_jpg_files(plugin_config.image_path)
        self.nickname_cache = load_json(plugin_config.nickname_path)

    async def verify_nickname(self):
        """检查nickname.json是否存在"""
        if self.nickname_cache is not None:
            cache: List[str] = list(set(self.jpg_list) - set(await list_all_keys(self.nickname_cache)))
            if not cache:
                logger.info("nickname.json已是最新版本")
                return True
            else:
                logger.warning(f"nickname.json缺少以下角色:{cache}")
                save_json(
                    plugin_config.nickname_path, await update_nickname(self.nickname_cache, {key: [] for key in cache})
                )
                return False
        else:
            logger.error("nickname.json不存在")
            raise FileNotFoundError

    @staticmethod
    async def verify_images():
        logger.debug("开始检查图片资源")
        logger.debug(f"图片仓库地址: {plugin_config.image_repository}")
        logger.debug(f"图片仓库路径: {plugin_config.image_path}")
        if await contrast_repository_url(plugin_config.image_repository, plugin_config.image_path):
            await git_pull()
        else:
            await git_clone()


@scheduler.scheduled_job("interval", seconds=plugin_config.resource_validation_time, id="resource_validation")
async def resource_scheduled_job():
    logger.debug("开始检查图片资源计划任务")
    await git_pull()
    await ResourcesVerify().verify_nickname()


@scheduler.scheduled_job("interval", seconds=plugin_config.resource_validation_time, id="null_nickname_warning")
async def null_nickname_warning():
    logger.debug("开始检查nickname.json空值计划任务")
    bot = get_bot()
    empty_value_list = await identify_empty_value_keys(load_json(plugin_config.nickname_path))
    if empty_value_list:
        logger.warning("nickname.json存在空值，请及时更新")
        logger.debug(f"空值列表: {empty_value_list}")
        msg_builder = saa.Text(f"nickname.json存在空值，请及时更新\n空值列表: {empty_value_list}")
        logger.debug(f"superusers: {global_config.superusers}")
        for superuser in global_config.superusers:
            msg_target = TargetQQPrivate(user_id=int(superuser))
            await msg_builder.send_to(msg_target, bot)


async def on_startup():
    """启动前检查"""
    await ResourcesVerify.verify_images()
    await ResourcesVerify().verify_nickname()
    if await identify_empty_value_keys(load_json(plugin_config.nickname_path)):
        logger.warning("nickname.json存在没有昵称的图片，请及时更新")
