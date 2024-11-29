# from googleapiclient.discovery import build
from pytubefix import YouTube, Search
import os
import time
import random
import traceback
import subprocess


# 使用pytubefix下载视频
def download_video(video_url, output_name, output_path, proxy=None, high_res=False):
        """
        下载视频
        
        Args:
            video_url (str): 视频URL
            output_path (str): 保存路径
            
        Returns:
            str: 下载文件的路径，失败返回None
        """
        try:
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            if proxy:
                proxies = {
                    'http': proxy,
                    'https': proxy
                }

                yt = YouTube(video_url, proxies=proxies)
            else:
                yt = YouTube(video_url) 

            print(f"正在下载: {yt.title}")
            if high_res:
                # 分别下载视频和音频
                video = yt.streams.filter(adaptive=True, file_extension='mp4').\
                    order_by('resolution').desc().first()
                audio = yt.streams.filter(only_audio=True).first()
                down_video = video.download(output_path)
                down_audio = audio.download(output_path)
                print(f"下载完成，正在合并视频和音频")
                # 使用 ffmpeg 合并视频和音频
                output_file = os.path.join(output_path, f"{output_name}.mp4")
                subprocess.run(['ffmpeg', '-i', down_video, '-i', down_audio, '-c:v', 'copy', '-c:a', 'aac', output_file])
            else:
                downloaded_file = yt.streams.filter(progressive=True, file_extension='mp4').\
                    order_by('resolution').desc().first().download(output_path)
                # 重命名下载到的视频文件
                new_filename = f"{output_name}.mp4"
                output_file = os.path.join(output_path, new_filename)
                os.rename(downloaded_file, output_file)
                print(f"下载完成，存储为: {new_filename}")

            return output_file
            
        except Exception as e:
            print(f"下载视频时发生错误:")
            traceback.print_exc()
            return None
        

class PurePytubefixDownloader:
    """
    只使用pytubefix进行搜索和下载的youtube视频下载器
    """
    def __init__(self, proxy=None):
        self.proxy = proxy
    
    def search_video(self, keyword, max_results=None):
        if self.proxy:
            proxies = {
                'http': self.proxy,
                'https': self.proxy
            }
            results = Search(keyword, proxies=proxies)
        else:
            results = Search(keyword)
        videos = []
        for result in results.videos:
            # print(f'Title: {result.title}')
            # print(f'URL: {result.watch_url}')
            # print(f'Duration: {result.length} sec')
            videos.append({
                'id': result.video_id,
                'title': result.title,
                'url': result.watch_url,
                'duration': result.length
            })
        if max_results:
            videos = videos[:max_results]
        return videos
    
    def download_video(self, video_url, output_name, output_path, high_res=False):
        return download_video(video_url, output_name, output_path, self.proxy, high_res)

