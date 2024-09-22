import os
from PIL import Image, ImageDraw, ImageFont
import argparse
from dataclasses import dataclass


@dataclass
class ImageOptions:
    text: str = "LGTM"
    font_path: str = "arial.ttf"
    font_size: int = 50
    text_x: int = None
    text_y: int = None
    output_path: str = None
    text_color: str = "white"


def add_lgtm_to_image(
    image_path,
    options: ImageOptions,
):
    # 画像を開く
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    # 画像のサイズを取得
    width, height = image.size

    # フォントとサイズを設定
    try:
        font = ImageFont.truetype(options.font_path, options.font_size)
    except IOError:
        print(f"Warning: Font '{options.font_path}' not found. Using default font.")
        font = ImageFont.load_default()

    # テキストのサイズを計算
    bbox = draw.textbbox((0, 0), options.text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # テキストの位置を計算
    text_x = options.text_x if options.text_x is not None else (width - text_width) / 2
    text_y = (
        options.text_y if options.text_y is not None else (height - text_height) / 2
    )

    # テキストを追加（文字色を設定）
    draw.text((text_x, text_y), options.text, font=font, fill=options.text_color)

    # 画像を保存
    output_path = (
        options.output_path
        if options.output_path
        else f"{os.path.splitext(image_path)[0]}_lgtm.jpg"
    )
    image.save(output_path, "JPEG")
    print(
        f"Successfully generated the image with text '{options.text}'. \nOutput path: {output_path}"
    )


if __name__ == "__main__":
    # argparseでコマンドライン引数を解析
    parser = argparse.ArgumentParser(description="Add text 'LGTM' to selected image.")
    parser.add_argument(
        "image_path",
        help="The path to the image file",
    )
    parser.add_argument(
        "--text",
        "-t",
        default="LGTM",
        help="The text to add to the image (default: LGTM)",
    )
    parser.add_argument(
        "--font",
        "-f",
        default="arial.ttf",
        help="The font file to use (default: arial.ttf)",
    )
    parser.add_argument(
        "--size",
        "-s",
        type=int,
        default=50,
        help="The font size of the text (default: 50)",
    )
    parser.add_argument(
        "--x",
        type=int,
        help="The x position of the text (default: center)",
    )
    parser.add_argument(
        "--y",
        type=int,
        help="The y position of the text (default: center)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="The output file path (default: same as input with '_lgtm' suffix)",
    )
    parser.add_argument(
        "--color",
        "-c",
        default="white",
        help="The color of the text (default: white)",
    )

    args = parser.parse_args()

    # ImageOptionsオブジェクトを作成し、引数を設定
    options = ImageOptions(
        text=args.text,
        font_path=args.font,
        font_size=args.size,
        text_x=args.x,
        text_y=args.y,
        output_path=args.output,
        text_color=args.color,
    )

    # メソッドで画像処理
    add_lgtm_to_image(
        args.image_path,
        options,
    )
