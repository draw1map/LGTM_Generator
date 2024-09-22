import os
from PIL import Image, ImageDraw, ImageFont, ImageColor
import argparse
from dataclasses import dataclass
import ast


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
    """文字列として渡された色情報 color をRGB形式に変換"""
    try:
        # RGBタプル形式の場合
        if color_str.startswith("(") and color_str.endswith(")"):
            # 文字列をタプルに変換
            return ast.literal_eval(color_str)
        # 16進数カラーコードの場合
        elif color_str.startswith("#") or color_str.isalpha():
            # カラーコードまたは名前をRGBに変換
            return ImageColor.getrgb(color_str)
        else:
            raise ValueError(f"Invalid color format: {color_str}")
    except Exception as e:
        raise ValueError(f"Invalid color format: {color_str}. Error: {e}")


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
        font = ImageFont.truetype(
            options.font_path,
            options.font_size,
        )
    except IOError:
        print(f"Warning: Font '{options.font_path}' not found. Using default font.")
        font = ImageFont.load_default()

    # テキストのサイズを計算
    bbox = draw.textbbox(
        xy=(0, 0),
        text=options.text,
        font=font,
    )
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # テキストの位置を計算
    text_x = options.text_x if options.text_x is not None else (width - text_width) / 2

    # `--position` オプションに基づいてY座標を計算
    if options.position == "top":
        text_y = 10
    elif options.position == "bottom":
        text_y = height - text_height - 25
    else:
        text_y = (
            options.text_y if options.text_y is not None else (height - text_height) / 2
        )

    # テキストを追加（文字色を設定）
    draw.text(
        xy=(text_x, text_y),
        text=options.text,
        font=font,
        fill=options.text_color,
    )

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
    parser = argparse.ArgumentParser(
        description="Add text 'LGTM' to selected image.",
        usage="%(prog)s image_path [options]",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # 必須の引数(ファイルパス)
    parser.add_argument(
        "image_path",
        help="The path to the image file",
    )

    # テキスト関連のオプション
    parser.add_argument(
        "--text",
        "-t",
        default="LGTM",
        help="The text to add to the image",
    )
    parser.add_argument(
        "--font",
        "-f",
        default="arial.ttf",
        help="The font file to use",
    )
    parser.add_argument(
        "--size",
        "-s",
        type=int,
        default=50,
        help="The font size of the text",
    )
    parser.add_argument(
        "--color",
        "-c",
        default="white",
        help="The color of the text",
    )
    parser.add_argument(
        "--position",
        "-p",
        choices=["top", "bottom", "center"],
        default="center",
        help="Position of the text (top, bottom, center).",
    )

    # テキストの位置指定用のオプション
    parser.add_argument(
        "--x",
        type=int,
        help="The x position of the text",
    )
    parser.add_argument(
        "--y",
        type=int,
        help="The y position of the text",
    )

    # 出力関連のオプション
    parser.add_argument(
        "--output",
        "-o",
        help="The output file path. default output filename is same as input with '_lgtm' suffix.",
    )

    args = parser.parse_args()

    # 色指定をtupleに変換
    text_color = parse_color(args.color)

    # ImageOptionsオブジェクトで引数を設定
    options = ImageOptions(
        text=args.text,
        font_path=args.font,
        font_size=args.size,
        text_color=text_color,
        position=args.position,
        text_x=args.x,
        text_y=args.y,
        output_path=args.output,
    )

    # メソッドで画像処理
    add_lgtm_to_image(
        args.image_path,
        options,
    )
