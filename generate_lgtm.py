import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageColor
import argparse
from dataclasses import dataclass

SETTINGS_FILE = "settings.json"


def load_settings():
    """設定ファイル (settings.json) から設定を読み込む"""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@dataclass
class ImageOptions:
    text: str = "LGTM"
    font_path: str = "arial.ttf"
    font_size: int = 50
    text_color: tuple = (255, 255, 255)
    position: str = "center"
    text_x: int = None
    text_y: int = None
    output_path: str = None


def parse_color(color_str: str) -> tuple:
    """文字列の色指定をRGBタプルに変換"""
    try:
        return ImageColor.getrgb(color_str)
    except ValueError:
        raise ValueError(f"Invalid color format: {color_str}")


def add_lgtm_to_image(
    image_path,
    options: ImageOptions,
):
    # 画像を開く
    output_extension = os.path.splitext(image_path)[1].lower()
    image = Image.open(image_path).convert(
        "RGBA" if output_extension == ".png" else "RGB"
    )
    draw = ImageDraw.Draw(image)

    # 画像のサイズを取得
    width, height = image.size

    # フォントとサイズを設定
    try:
        font = ImageFont.truetype(options.font_path, options.font_size)
    except IOError:
        print(f"Warning: Font '{options.font_path}' not found. Using default font.")
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), options.text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    text_x = options.text_x if options.text_x is not None else (width - text_width) / 2
    text_y = (
        options.text_y
        if options.text_y is not None
        else (
            10
            if options.position == "top"
            else height - text_height - 25
            if options.position == "bottom"
            else (height - text_height) / 2
        )
    )

    draw.text((text_x, text_y), options.text, font=font, fill=options.text_color)

    # 画像を保存
    output_path = (
        options.output_path
        or f"{os.path.splitext(image_path)[0]}_lgtm{output_extension}"
    )
    image.save(output_path, "PNG" if output_extension == ".png" else "JPEG", quality=95)

    print(f"Image saved at {output_path}")


if __name__ == "__main__":
    # コマンドライン引数を受け取る
    parser = argparse.ArgumentParser(description="Add text 'LGTM' to an image.")
    parser.add_argument("image_path", help="Path to the image file")
    parser.add_argument("--text", "-t", help="Text to add")
    parser.add_argument("--font", "-f", help="Font file")
    parser.add_argument("--size", "-s", type=int, help="Font size")
    parser.add_argument("--color", "-c", help="Text color")
    parser.add_argument(
        "--position", "-p", choices=["top", "bottom", "center"], help="Text position"
    )
    parser.add_argument("--x", type=int, help="Text X position")
    parser.add_argument("--y", type=int, help="Text Y position")
    parser.add_argument("--output", "-o", help="Output file path")
    args = parser.parse_args()

    # settings.json から設定を読み込む
    settings = load_settings()
    options = ImageOptions(
        text=args.text or settings.get("text", "LGTM"),
        font_path=args.font or settings.get("font_path", "arial.ttf"),
        font_size=args.size or settings.get("font_size", 50),
        text_color=parse_color(args.color)
        if args.color
        else parse_color(settings.get("text_color", "white")),
        position=args.position or settings.get("position", "center"),
        text_x=args.x if args.x is not None else settings.get("text_x"),
        text_y=args.y if args.y is not None else settings.get("text_y"),
        output_path=args.output or settings.get("output_path"),
    )
    add_lgtm_to_image(args.image_path, options)
