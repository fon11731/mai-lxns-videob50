from gene_video import create_video_segment, create_full_video, combine_full_video_from_existing_clips
import json
import os
import random
import time
import yaml

FONT_PATH = "./font/SOURCEHANSANSSC-BOLD.OTF"

def start():
    print("#####【mai-genb50视频生成器 - Step2 视频合成】#####")
    # read global_config.yaml file 
    with open("./global_config.yaml", "r", encoding="utf-8") as f:
        global_config = yaml.load(f, Loader=yaml.FullLoader)

    username = global_config["USER_ID"]
    use_all_cache = global_config["USE_ALL_CACHE"]
    video_res = global_config["VIDEO_RES"]
    video_trans_time = global_config["VIDEO_TRANS_TIME"]
    only_generate_clips = global_config["ONLY_GENERATE_CLIPS"]

    video_output_path = f"./videos/{username}"
    if not os.path.exists(video_output_path):
        os.makedirs(video_output_path)

    b50_raw_file = f"./b50_datas/b50_raw_{username}.json"
    b50_data_file = f"./b50_datas/b50_config_{username}.json"
    config_output_file = f"./b50_datas/video_configs_{username}.json"

    # 检查配置文件的完整性
    if not os.path.exists(config_output_file) or not config_output_file:
        print(f"Error: 没有找到配置文件{config_output_file}，请检查预处理步骤是否完成")

    # 读取配置文件
    with open(config_output_file, "r", encoding="utf-8") as f:
        configs = json.load(f)

    # 生成最终视频
    if only_generate_clips:
        print("[INFO] 仅生成视频片段")
        for resource in configs:
            print(f"正在合成视频片段: {resource['id']}")
            clip = create_video_segment(resource, resolution=video_res, font_path=FONT_PATH)
            clip.write_videofile(os.path.join(video_output_path, f"{resource['id']}.mp4"), 
                                 fps=30, codec='h264_nvenc', threads=4, preset='fast', bitrate='5000k')

    else:
        print("[INFO] 合成完整视频，可能需要一段时间")
        try:
            final_video = create_full_video(configs, resolution=video_res, font_path=FONT_PATH, trans_time=video_trans_time)
            final_video.write_videofile(os.path.join(video_output_path, f"{username}_B50.mp4"), 
                                        fps=30, codec='h264_nvenc', threads=4, preset='fast', bitrate='5000k')
        except Exception as e:
            print(f"Error: 合成完整视频时发生异常: {e}")
            return 1
    return 0


def video_generation_test():
    username = "nickbit"

    video_output_path = "./videos/test"
    if not os.path.exists(video_output_path):
        os.makedirs(video_output_path)

    config_output_file = f"./b50_datas/video_configs_{username}.json"
    if not os.path.exists(config_output_file) or not config_output_file:
        print(f"Error: 没有找到配置文件{config_output_file}，请检查预处理步骤是否完成")

    # 读取配置文件
    with open(config_output_file, "r", encoding="utf-8") as f:
        configs = json.load(f)

    main_configs = configs['main'][:1]

    # generate video clips
    for resource in main_configs:
        clip = create_video_segment(resource, resolution=(1920, 1080), font_path=FONT_PATH)
        # clip.write_videofile(os.path.join(video_output_path, f"{resource['id']}.mp4"), fps=30, codec='h264_nvenc', threads=4, preset='fast', bitrate='5000k')
        clip.save_frame(os.path.join(video_output_path, f"{resource['id']}.png"), t=1)

    # generate full video
    # full_video = create_full_video(configs[35:], resolution=(1920, 1080), font_path=FONT_PATH, trans_time=1.5)
    # full_video.write_videofile(os.path.join(video_output_path, f"{username}_B50.mp4"), fps=30, codec='h264_nvenc', threads=4, preset='fast', bitrate='5000k')


def combine_video_test(username):
    print(f"Start: 正在合并{username}的B50视频")
    video_clip_path = f"./videos/{username}"
    video_output_path = f"./videos"
    full_video = combine_full_video_from_existing_clips(video_clip_path, resolution=(1920, 1080), trans_time=1.5)
    full_video.write_videofile(os.path.join(video_output_path, f"{username}_B50.mp4"), fps=30, codec='h264_nvenc', threads=4, preset='fast', bitrate='5000k')

if __name__ == "__main__":
    # start()
    video_generation_test()