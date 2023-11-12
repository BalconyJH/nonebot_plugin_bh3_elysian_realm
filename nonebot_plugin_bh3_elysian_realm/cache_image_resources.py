import asyncio
import io
import os
import re
import subprocess
import sys
import zipfile
# from nonebot import get_driver

import httpx
from tqdm import tqdm


# config = get_driver().config


async def git_pull():
    repository_url = "https://github.com/MskTmi/ElysianRealm-Data"  # 请替换为实际的 Git 仓库 URL
    clone_command = ["git", "pull"]
    repo_dir = "resources/images"

    # 确保目录存在
    if not os.path.exists(repo_dir):
        print(f"目录 {repo_dir} 不存在")
        return

    # 更改当前工作目录
    os.chdir(repo_dir)
    print(f"当前工作目录: {os.getcwd()}\n")

    try:
        # 使用 Popen 而不是 run
        with subprocess.Popen(clone_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            # 使用 tqdm 显示进度
            with tqdm(desc="仓库更新中") as pbar:
                print(process.stdout.read())
                for line in process.stderr:  # git clone 的进度信息在 stderr 中
                    speed_match = re.search(r"\|\s*([\d.]+\s*[\w/]+/s)", line)
                    if speed_match:
                        speed = speed_match.group(1)
                        pbar.set_postfix_str(f"下载速度: {speed}")
                    pbar.update()  # 更新进度条

    except subprocess.CalledProcessError as e:
        pass


async def git_clone():
    repository_url = "https://github.com/MskTmi/ElysianRealm-Data"
    clone_command = ["git", "clone", "--progress", "--depth=1", repository_url, "resources/images"]

    try:
        # 使用 Popen 而不是 run
        with subprocess.Popen(clone_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            # 使用 tqdm 显示进度
            with tqdm(desc="仓库克隆中") as pbar:
                for line in process.stderr:  # git clone 的进度信息在 stderr 中
                    if "fatal: destination path" in line:
                        print(f"data目录下已存在ElysianRealm-Data, 请勿重复获取")
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
            print(f"{error_info}\ndata目录下已存在ElysianRealm-Data, 请勿重复获取")
        else:
            print(f"clone出现异常:\n{error_info}")
            print(e)


if __name__ == "__main__":
    asyncio.run(git_clone())
