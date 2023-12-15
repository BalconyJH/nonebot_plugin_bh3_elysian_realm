import json
import random
import asyncio
from collections import OrderedDict
from datetime import datetime, timedelta

import httpx
from lxml import etree

# from nonebot_plugin_bh3_elysian_realm.config import plugin_config


def standardize_date(created_at):
    """标准化微博发布时间"""
    if "刚刚" in created_at:
        ts = datetime.now()
    elif "分钟" in created_at:
        minute = created_at[: created_at.find("分钟")]
        minute = timedelta(minutes=int(minute))
        ts = datetime.now() - minute
    elif "小时" in created_at:
        hour = created_at[: created_at.find("小时")]
        hour = timedelta(hours=int(hour))
        ts = datetime.now() - hour
    elif "昨天" in created_at:
        day = timedelta(days=1)
        ts = datetime.now() - day
    else:
        created_at = created_at.replace("+0800 ", "")
        ts = datetime.strptime(created_at, "%c")

    created_at = ts.strftime("%Y-%m-%dT%H:%M:%S")
    full_created_at = ts.strftime("%Y-%m-%d %H:%M:%S")
    return created_at, full_created_at


class Weibo:
    def __init__(self):
        self.weibo_url = "https://m.weibo.cn/api/container/getIndex?"
        self.user_id = "7853323663"
        self.weibo_headers = {
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/86.0.4240.111 Safari/537.36")
            ,
            "Cookie": ""
        }

    async def get_json(self, params):
        async with httpx.AsyncClient(verify=False) as client:
            resp = await client.get(self.weibo_url, headers=self.weibo_headers, params=params)
            print(resp.json())
            return resp.json(), resp.status_code

    async def get_weibo_json(self, page):
        params = (
            {
                "container_ext": "profile_uid:" + self.user_id,
                "containerid": "100103type=401&q=",
                "page_type": "searchall",
            }
        )
        params["page"] = page
        raw_data, _ = await self.get_json(params)
        print(raw_data)
        return raw_data

    async def get_one_weibo(self, info):
        """获取一条微博的全部信息"""
        try:
            weibo_info = info["mblog"]
            weibo_id = weibo_info["id"]
            retweeted_status = weibo_info.get("retweeted_status")
            is_long = (
                True if weibo_info.get("pic_num") > 9 else weibo_info.get("isLongText")
            )
            if retweeted_status and retweeted_status.get("id"):  # 转发
                retweet_id = retweeted_status.get("id")
                is_long_retweet = retweeted_status.get("isLongText")
                if is_long:
                    weibo = self.get_long_weibo(weibo_id)
                    if not weibo:
                        weibo = self.parse_weibo(weibo_info)
                else:
                    weibo = self.parse_weibo(weibo_info)
                if is_long_retweet:
                    retweet = self.get_long_weibo(retweet_id)
                    if not retweet:
                        retweet = self.parse_weibo(retweeted_status)
                else:
                    retweet = self.parse_weibo(retweeted_status)
                (
                    retweet["created_at"],
                    retweet["full_created_at"],
                ) = standardize_date(retweeted_status["created_at"])
                weibo["retweet"] = retweet
            else:  # 原创
                if is_long:
                    weibo = self.get_long_weibo(weibo_id)
                    if not weibo:
                        weibo = self.parse_weibo(weibo_info)
                else:
                    weibo = self.parse_weibo(weibo_info)
            weibo["created_at"], weibo["full_created_at"] = standardize_date(
                weibo_info["created_at"]
            )
            return weibo
        except Exception as e:
            print(e)

    async def get_long_weibo(self, id):
        """获取长微博"""
        url = "https://m.weibo.cn/detail/%s" % id
        for i in range(5):
            async with httpx.AsyncClient(verify=False) as client:
                html = (await client.get(url, headers=self.weibo_headers)).text
                html = html[html.find('"status":') :]
                html = html[: html.rfind('"call"')]
                html = html[: html.rfind(",")]
                html = "{" + html + "}"
                js = json.loads(html, strict=False)
                weibo_info = js.get("status")
                if weibo_info:
                    weibo = self.parse_weibo(weibo_info)
                    return weibo
                await asyncio.sleep(random.randint(6, 10))

    def parse_weibo(self, weibo_info):
        weibo = OrderedDict()
        if weibo_info["user"]:
            weibo["user_id"] = weibo_info["user"]["id"]
            weibo["screen_name"] = weibo_info["user"]["screen_name"]
        else:
            weibo["user_id"] = ""
            weibo["screen_name"] = ""
        weibo["id"] = int(weibo_info["id"])
        weibo["bid"] = weibo_info["bid"]
        text_body = weibo_info["text"]
        selector = etree.HTML(f"{text_body}<hr>" if text_body.isspace() else text_body)
        if self.remove_html_tag:
            text_list = selector.xpath("//text()")
            # 若text_list中的某个字符串元素以 @ 或 # 开始，则将该元素与前后元素合并为新元素，否则会带来没有必要的换行
            text_list_modified = []
            for ele in range(len(text_list)):
                if ele > 0 and (text_list[ele-1].startswith(("@","#")) or text_list[ele].startswith(("@","#"))):
                    text_list_modified[-1] += text_list[ele]
                else:
                    text_list_modified.append(text_list[ele])
            weibo["text"] = "\n".join(text_list_modified)
        else:
            weibo["text"] = text_body
        weibo["article_url"] = self.get_article_url(selector)
        weibo["pics"] = self.get_pics(weibo_info)
        weibo["video_url"] = self.get_video_url(weibo_info)
        weibo["location"] = self.get_location(selector)
        weibo["created_at"] = weibo_info["created_at"]
        weibo["source"] = weibo_info["source"]
        weibo["attitudes_count"] = self.string_to_int(
            weibo_info.get("attitudes_count", 0)
        )
        weibo["comments_count"] = self.string_to_int(
            weibo_info.get("comments_count", 0)
        )
        weibo["reposts_count"] = self.string_to_int(weibo_info.get("reposts_count", 0))
        weibo["topics"] = self.get_topics(selector)
        weibo["at_users"] = self.get_at_users(selector)
        return self.standardize_info(weibo)

    @staticmethod
    def get_pics(weibo_info):
        """获取微博原始图片url"""
        if weibo_info.get("pics"):
            pic_info = weibo_info["pics"]
            pic_list = [pic["large"]["url"] for pic in pic_info]
            pics = ",".join(pic_list)
        else:
            pics = ""
        return pics

    @staticmethod
    def get_live_photo(weibo_info):
        """获取live photo中的视频url"""
        live_photo_list = []
        live_photo = weibo_info.get("pic_video")
        if live_photo:
            prefix = "https://video.weibo.com/media/play?livephoto=//us.sinaimg.cn/"
            for i in live_photo.split(","):
                if len(i.split(":")) == 2:
                    url = prefix + i.split(":")[1] + ".mov"
                    live_photo_list.append(url)
            return live_photo_list

    def get_video_url(self, weibo_info):
        """获取微博视频url"""
        video_url = ""
        video_url_list = []
        if weibo_info.get("page_info"):
            if (
                    weibo_info["page_info"].get("urls")
                    or weibo_info["page_info"].get("media_info")
            ) and weibo_info["page_info"].get("type") == "video":
                media_info = weibo_info["page_info"]["urls"]
                if not media_info:
                    media_info = weibo_info["page_info"]["media_info"]
                video_url = media_info.get("mp4_720p_mp4")
                if not video_url:
                    video_url = media_info.get("mp4_hd_url")
                if not video_url:
                    video_url = media_info.get("hevc_mp4_hd")
                if not video_url:
                    video_url = media_info.get("mp4_sd_url")
                if not video_url:
                    video_url = media_info.get("mp4_ld_mp4")
                if not video_url:
                    video_url = media_info.get("stream_url_hd")
                if not video_url:
                    video_url = media_info.get("stream_url")
        if video_url:
            video_url_list.append(video_url)
        live_photo_list = self.get_live_photo(weibo_info)
        if live_photo_list:
            video_url_list += live_photo_list
        return ";".join(video_url_list)


if __name__ == "__main__":
    asyncio.run(Weibo().get_weibo_json(1))
