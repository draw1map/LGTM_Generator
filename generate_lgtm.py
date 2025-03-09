import os
from PIL import Image, ImageDraw, ImageFont, ImageColor
import argparse
from dataclasses import dataclass
import re
import ast


@dataclass
class ImageOptions:
    """画像に追加するテキストや位置、サイズなどのオプションを管理するデータクラス"""

    text: str = "LGTM"
    font_path: str = "arial.ttf"
    font_size: str = "50"
    text_color: tuple = (255, 255, 255)
    outline_color: tuple = None
    position: str = "center"
    text_x: str = None
    text_y: str = None
    output_path: str = None
    resize: str = None


def parse_color(color_str: str) -> tuple:
    """色指定を解析し、RGBのタプルに変換する"""
    if not color_str:
        return None

    if color_str.startswith("(") and color_str.endswith(")"):
        try:
            return ast.literal_eval(color_str)
        except (SyntaxError, ValueError):
            raise ValueError(f"無効なRGBカラー形式: {color_str}")

    if color_str.startswith("[") and color_str.endswith("]"):
        try:
            return tuple(ast.literal_eval(color_str))
        except (SyntaxError, ValueError):
            raise ValueError(f"無効なRGBカラー形式: {color_str}")

    try:
        return ImageColor.getrgb(color_str)
    except ValueError:
        raise ValueError(f"無効なカラー形式: {color_str}")


def parse_size(value: str, max_value: int) -> int:
    """フォントサイズを数値または 'pct' 指定で解析し、適用可能なサイズに変換"""
    percent_match = re.match(r"(\d+(?:\.\d+)?)pct", value)
    if percent_match:
        return int(float(percent_match.group(1)) / 100 * max_value)

    try:
        return int(value)
    except ValueError:
        raise ValueError(f"無効なサイズ指定: {value}")


def parse_position(value: str, max_value: int) -> int:
    """座標を数値または 'pct' 指定で解析し、適用可能な座標に変換"""
    if value is None:
        return None

    percent_match = re.match(r"(\d+(?:\.\d+)?)pct", value)
    if percent_match:
        return int(float(percent_match.group(1)) / 100 * max_value)

    try:
        return int(value)
    except ValueError:
        raise ValueError(f"無効な座標指定: {value}")


def parse_resize(value: str, width: int, height: int) -> tuple:
    """リサイズオプションを解析し、新しい (width, height) を計算"""
    if value.endswith("pct"):
        try:
            scale = float(value[:-3]) / 100.0
            return int(width * scale), int(height * scale)
        except ValueError:
            raise ValueError(f"無効なリサイズ指定: {value}")

    size_match = re.match(r"(\d+)x(\d+)", value)
    if size_match:
        return int(size_match.group(1)), int(size_match.group(2))

    raise ValueError(f"無効なリサイズ指定: {value}")


def add_lgtm_to_image(image_path, options: ImageOptions):
    """画像にテキストを追加し、オプションに応じた処理を行う"""
    image = Image.open(image_path)
    width, height = image.size

    # 画像のリサイズ処理
    if options.resize:
        width, height = parse_resize(options.resize, width, height)
        image = image.resize((width, height), Image.LANCZOS)

    draw = ImageDraw.Draw(image)

    # フォントサイズを解析
    font_size = parse_size(options.font_size, height)
    if font_size <= 0 or font_size > height:
        raise ValueError("フォントサイズが大きすぎる、または無効です。")

    # フォントをロード（存在しない場合はデフォルトを使用）
    try:
        font = ImageFont.truetype(options.font_path, font_size)
    except IOError:
        print(
            f"警告: フォント '{options.font_path}' が見つかりません。デフォルトフォントを使用します。"
        )
        font = ImageFont.load_default()

    # テキストのサイズを取得
    bbox = draw.textbbox((0, 0), options.text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # X座標の計算
    text_x = parse_position(options.text_x, width)
    if text_x is not None:
        text_x -= text_width // 2  # テキストの中心を基準に調整
    else:
        text_x = (width - text_width) / 2  # デフォルトは中央配置

    # Y座標の計算
    text_y = parse_position(options.text_y, height)
    if text_y is not None:
        text_y -= text_height // 2  # テキストの中心を基準に調整
    else:
        if options.position == "top":
            text_y = 10
        elif options.position == "bottom":
            text_y = height - text_height - 25
        else:
            text_y = (height - text_height) / 2  # デフォルトは中央配置

    # テキストの範囲外チェック
    if (
        text_x < 0
        or text_x + text_width > width
        or text_y < 0
        or text_y + text_height > height
    ):
        raise ValueError("テキストの位置が画像の範囲外です。")

    # アウトラインの描画
    if options.outline_color:
        outline_offsets = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        for offset in outline_offsets:
            draw.text(
                (text_x + offset[0], text_y + offset[1]),
                options.text,
                font=font,
                fill=options.outline_color,
            )

    # メインテキストを描画
    draw.text((text_x, text_y), options.text, font=font, fill=options.text_color)

    # 画像の保存
    output_path = (
        options.output_path
        if options.output_path
        else f"{os.path.splitext(image_path)[0]}_lgtm.png"
    )
    image.save(output_path)
    print("🚀  LGTMマスターが新たな作品を生み出した！🎉")
    print(f"📁  保存先: {output_path}")


if __name__ == "__main__":
    """ コマンドライン引数を処理し、オプションを設定 """
    parser = argparse.ArgumentParser(
        description="画像にテキストを追加し、位置とサイズを指定可能。"
    )
    parser.add_argument("image_path", help="画像ファイルのパス")
    parser.add_argument("--text", "-t", default="LGTM", help="画像に追加するテキスト")
    parser.add_argument(
        "--font", "-f", default="arial.ttf", help="使用するフォントファイル"
    )
    parser.add_argument(
        "--size", "-s", default="50", help="フォントサイズ (ピクセル または 'pct')"
    )
    parser.add_argument("--color", "-c", default="white", help="テキストの色")
    parser.add_argument("--outline", "-ol", help="テキストのアウトライン色")
    parser.add_argument(
        "--position",
        "-p",
        choices=["top", "bottom", "center"],
        default="center",
        help="テキストの配置位置",
    )
    parser.add_argument("--x", "-x", help="X座標 (ピクセル または 'pct')")
    parser.add_argument("--y", "-y", help="Y座標 (ピクセル または 'pct')")
    parser.add_argument(
        "--resize", "-r", help="リサイズ (ピクセル指定 '800x600' または '150pct')"
    )
    parser.add_argument("--output", "-o", help="出力ファイルのパス")

    args = parser.parse_args()
    options = ImageOptions(
        text=args.text,
        font_path=args.font,
        font_size=args.size,
        text_color=parse_color(args.color),
        outline_color=parse_color(args.outline),
        position=args.position,
        text_x=args.x,
        text_y=args.y,
        output_path=args.output,
        resize=args.resize,
    )
    add_lgtm_to_image(args.image_path, options)
