from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import argparse
import re
from youtube_transcript_api import YouTubeTranscriptApi

def get_video_id(url: str) -> str | None:
    """
    从 YouTube URL 中提取视频 ID。
    支持的格式:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    """
    # 正则表达式匹配 video_id
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"youtu\.be\/([0-9A-Za-z_-]{11})"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript(video_id: str, proxies: dict | None = None) -> list | str:
    """
    根据给定的 YouTube 视频 ID 获取字幕。

    Args:
        video_id: YouTube 视频的唯一标识符。
        proxies: 用于请求的代理配置 (例如: {'http': '...', 'https': '...'})。

    Returns:
        返回一个包含字幕数据的列表，如果获取失败则返回包含错误信息的字符串。
    """
    print(f"正在尝试获取视频 ID '{video_id}' 的字幕...")
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxies)
        print("成功获取字幕。")
        return transcript
    except Exception as e:
        print(f"获取字幕失败: {e}")
        return f"获取字幕失败: {e}"

def main(url: str):
    """
    主函数，解析命令行参数并执行字幕提取。
    """

    # --- 代理配置 ---
    # 如果您需要通过代理服务器访问，请在此处填写您的代理信息。
    # 如果不需要，请将 proxies 设置为 None。
    # 示例:
    # proxies = {
    #    'http': 'http://127.0.0.1:7890',
    #    'https': 'http://127.0.0.1:7890'
    # }
    proxies = None
    
    video_id = get_video_id(url)
    
    if not video_id:
        error_message = f"错误: 无法从 URL '{url}' 中提取有效的 YouTube 视频 ID。"
        print(error_message)
        return error_message

    transcript_data = get_transcript(video_id, proxies=proxies)
    
    if isinstance(transcript_data, str):
        return transcript_data

    full_transcript = "\n".join([item['text'] for item in transcript_data])

    return full_transcript

class YoutubeSubtitlesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        url = tool_parameters["query"]
        full_transcript = main(url)

        yield self.create_text_message(text=full_transcript)
