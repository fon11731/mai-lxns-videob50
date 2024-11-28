import os
import json
from PIL import Image, ImageDraw, ImageFont
from utils.Utils import Utils


def generate_single_image(background_path, record_detail, user_id, prefix, index):
    function = Utils()
    with Image.open(background_path) as background:
        # 生成并调整单个成绩图片
        single_image = function.GenerateOneAchievement(record_detail)
        new_size = (int(single_image.width * 0.55), int(single_image.height * 0.55))
        single_image = single_image.resize(new_size, Image.LANCZOS)
        
        # 粘贴图片
        background.paste(single_image, (940, 170), single_image.convert("RGBA"))
        
        # 添加文字
        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype("./font/FOT_NewRodin_Pro_EB.otf", 50)
        draw.text((940, 100), f"{prefix} {index + 1}", fill=(255, 255, 255), font=font)
        
        # 保存图片
        background.save(f"./b50_images/{user_id}/{prefix}_{index + 1}.png")

def generate_b50_images(UserID, b35_data, b15_data, output_dir):
    print("生成B50图片中...")
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成历史最佳图片
    for index, record_detail in enumerate(b35_data):
        generate_single_image(
            "./images/B50ViedoBase.png",
            record_detail,
            UserID,
            "PastBest",
            index,
        )
    
    # 生成最新最佳图片
    for index, record_detail in enumerate(b15_data):
        generate_single_image(
            "./images/B50ViedoBase.png",
            record_detail,
            UserID,
            "NewBest",
            index,
        )

    print(f"已生成 {UserID} 的 B50 图片，请在 b50_images/{UserID} 文件夹中查看。")


