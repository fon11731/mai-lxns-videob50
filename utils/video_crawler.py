# from googleapiclient.discovery import build
from pytubefix import YouTube, Search
import os
import time
import random
import subprocess


# 使用pytubefix下载视频
def download_video(video_url, output_name, output_path, high_res=False):
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

            proxies = {
                'http': 'http://127.0.0.1:7890',
                'https': 'http://127.0.0.1:7890'
            }

            yt = YouTube(video_url, proxies=proxies)
            # for stream in yt.streams:
            #     print(stream)
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
            
            # 等待15-30秒，以减少被检测为bot的风险
            time.sleep(random.randint(15, 30))

            return output_file
            
        except Exception as e:
            print(f"下载视频时发生错误: {str(e)}")
            return None

# not use for now
# class YouTubeDownloader:
#     def __init__(self, api_key, proxy=None):
#         """
#         使用官方API进行搜索（需要API Key，每日限额100次，约能查找2次B50）
#         使用pytubefix进行下载的youtube视频下载器
        
#         Args:
#             api_key (str): YouTube Data API key
#         """
#         self.API_NAME = "youtube"
#         self.API_VERSION = "v3"
#         self.api_key = api_key

#         # 创建带代理的 HTTP 对象
#         if proxy:
#             try:
#                 import httplib2
#                 print(f"正在使用代理: {proxy}")
#                 http = httplib2.Http(proxy_info=httplib2.ProxyInfo(
#                     httplib2.socks.PROXY_TYPE_HTTP,
#                     proxy.split(':')[0],
#                     int(proxy.split(':')[1])
#                 ))
#                 # 测试代理连接
#                 proxies = {
#                     'http': 'http://127.0.0.1:7890',
#                     'https': 'http://127.0.0.1:7890'
#                 }
#                 try:
#                     response = requests.get('https://www.google.com', proxies=proxies)
#                     print(f"代理测试状态码: {response.status_code}")
#                 except Exception as e:
#                     print(f"代理测试失败: {e}")
#             except Exception as e:
#                 print(f"代理设置失败: {str(e)}")
#                 http = None
#         else:
#             http = None
        
#         try:
#             print("正在创建 YouTube API 客户端...")
#             self.youtube = build(
#                 self.API_NAME, 
#                 self.API_VERSION, 
#                 developerKey=self.api_key,
#                 http=http
#             )
#             print("YouTube API 客户端创建成功")
#         except Exception as e:
#             print(f"创建 YouTube API 客户端失败: {str(e)}")
#             raise

#     def search_video(self, keyword, max_results=1):
#         """
#         搜索视频
        
#         Args:
#             keyword (str): 搜索关键词
#             max_results (int): 返回结果数量
            
#         Returns:
#             list: 视频信息列表
#         """
#         try:
#             print(f"正在搜索视频: {keyword}")
#             search_response = self.youtube.search().list(
#                 q=keyword,
#                 part="id,snippet",
#                 maxResults=max_results,
#                 type="video"
#             ).execute()

#             videos = []
#             for search_result in search_response.get("items", []):
#                 if search_result["id"]["kind"] == "youtube#video":
#                     videos.append({
#                         'id': search_result["id"]["videoId"],
#                         'title': search_result["snippet"]["title"],
#                         'url': f"https://www.youtube.com/watch?v={search_result['id']['videoId']}"
#                     })
#             return videos
            
#         except Exception as e:
#             print(f"搜索视频时发生错误: {str(e)}")
#             import traceback
#             print("详细错误信息:")
#             print(traceback.format_exc())
#             return []

class PurePytubefixDownloader:
    """
    只使用pytubefix进行搜索和下载的youtube视频下载器
    """
    def __init__(self, proxy=None):
        self.proxy = proxy
    
    def search_video(self, keyword, max_results=None):
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