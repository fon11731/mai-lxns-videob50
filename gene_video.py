import os
import shutil
import numpy as np
from PIL import Image

def get_imagemagick_binary():
    if os.name == 'nt':  # Windows
        # 使用 shutil 查找可执行文件的完整路径
        magick_path = shutil.which('magick')
        if not magick_path:
            # 如果在 PATH 中找不到，尝试常见的安装路径
            common_paths = [
                r"C:\Program Files\ImageMagick-7.1.1-Q16\magick.exe",
                r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe",
            ]
            for path in common_paths:
                if os.path.exists(path):
                    return path
            raise FileNotFoundError("ImageMagick not found. Please install it and add to PATH")
        return magick_path
    else:  # Linux/Mac
        convert_path = shutil.which('convert')
        if not convert_path:
            raise FileNotFoundError("ImageMagick not found. Please install it and add to PATH")
        return convert_path
    
# 设置ImageMagick路径，请确保在运行前安装ImageMagick了并勾选了添加到环境变量
assert os.path.exists(get_imagemagick_binary())
os.environ['IMAGEMAGICK_BINARY'] = get_imagemagick_binary()

# 如果环境变量不起作用，手动指定ImageMagick的可执行文件路径：
# from moviepy.config import change_settings
# change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

from moviepy.editor import ImageClip, VideoFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, CompositeAudioClip
import json


def load_resources(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
    return data


def create_blank_image(width, height, color=(0, 0, 0, 0)):
    """创建一个透明的图片"""
    # 创建一个RGBA模式的空白图片
    image = Image.new('RGBA', (width, height), color)
    # 转换为numpy数组，moviepy需要这种格式
    return np.array(image)


def create_video_segment(resource, resolution, font_path, text_size=28):
    print(f"正在合成视频片段: {resource['id']}")
    
    # 创建底部背景
    bg_image = ImageClip("./images/VideoUnderBase.png").set_duration(resource['duration'])
    
    # 检查背景图片是否存在
    if 'background' in resource and os.path.exists(resource['background']):
        main_image = ImageClip(resource['background']).set_duration(resource['duration'])
    else:
        print(f"Video Generator Warning:{resource['id']} 没有对应的图片, 请检查本地资源")
        main_image = ImageClip(create_blank_image(resolution[0], resolution[1])).set_duration(resource['duration'])

    # 检查视频是否存在
    if 'video' in resource and os.path.exists(resource['video']):
        video_clip = VideoFileClip(resource['video']).subclip(resource['start'], resource['end'])
        # 将视频预览等比例地缩放
        video_clip = video_clip.resize(height=540/1080 * resolution[1], width=540/1080 * resolution[0])
        
        # 裁剪成正方形
        video_height = video_clip.h
        video_width = video_clip.w
        x_center = video_width / 2
        crop_size = video_height
        x1 = x_center - (crop_size / 2)
        x2 = x_center + (crop_size / 2)
        video_clip = video_clip.crop(x1=x1, y1=0, x2=x2, y2=video_height)
    else:
        print(f"Video Generator Warning:{resource['id']} 没有对应的视频, 请检查本地资源")
        # 创建一个透明的视频片段
        blank_frame = create_blank_image(
            int(540/1080 * resolution[1]),  # 使用相同的尺寸计算
            int(540/1080 * resolution[1])   # 正方形，所以宽高相同
        )
        video_clip = ImageClip(blank_frame).set_duration(resource['duration'])

    # 计算位置
    video_pos = (int(0.092 * resolution[0]), int(0.328 * resolution[1]))
    text_pos = (int(0.56 * resolution[0]), int(0.56 * resolution[1]))

    # 创建文字
    txt_clip = TextClip(resource['text'], fontsize=text_size, color='white', font=font_path)
    txt_clip = txt_clip.set_duration(resource['duration'])

    # 视频叠放顺序，从下往上：背景底图，谱面预览，图片（带有透明通道），文字
    composite_clip = CompositeVideoClip([
            bg_image.set_position((0, 0)),
            video_clip.set_position((video_pos[0], video_pos[1])),
            main_image.set_position((0, 0)),
            txt_clip.set_position((text_pos[0], text_pos[1]))
        ],
        size=resolution
    )

    return composite_clip.set_duration(resource['duration'])


def normalize_audio_volume(clip, target_dbfs=-20):
    """均衡化音频响度到指定的分贝值"""
    if clip.audio is None:
        return clip
    
    try:
        # 获取音频数据
        audio = clip.audio
        
        # 采样音频的多个点来计算平均音量
        sample_times = np.linspace(0, clip.duration, num=100)
        samples = []
        
        for t in sample_times:
            frame = audio.get_frame(t)
            if isinstance(frame, (list, tuple, np.ndarray)):
                samples.append(np.array(frame))
        
        if not samples:
            return clip
            
        # 将样本堆叠成数组
        audio_array = np.stack(samples)
        
        # 计算当前音频的均方根值
        current_rms = np.sqrt(np.mean(audio_array**2))
        
        # 计算需要的增益
        target_rms = 10**(target_dbfs/20)
        gain = target_rms / (current_rms + 1e-8)  # 添加小值避免除零
        
        # 限制增益范围，避免过度放大或减弱
        gain = np.clip(gain, 0.1, 3.0)
        
        # print(f"Applying volume gain: {gain:.2f}")
        
        # 应用音量调整
        return clip.volumex(gain)
    except Exception as e:
        print(f"Warning: Audio normalization failed - {str(e)}")
        return clip


def create_full_video(resources, resolution, font_path, trans_time=1, transition=None):
    clips = []

    for resource in resources:
        clip = create_video_segment(resource, resolution, font_path)
        # 对视频片段进行音频响度均衡化
        clip = normalize_audio_volume(clip)
        
        if len(clips) == 0:
            clips.append(clip)
        else:
            # 为前一个片段添加音频渐出效果
            clips[-1] = clips[-1].audio_fadeout(trans_time)
            # 为当前片段添加音频渐入效果和视频渐入效果
            current_clip = clip.audio_fadein(trans_time).crossfadein(trans_time)
            # 设置片段开始时间
            clips.append(current_clip.set_start(clips[-1].end - trans_time))

    final_video = CompositeVideoClip(clips, size=resolution)
    return final_video

def sort_video_files(files):
    """
    对视频文件名进行排序，
    排序规则：NewBest_15到NewBest_1，然后是PastBest_35到PastBest_1
    """
    def get_sort_key(filename):
        # 移除文件扩展名
        name = os.path.splitext(filename)[0]
        try:
            if name.startswith('NewBest_'):
                number = int(name.replace('NewBest_', ''))
                if 1 <= number <= 15:  # 只处理1-15的编号
                    return (1, number)
            elif name.startswith('PastBest_'):
                number = int(name.replace('PastBest_', ''))
                if 1 <= number <= 35:  # 只处理1-35的编号
                    return (0, number)
        except ValueError:
            pass
        return None  
    
    # 过滤并排序文件
    valid_files = []
    for file in files:
        sort_key = get_sort_key(file)
        if sort_key is not None:  # 只保留有效的文件
            valid_files.append((file, sort_key))
    
    # 根据排序键排序并返回文件名列表
    sorted_files = sorted(valid_files, key=lambda x: x[1], reverse=True)
    return [f[0] for f in sorted_files]  # 只返回文件名列表

def combine_full_video_from_existing_clips(video_clip_path, resolution, trans_time=1):
    clips = []

    video_files = [f for f in os.listdir(video_clip_path) if f.endswith(".mp4")]
    sorted_files = sort_video_files(video_files)
    
    print(f"Sorted files: {sorted_files}")

    if not sorted_files:
        raise ValueError("Error: 没有有效的视频片段文件！(NewBest_1-15 or PastBest_1-35)")

    for file in sorted_files:
        clip = VideoFileClip(os.path.join(video_clip_path, file))
        clip = normalize_audio_volume(clip)
        
        if len(clips) == 0:
            clips.append(clip)
        else:
            # 为前一个片段添加音频渐出效果
            clips[-1] = clips[-1].audio_fadeout(trans_time)
            # 为当前片段添加音频渐入效果和视频渐入效果
            current_clip = clip.audio_fadein(trans_time).crossfadein(trans_time)
            # 设置片段开始时间
            clips.append(current_clip.set_start(clips[-1].end - trans_time))

    final_video = CompositeVideoClip(clips, size=resolution)
    return final_video


if __name__ == "__main__":
    # gene_resource_config("./b50_images/nickbit", "./videos", "./b50_datas/video_configs.json")
    # Example usage
    json_file = "./b50_datas/video_configs.json"
    final_video = create_full_video(json_file, resolution=(1280, 720), text_position='center', clip_position=(100, 100),
                                    transition='compose')
    final_video.write_videofile('./videos/output.mp4', fps=24, codec='h264_nvenc', threads=4, preset='fast', bitrate='5000k')

