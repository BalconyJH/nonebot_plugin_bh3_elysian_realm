import os
import re
import asyncio
from pathlib import Path
from typing import Union

from tqdm import tqdm
from nonebot import logger


def update_progress(stderr_lines):
    """更新克隆或拉取资源的进度条"""
    with tqdm(desc="更新中") as pbar:
        for line in stderr_lines:
            logger.debug(line)
            speed_match = re.search(r"\|\s*([\d.]+\s*[\w/]+/s)", line)
            if speed_match:
                speed = speed_match.group(1)
                pbar.set_postfix_str(f"下载速度: {speed}")
            pbar.update()


async def git_pull(image_path: Path) -> bool:
    clone_command = ["git", "pull"]
    process = None

    if not os.path.exists(image_path):
        logger.error(f"目录 {image_path} 不存在")
        return False

    os.chdir(image_path)

    # try:
    #     with subprocess.Popen(clone_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
    #         stdout, stderr = process.communicate()
    #
    #         if "Already up to date." in stdout:
    #             logger.info("图片资源已是最新版本")
    #         else:
    #             logger.info("图片资源开始更新")
    #             with tqdm(desc="更新中") as pbar:
    #                 for line in stderr.splitlines():
    #                     logger.debug(line)
    #                     if speed_match := re.search(r"\|\s*([\d.]+\s*[\w/]+/s)", line):
    #                         speed = speed_match[1]
    #                         pbar.set_postfix_str(f"下载速度: {speed}")
    #                     pbar.update()
    #             logger.info("图片资源更新完成")
    #
    #         return True
    # except subprocess.CalledProcessError:
    #     logger.error("图片资源更新异常")
    #     return False
    try:
        process = await asyncio.create_subprocess_exec(
            *clone_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()
        stdout_lines = stdout.decode("utf-8").splitlines()
        stderr_lines = stderr.decode("utf-8").splitlines()

        if "Already up to date." in stdout_lines:
            logger.info("图片资源已是最新版本")
        else:
            logger.info("图片资源开始更新")
            update_progress(stderr_lines)
            logger.info("图片资源更新完成")

        await process.wait()
        return True
    except asyncio.CancelledError:
        logger.error("图片资源更新被取消")
        return False
    except Exception as e:
        logger.error(f"图片资源更新异常: {e!s}")
        return False
    finally:
        if process and process.returncode is None:
            logger.info("终止未结束的子进程")
            process.terminate()
            await process.wait()


async def git_clone(repository_url: str, image_path: Path) -> Union[bool, str]:
    clone_command = ["git", "clone", "--progress", "--depth=1", repository_url, str(image_path)]
    process = None

    if os.path.exists(image_path) and os.listdir(image_path):
        logger.error(f"目录 {image_path} 不为空")
        return False

    if (image_path / ".gitkeep").exists():
        os.remove(image_path / ".gitkeep")

    try:
        process = await asyncio.create_subprocess_exec(
            *clone_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()
        # stdout_lines = stdout.decode("utf-8").splitlines()
        stderr_lines = stderr.decode("utf-8").splitlines()

        update_progress(stderr_lines)

    except asyncio.CancelledError:
        logger.error("克隆被取消")
        return False
    except Exception as e:
        logger.error(f"克隆异常: {e!s}")
        return False
    finally:
        if process and process.returncode is None:
            logger.info("终止未结束的子进程")
            process.terminate()
            await process.wait()

    return False


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
    process = None
    try:
        os.chdir(path)

        # 异步执行 "git config --get remote.origin.url" 命令
        process = await asyncio.create_subprocess_exec(
            "git",
            "config",
            "--get",
            "remote.origin.url",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()
        remote_url = stdout.decode("utf-8").strip()

        if process.returncode == 0:
            if remote_url == repository_url:
                logger.debug("指定仓库地址与目录下仓库地址匹配")
                return True
            else:
                logger.debug(f"目录下仓库地址: {remote_url}")
                logger.debug(f"指定仓库地址: {repository_url}")
                return False
        else:
            logger.error(f"获取远程仓库地址时出错：{stderr.decode('utf-8').strip()}")
            return False

    except Exception as e:
        logger.error(f"检查仓库地址时发生异常：{e}")
        return False
    finally:
        os.chdir(original_cwd)
        if process and process.returncode is None:
            logger.info("终止未结束的子进程")
            process.terminate()
            await process.wait()
