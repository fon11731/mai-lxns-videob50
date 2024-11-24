import os
from PIL import Image
import numpy as np
import shutil

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

from moviepy.editor import ImageClip, VideoFileClip, TextClip, CompositeVideoClip

def test_system():
    print("开始系统功能测试...")
    
    # 测试文件夹创建
    if not os.path.exists("videos"):
        os.makedirs("videos")

    # 生成测试视频
    try:
        # 创建底部背景
        bg_image = ImageClip("./images/VideoUnderBase.png").set_duration(5)

        # 创建文字
        txt_clip = TextClip('测试文字', 
                            fontsize=24, 
                            color='white',
                            font="./font/SOURCEHANSANSSC-BOLD.OTF")
        txt_clip = txt_clip.set_duration(5)

        # 视频叠放顺序，从下往上：背景底图，谱面预览，图片（带有透明通道），文字
        composite_clip = CompositeVideoClip([
                bg_image.set_position((0, 0)),
                txt_clip.set_position((0, 0))
            ],
            size=(1920, 1080)
        )

        # 保存视频
        composite_clip.write_videofile("videos/test.mp4", fps=30, codec='h264_nvenc', threads=4, preset='fast', bitrate='5000k')


    except Exception as e:
        print(f"生成测试视频时发生错误: {str(e)}")
        return False

    print("\n系统功能测试完成！")
    return True

if __name__ == "__main__":
    test_system()