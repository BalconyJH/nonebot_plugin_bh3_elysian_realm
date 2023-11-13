import os
import re
import subprocess

from nonebot import logger
from tqdm import tqdm

from .config import plugin_config


# from nonebot import get_driver


# config = get_driver().config


async def git_pull():
    clone_command = ["git", "pull"]
    repo_dir = "resources/images"

    # 确保目录存在
    if not os.path.exists(repo_dir):
        print(f"目录 {repo_dir} 不存在")
        return

    # 更改当前工作目录
    os.chdir(repo_dir)

    try:
        # 使用 Popen 而不是 run
        with subprocess.Popen(clone_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            # 使用 tqdm 显示进度
            if "Already up to date." in process.stdout.read():
                print("ElysianRealm-Data已是最新版本")
            else:
                with tqdm(desc="仓库更新中") as pbar:
                    # print(process.stdout.read())
                    for line in process.stderr:  # git clone 的进度信息在 stderr 中
                        speed_match = re.search(r"\|\s*([\d.]+\s*[\w/]+/s)", line)
                        if speed_match:
                            speed = speed_match.group(1)
                            pbar.set_postfix_str(f"下载速度: {speed}")
                        pbar.update()  # 更新进度条

    except subprocess.CalledProcessError:
        logger.error("git pull 出现异常")


repository = "https://github.com/MskTmi/ElysianRealm-Data"


async def git_clone(repository_url: str = repository):
    clone_command = ["git", "clone", "--progress", "--depth=4", repository_url, "resources/images"]

    try:
        # 使用 Popen 而不是 run
        with subprocess.Popen(clone_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            # 使用 tqdm 显示进度
            with tqdm(desc="仓库克隆中") as pbar:
                for line in process.stderr:  # git clone 的进度信息在 stderr 中
                    if "fatal: destination path" in line:
                        print("data目录下已存在ElysianRealm-Data, 请勿重复获取")
                        break
                    speed_match = re.search(r"\|\s*([\d.]+\s*[\w/]+/s)", line)
                    if speed_match:
                        speed = speed_match.group(1)
                        pbar.set_postfix_str(f"下载速度: {speed}")
                    pbar.update()  # 更新进度条

        # 检查进程是否成功完成
        if process.returncode == 0:
            print("乐土攻略获取完成")

    except subprocess.CalledProcessError as e:
        error_info = e.stderr
        if "fatal: destination path" in error_info:
            logger.info(f"{error_info}\ndata目录下已存在ElysianRealm-Data")
        else:
            logger.error(f"clone出现异常:\n{error_info}")


async def get_git_repository_url(repository_url: str) -> bool:
    """
    异步地检查当前目录是否为指定的 Git 仓库。

    此函数通过执行 Git 命令来获取当前目录 Git 仓库的远程 URL。
    然后，它会将这个 URL 与提供的 URL 进行比较。

    参数:
        repository_url (str): 要检查的 Git 仓库的 URL。

    返回:
        bool: 如果当前目录是指定的 Git 仓库，则返回 True；否则返回 False。

    异常:
        subprocess.CalledProcessError: 如果在执行 Git 命令时出错，将捕获此异常并返回 False。

    注意:
        这个函数假设 'git' 命令在系统路径上可用，并且当前目录是一个 Git 仓库。
        如果当前目录不是 Git 仓库，或者 'git' 命令无法执行，函数将返回 False。
    """
    try:
        remote_url = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"],
            stderr=subprocess.STDOUT
        ).strip().decode("utf-8")

        if remote_url == repository_url:
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        return False


async def find_image(role: str) -> str:
    """根据传入的角色名，返回对应的图片"""
    image_path = plugin_config.image_path / f"{role}.jpg"
    print(image_path)
    return image_path
