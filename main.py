from gene_images import generate_b50_images, get_b50_data_from_fish
from gene_video import create_video_segment, create_full_video, combine_full_video_from_existing_clips
from utils.video_crawler import PurePytubefixDownloader, download_video
import json
import os
import random
import time

SEARCH_MAX_RESULTS = 3
DOWNLOAD_HIGH_RES = False
USE_IMAGE_CACHE = True
ONLY_GENERATE_CLIPS = False

VIDEO_RES = (1920, 1080)
FONT_PATH = "./font/SOURCEHANSANSSC-BOLD.OTF"
VIDEO_TRANS_TIME = 1.5

def search_b50_videos(b50_data, b50_data_file, proxy=None):
    if proxy:
        downloader = PurePytubefixDownloader(proxy)
    else:
        downloader = PurePytubefixDownloader()

    i = 0
    for song in b50_data:
        i += 1
        # Skip if video info already exists and is not empty
        if 'video_info_match' in song and song['video_info_match']:
            print(f"跳过({i}/50): {song['title']} ，已储存有相关视频信息")
            continue
        title_name = song['title']
        difficulty_name = song['level_label']
        type = song['type']
        if type == "SD":
            keyword = f"{title_name} {difficulty_name} AP【maimaiでらっくす外部出力】"
        else:
            keyword = f"{title_name} DX譜面 {difficulty_name} AP【maimaiでらっくす外部出力】"

        print(f"正在搜索视频({i}/50): {keyword}")
        videos = downloader.search_video(keyword, max_results=SEARCH_MAX_RESULTS)

        if len(videos) == 0:
            print(f"Error: 没有找到{title_name} {difficulty_name}的视频")
            song['video_info_list'] = []
            song['video_info_match'] = {}
            continue

        match_index = 0
        # TODO: 手动匹配
        # for video in videos:
        #     video_title = video['title']
        #     dx_title_match = "DX" in video_title
        #     if type == "SD" and dx_title_match:
        #         print(f"Warning: 疑似SD谱面标题到匹配到DX视频标题: {video_title}")
        #         continue
        #     elif type == "DX" and not dx_title_match:
        #         print(f"Warning: 疑似DX谱面标题没有匹配到DX视频标题: {video_title}")
        #         continue
        #     else:
        #         match_index = videos.index(video)
        #         break
        print(f"匹配结果({i}/50): {videos[match_index]['title']}")

        song['video_info_list'] = videos
        song['video_info_match'] = videos[match_index]

        # 每次搜索后都写入b50_data_file
        with open(b50_data_file, "w", encoding="utf-8") as f:
            json.dump(b50_data, f, ensure_ascii=False, indent=4)
        
        # 等待30-60秒，以减少被检测为bot的风险
        time.sleep(random.randint(30, 60))
    
    return b50_data

def gene_resource_config(b50_data, images_path, videoes_path, ouput_file, random_length=False):
    data = []
    for song in b50_data:
        if not song['clip_id']:
            print(f"Error: 没有找到 {song['title']} {song['level_label']} 的clip_id，请检查数据格式，跳过该片段。")
            continue
        id = song['clip_id']
        __image_path = os.path.join(images_path, id + ".png")
        __image_path = os.path.normpath(__image_path)
        if not os.path.exists(__image_path):
            print(f"Error: 没有找到 {id}.png 图片，请检查本地缓存数据。")
            __image_path = ""

        __video_path = os.path.join(videoes_path, id + ".mp4")
        __video_path = os.path.normpath(__video_path)
        if not os.path.exists(__video_path):
            print(f"Error: 没有找到 {id}.mp4 视频，请检查本地缓存数据。")
            __video_path = ""
        
        if random_length:
            duration = random.randint(10, 12)
            start = random.randint(15, 85)
            end = start + duration
        else:
            # TODO:可配置
            duration = 15
            start = 10
            end = 25

        sub_data = {
            "id": id,
            "background": __image_path,
            "video": __video_path,
            "duration": duration,
            "start": start,
            "end": end,
            "text": "这里本来应该有B50瑞平，但是我懒得写了。"
        }
        data.append(sub_data)

    with open(ouput_file, 'w', encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    return data

def start(username):
    # 创建缓存文件夹
    cache_pathes = [
        f"./b50_datas",
        f"./b50_images",
        f"./videos",
        f"./videos/downloads"
    ]
    for path in cache_pathes:
        if not os.path.exists(path):
            os.makedirs(path)

    # username = input("请输入水鱼用户名：")
    b50_raw_file = f"./b50_datas/b50_raw_{username}.json"
    b50_data_file = f"./b50_datas/b50_config_{username}.json"

    # 检查是否存在已有的b50_data_file
    if os.path.exists(b50_data_file):
        # TODO: 如果已有b50_data_file，对比最新的b50_raw_file，如果b50_raw_file有更新，则更新b50_data_file
        print("[INFO] 检测到已有的b50_data_file，跳过从水鱼获取数据")
        with open(b50_data_file, "r", encoding="utf-8") as f:
            b50_data = json.load(f)
    else:
        print("#####【1/5】从水鱼获取b50数据 #####")
        # 从水鱼获取b50数据
        try:
            fish_data = get_b50_data_from_fish(username)
        except FileNotFoundError:
            print(f"从水鱼获得B50数据失败。")
        except json.JSONDecodeError:
            print("读取 JSON 文件时发生错误，请检查数据格式。")

        charts_data = fish_data['charts']
        user_rating = fish_data['rating']
        user_dan = fish_data['additional_rating']
        b35_data = charts_data['sd']
        b15_data = charts_data['dx']

        # 写入b50_raw_file
        with open(b50_raw_file, "w", encoding="utf-8") as f:
            json.dump(fish_data, f, ensure_ascii=False, indent=4)

        for i in range(len(b35_data)):
            song = b35_data[i]
            song['clip_id'] = f"PastBest_{i + 1}"

        for i in range(len(b15_data)):
            song = b15_data[i]
            song['clip_id'] = f"NewBest_{i + 1}"
        
        # 合并b35_data和b15_data到同一列表
        b50_data = b35_data + b15_data
        # 写入b50_data_file（存档点）
        with open(b50_data_file, "w", encoding="utf-8") as f:
            json.dump(b50_data, f, ensure_ascii=False, indent=4)

    # 搜索b50视频信息，并写入config文件
    print("#####【2/5】搜索b50视频信息 #####")
    proxy = "127.0.0.1:7890"
    try:
        b50_data = search_b50_videos(b50_data, b50_data_file, proxy)
    except Exception as e:
        print(f"Error: 搜索视频信息时发生异常: {e}")
        return -1
    # 写入b50_data_file（存档点）
    with open(b50_data_file, "w", encoding="utf-8") as f:
        json.dump(b50_data, f, ensure_ascii=False, indent=4)

    # 下载谱面确认视频
    print("#####【3/5】下载谱面确认视频 #####")
    video_download_path = f"./videos/downloads/{username}"
    if not os.path.exists(video_download_path):
        os.makedirs(video_download_path)
    i = 0
    for song in b50_data:
        i += 1
        clip_id = song['clip_id']
        
        # Check if video already exists
        video_path = os.path.join(video_download_path, f"{clip_id}.mp4")
        if os.path.exists(video_path):
            print(f"谱面视频已存在({i}/50): {clip_id}")
            continue
            
        print(f"正在下载视频({i}/50): {clip_id}, {song['title']} {song['level_label']}……")
        if 'video_info_match' not in song or not song['video_info_match']:
            print(f"Error: 没有{song['title']} {song['level_label']}的视频信息，Skipping………")
            continue
        video_info = song['video_info_match']
        try:
            download_video(video_info['url'], 
                       output_name=clip_id, 
                           output_path=video_download_path, 
                           high_res=DOWNLOAD_HIGH_RES)
        except Exception as e:
            print(f"Error: 下载视频时发生异常: {e}")
            return -1
        print("\n")

    
    # 生成b50图片
    print("#####【4/5】生成b50背景图片 #####")
    image_output_path = f"./b50_images/{username}"
    if not os.path.exists(image_output_path):
        os.makedirs(image_output_path)
    # check if image_output_path has png files
    if len(os.listdir(image_output_path)) == 0 or not USE_IMAGE_CACHE:
        b35_data = b50_data[:35]
        b15_data = b50_data[35:]
        try:
            generate_b50_images(username, b35_data, b15_data, image_output_path)
        except Exception as e:
            print(f"Error: 生成图片时发生异常: {e}")
            return 1
    else:
        print("[INFO] 检测到已生成的图片，使用缓存图片")

    print("#####【5/5】合成B50视频 #####")
    # 配置视频生成的配置文件
    try:
        configs = gene_resource_config(b50_data, image_output_path, video_download_path, 
                                   f"./b50_datas/video_configs_{username}.json", random_length=True)
    except Exception as e:
        print(f"Error: 生成视频配置时发生异常: {e}")
        return 1
    # TODO：一个web前端可以改变配置和选择视频片段的长度

    # 生成最终视频
    video_output_path = f"./videos/{username}"
    if not os.path.exists(video_output_path):
        os.makedirs(video_output_path)
    if ONLY_GENERATE_CLIPS:
        print("[INFO] 仅生成视频片段")
        for resource in configs:
            print(f"正在合成视频片段: {resource['id']}")
            clip = create_video_segment(resource, resolution=VIDEO_RES, font_path=FONT_PATH)
            clip.write_videofile(os.path.join(video_output_path, f"{resource['id']}.mp4"), fps=30, codec='h264_nvenc', threads=4, preset='fast', bitrate='5000k')

    else:
        print("[INFO] 合成完整视频，可能需要一段时间")
        try:
            final_video = create_full_video(configs, resolution=VIDEO_RES, font_path=FONT_PATH, trans_time=VIDEO_TRANS_TIME)
            final_video.write_videofile(os.path.join(video_output_path, f"{username}_B50.mp4"), fps=30, codec='h264_nvenc', threads=4, preset='fast', bitrate='5000k')
        except Exception as e:
            print(f"Error: 合成完整视频时发生异常: {e}")
            return 1
    return 0


def full_video_generation_test():
    username = "nickbit"
    b50_data_file = f"./b50_datas/b50_config_{username}.json"
    with open(b50_data_file, "r", encoding="utf-8") as f:
        b50_data = json.load(f)
    image_output_path = f"./b50_images/{username}"
    video_download_path = f"./videos/downloads"

    configs = gene_resource_config(b50_data, image_output_path, video_download_path, 
                                f"./b50_datas/video_configs_{username}.json", random_length=True)
    # # read configs file
    # with open("./b50_datas/video_configs_nickbit.json", "r", encoding="utf-8") as f:
    #     configs = json.load(f)

    video_output_path = "./videos/test"
    if not os.path.exists(video_output_path):
        os.makedirs(video_output_path)

    # generate video clips
    # for resource in configs[:2]:
    #     clip = create_video_segment(resource, resolution=VIDEO_RES, font_path=FONT_PATH)
    #     clip.write_videofile(os.path.join(video_output_path, f"{resource['id']}.mp4"), fps=30, codec='h264_nvenc', threads=4, preset='fast', bitrate='5000k')
    
    # generate full video
    full_video = create_full_video(configs[35:], resolution=VIDEO_RES, font_path=FONT_PATH, trans_time=VIDEO_TRANS_TIME)
    full_video.write_videofile(os.path.join(video_output_path, f"{username}_B50.mp4"), fps=30, codec='h264_nvenc', threads=4, preset='fast', bitrate='5000k')


def combine_video_test(username):
    print(f"Start: 正在合并{username}的B50视频")
    video_clip_path = f"./videos/{username}"
    video_output_path = f"./videos"
    full_video = combine_full_video_from_existing_clips(video_clip_path, resolution=VIDEO_RES, trans_time=VIDEO_TRANS_TIME)
    full_video.write_videofile(os.path.join(video_output_path, f"{username}_B50.mp4"), fps=30, codec='h264_nvenc', threads=4, preset='fast', bitrate='5000k')

if __name__ == "__main__":
    # 从 nameid.txt中逐行读取用户名，并调用start函数
    with open("nameid.txt", "r", encoding="utf-8") as f:
        for line in f:
            username = line.strip()
            # print(f"Start: 正在生成{username}的B50视频")
            # result = -1
            # while result == -1:
            #     result = start(username)
            combine_video_test(username)