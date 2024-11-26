import os
from PIL import Image
import numpy as np
import shutil
from moviepy import ImageClip, VideoFileClip, TextClip, CompositeVideoClip

def test_system():
    print("开始系统功能测试...")
    
    # 测试文件夹创建
    if not os.path.exists("videos"):
        os.makedirs("videos")

    # 生成测试视频
    try:
        # 创建底部背景
        bg_image = ImageClip("./images/VideoUnderBase.png").with_duration(5)

        # 创建文字
        txt_clip = TextClip(font="./font/SOURCEHANSANSSC-BOLD.OTF", text="测试文字", font_size=24, color="white")
        txt_clip = txt_clip.with_duration(5)

        # 视频叠放顺序，从下往上：背景底图，谱面预览，图片（带有透明通道），文字
        composite_clip = CompositeVideoClip([
                bg_image.with_position((0, 0)),
                txt_clip.with_position((0, 0))
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