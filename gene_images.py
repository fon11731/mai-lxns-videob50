import os
import json
from PIL import Image, ImageDraw, ImageFont
from utils.Utils import Utils
import requests


def get_b50_data_from_fish(username):
    url = "https://www.diving-fish.com/api/maimaidxprober/query/player"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Content-Type": "application/json"
    }
    payload = {
        "username": username,
        "b50": "1"
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 400:
        return {"error": "No such user"}
    elif response.status_code == 403:
        return {"error": "User has set privacy or not agreed to the user agreement"}
    else:
        return {"error": f"Failed to get data, status code: {response.status_code}"}


def generate_b50_images(UserID, b35_data, b15_data, output_dir):
    Function = Utils()
    print("生成B50图片中...")
    os.makedirs(output_dir, exist_ok=True)

    for __index, __record_detail in enumerate(b35_data):
        with Image.open("./images/B50ViedoBase.png") as Background:
            SigleImage = Function.GenerateOneAchievement(__record_detail)
            NewSize = (int(SigleImage.width * 0.55), int(SigleImage.height * 0.55))
            SigleImage = SigleImage.resize(NewSize, Image.LANCZOS)

            Background.paste(SigleImage, (940, 170), SigleImage.convert("RGBA"))

            Draw = ImageDraw.Draw(Background)
            FontPath = "./font/FOT_NewRodin_Pro_EB.otf"
            FontSize = 50
            FontColor = (255, 255, 255)
            Font = ImageFont.truetype(FontPath, FontSize)
            TextPosition = (940, 100)
            Draw.text(TextPosition, f"PastBest {__index + 1}", fill=FontColor, font=Font)

            Background.save(f"./b50_images/{UserID}/PastBest_{__index + 1}.png")

    for __index, __record_detail in enumerate(b15_data):
        with Image.open("./images/B50ViedoBase.png") as Background:
            SigleImage = Function.GenerateOneAchievement(__record_detail)
            NewSize = (int(SigleImage.width * 0.55), int(SigleImage.height * 0.55))
            SigleImage = SigleImage.resize(NewSize, Image.LANCZOS)

            Background.paste(SigleImage, (940, 170), SigleImage.convert("RGBA"))

            Draw = ImageDraw.Draw(Background)
            FontPath = "./font/FOT_NewRodin_Pro_EB.otf"
            FontSize = 50
            FontColor = (255, 255, 255)
            Font = ImageFont.truetype(FontPath, FontSize)
            TextPosition = (940, 100)
            Draw.text(TextPosition, f"NewBest {__index + 1}", fill=FontColor, font=Font)

            Background.save(f"./b50_images/{UserID}/NewBest_{__index + 1}.png")

    print(f"已生成 {UserID} 的 B50 图片，请在 b50_images/{UserID} 文件夹中查看。")


