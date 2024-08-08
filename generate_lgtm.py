import os
from PIL import Image, ImageDraw, ImageFont
import sys


def add_lgtm_to_image(image_path):
    # 画像を開く
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    # 画像のサイズを取得
    width, height = image.size

    # フォントとサイズを設定
    # 画像の高さの20%の大きさ
    font_size = int(height / 5)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # テキストのサイズを計算
    text = "LGTM"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # テキストの位置を計算（中央に配置）
    text_x = (width - text_width) / 2
    text_y = (height - text_height) / 2

    # テキストを追加
    draw.text((text_x, text_y), text, font=font, fill="white")

    # JPEGで保存
    file_name, _ = os.path.splitext(image_path)
    output_path = f"{file_name}_lgtm.jpg"

    # 画像を保存
    image.save(output_path, "JPEG")
    print(f"Successfully generated the LGTM image. : {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("command: python generate_lgtm.py <image_path>")
    else:
        add_lgtm_to_image(sys.argv[1])
