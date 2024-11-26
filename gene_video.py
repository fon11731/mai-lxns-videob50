import os
import shutil
import numpy as np
import json
from PIL import Image, ImageFilter
from moviepy import VideoFileClip, ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips, CompositeAudioClip

def create_blank_image(width, height, color=(0, 0, 0, 0)):
    """创建一个透明的图片"""
    # 创建一个RGBA模式的空白图片
    image = Image.new('RGBA', (width, height), color)
    # 转换为numpy数组，moviepy需要这种格式
    return np.array(image)


def create_info_segment(clip_config, resolution, font_path, text_size=28):
    pass


def blur_image(image_path, blur_radius=5):
    """
    对图片进行高斯模糊处理
    
    Args:
        image_path (str): 图片路径
        blur_radius (int): 模糊半径，默认为10
        
    Returns:
        numpy.ndarray: 模糊处理后的图片数组
    """
    try:
        pil_image = Image.open(image_path)
        blurred_image = pil_image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        # 将模糊后的图片转换为 numpy 数组
        return np.array(blurred_image)
    except Exception as e:
        print(f"Warning: 图片模糊处理失败 - {str(e)}")
        return np.array(Image.open(image_path))


def create_video_segment(clip_config, resolution, font_path, text_size=28, inline_max_bytes=72):
    print(f"正在合成视频片段: {clip_config['id']}")
    
    # 默认的底部背景
    default_bg_path = "./images/VideoUnderBase.png"
    
    # 检查背景图片是否存在
    if 'main_image' in clip_config and os.path.exists(clip_config['main_image']):
        main_image = ImageClip(clip_config['main_image']).with_duration(clip_config['duration'])
    else:
        print(f"Video Generator Warning: {clip_config['id']} 没有对应的成绩图, 请检查成绩图资源是否已生成")
        main_image = ImageClip(create_blank_image(resolution[0], resolution[1])).with_duration(clip_config['duration'])

    # 读取song_id，并获取预览图jacket
    __musicid = str(clip_config['song_id'])[-4:].zfill(4)
    __jacket_path = f"./images/Jackets/UI_Jacket_00{__musicid}.png"
    if os.path.exists(__jacket_path):
        # 高斯模糊处理图片
        jacket_array = blur_image(__jacket_path, blur_radius=5)
        # 创建 ImageClip
        jacket_image = ImageClip(jacket_array).with_duration(clip_config['duration'])
        # 将jacket图片按视频分辨率宽度等比例缩放，以填充整个背景
        jacket_image = jacket_image.resized(height=resolution[0], width=resolution[0])
    else:
        print(f"Video Generator Warning: {clip_config['id']} 没有找到对应的封面图, 将使用默认背景")
        jacket_image = ImageClip(default_bg_path).with_duration(clip_config['duration'])

    # 检查视频是否存在
    if 'video' in clip_config and os.path.exists(clip_config['video']):
        video_clip = VideoFileClip(clip_config['video']).subclipped(start_time=clip_config['start'], 
                                                                    end_time=clip_config['end'])
        # 将视频预览等比例地缩放
        video_clip = video_clip.resized(height=540/1080 * resolution[1], width=540/1080 * resolution[0])
        
        # 裁剪成正方形
        video_height = video_clip.h
        video_width = video_clip.w
        x_center = video_width / 2
        crop_size = video_height
        x1 = x_center - (crop_size / 2)
        x2 = x_center + (crop_size / 2)
        video_clip = video_clip.cropped(x1=x1, y1=0, x2=x2, y2=video_height)
    else:
        print(f"Video Generator Warning:{clip_config['id']} 没有对应的视频, 请检查本地资源")
        # 创建一个透明的视频片段
        blank_frame = create_blank_image(
            int(540/1080 * resolution[1]),  # 使用相同的尺寸计算
            int(540/1080 * resolution[1])   
        )
        video_clip = ImageClip(blank_frame).with_duration(clip_config['duration'])

    # 计算位置
    video_pos = (int(0.092 * resolution[0]), int(0.328 * resolution[1]))
    text_pos = (int(0.54 * resolution[0]), int(0.54 * resolution[1]))

    # 创建文字
    text_list = get_splited_text(clip_config['text'], text_max_bytes=inline_max_bytes)
    txt_clip = TextClip(font=font_path, text="\n".join(text_list),
                        method = "label",
                        # size=(text_max_width, text_max_height), 
                        font_size=text_size,
                        margin=(20, 20),
                        interline=6.5,
                        vertical_align="top",
                        color="white",
                        duration=clip_config['duration'])

    # 视频叠放顺序，从下往上：背景底图，谱面预览，图片（带有透明通道），文字
    composite_clip = CompositeVideoClip([
            jacket_image.with_position((0, -0.5), relative=True),
            video_clip.with_position((video_pos[0], video_pos[1])),
            main_image.with_position((0, 0)),
            txt_clip.with_position((text_pos[0], text_pos[1]))
        ],
        size=resolution
    )

    return composite_clip.with_duration(clip_config['duration'])


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

    intro_configs = resources['intro']
    ending_configs = resources['ending']
    main_configs = resources['main']

    clips = []

    for clip_config in intro_configs:
        pass

    for clip_config in main_configs:
        clip = create_video_segment(clip_config, resolution, font_path)
        # 对视频片段进行音频响度均衡化
        clip = normalize_audio_volume(clip)
        
        if len(clips) == 0:
            clips.append(clip)
        else:
            # 为前一个片段添加音频渐出效果
            clips[-1] = clips[-1].with_audio_fadeout(trans_time)
            # 为当前片段添加音频渐入效果和视频渐入效果
            current_clip = clip.with_audio_fadein(trans_time).with_crossfadein(trans_time)
            # 设置片段开始时间
            clips.append(current_clip.with_start(clips[-1].end - trans_time))
    
    for clip_config in ending_configs:
        pass

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
            clips[-1] = clips[-1].with_audio_fadeout(trans_time)
            # 为当前片段添加音频渐入效果和视频渐入效果
            current_clip = clip.with_audio_fadein(trans_time).with_crossfadein(trans_time)
            # 设置片段开始时间
            clips.append(current_clip.with_start(clips[-1].end - trans_time))

    final_video = CompositeVideoClip(clips, size=resolution)
    return final_video

def get_splited_text(text, text_max_bytes=60):
    """
    将说明文本按照最大字节数限制切割成多行
    
    Args:
        text (str): 输入文本
        text_max_bytes (int): 每行最大字节数限制（utf-8编码）
        
    Returns:
        str: 按规则切割并用换行符连接的文本
    """
    lines = []
    current_line = ""
    
    # 按现有换行符先分割
    for line in text.split('\n'):
        current_bytes = 0
        current_line = ""
        
        for char in line:
            char_bytes = len(char.encode('utf-8'))
            
            # 如果添加这个字符会超出限制，保存当前行并重新开始
            if current_bytes + char_bytes > text_max_bytes:
                lines.append(current_line)
                current_line = char
                current_bytes = char_bytes
            else:
                current_line += char
                current_bytes += char_bytes
        
        # 处理剩余的字符
        if current_line:
            lines.append(current_line)
    
    return lines

