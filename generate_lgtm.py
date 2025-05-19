import os
from PIL import Image, ImageDraw, ImageFont, ImageColor
import argparse
from dataclasses import dataclass
import re
import ast
import sys
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class ImageOptions:
    """画像に追加するテキストや位置、サイズなどのオプションを管理するデータクラス"""

    text: str = "LGTM"
    font_path: str = "arial.ttf"
    font_size: str = "50"
    text_color: tuple = (255, 255, 255)
    outline_color: tuple = None
    outline_width: int = 2
    position: str = "center"
    text_x: str = None
    text_y: str = None
    output_path: str = None
    resize: str = None


def validate_image_path(image_path: str) -> None:
    """画像ファイルの存在と形式を確認"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"画像ファイルが見つかりません: {image_path}")

    try:
        with Image.open(image_path) as img:
            img.verify()
    except Exception as e:
        raise ValueError(f"無効な画像ファイルです: {image_path} - {str(e)}")


def validate_output_path(output_path: str) -> None:
    """出力先のディレクトリが存在することを確認"""
    if output_path:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                raise OSError(
                    f"出力ディレクトリの作成に失敗しました: {output_dir} - {str(e)}"
                )


def get_default_font() -> str:
    """OSに応じたデフォルトフォントを返す"""
    if sys.platform == "win32":
        return "arial.ttf"
    elif sys.platform == "darwin":
        return "/System/Library/Fonts/Helvetica.ttc"
    else:
        return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def parse_color(color_str: str) -> tuple:
    """色指定を解析し、RGBのタプルに変換する"""
    if not color_str:
        return None

    try:
        if color_str.startswith("(") and color_str.endswith(")"):
            color = ast.literal_eval(color_str)
        elif color_str.startswith("[") and color_str.endswith("]"):
            color = tuple(ast.literal_eval(color_str))
        else:
            color = ImageColor.getrgb(color_str)

        # RGB値の範囲チェック
        if len(color) != 3:
            raise ValueError(f"RGB値は3つの要素が必要です: {color_str}")

        for value in color:
            if not isinstance(value, int) or value < 0 or value > 255:
                raise ValueError(
                    f"RGB値は0から255の間である必要があります: {color_str}"
                )

        return color
    except (SyntaxError, ValueError) as e:
        raise ValueError(f"無効なカラー形式: {color_str} - {str(e)}")


def parse_size(value: str, max_value: int) -> int:
    """フォントサイズを数値または 'pct' 指定で解析し、適用可能なサイズに変換"""
    try:
        percent_match = re.match(r"(-?\d+(?:\.\d+)?)pct", value)
        if percent_match:
            percentage = float(percent_match.group(1))
            if percentage <= 0:
                raise ValueError("パーセンテージは0より大きい値である必要があります")
            return int(percentage / 100 * max_value)

        size = int(value)
        if size <= 0:
            raise ValueError("サイズは0より大きい値である必要があります")
        return size
    except ValueError as e:
        raise ValueError(f"無効なサイズ指定: {value} - {str(e)}")


def parse_position(value: str, max_value: int) -> int:
    """座標を数値または 'pct' 指定で解析し、適用可能な座標に変換"""
    if value is None:
        return None

    try:
        percent_match = re.match(r"(-?\d+(?:\.\d+)?)pct", value)
        if percent_match:
            percentage = float(percent_match.group(1))
            # パーセンテージを0-100の範囲に正規化
            percentage = max(0, min(100, percentage))
            return int(percentage / 100 * max_value)

        pos = int(value)
        # 座標を0-max_valueの範囲に正規化
        return max(0, min(max_value, pos))
    except ValueError as e:
        raise ValueError(f"無効な座標指定: {value} - {str(e)}")


def parse_resize(value: str, width: int, height: int) -> tuple:
    """リサイズオプションを解析し、新しい (width, height) を計算"""
    try:
        if value.endswith("pct"):
            scale = float(value[:-3]) / 100.0
            if scale <= 0:
                raise ValueError("スケールは0より大きい値である必要があります")
            new_width = int(width * scale)
            new_height = int(height * scale)
        else:
            size_match = re.match(r"(\d+)x(\d+)", value)
            if not size_match:
                raise ValueError(f"無効なリサイズ指定: {value}")

            new_width = int(size_match.group(1))
            new_height = int(size_match.group(2))

        # 最小サイズのチェック
        if new_width < 10 or new_height < 10:
            raise ValueError("リサイズ後のサイズが小さすぎます（最小10x10）")

        # 最大サイズのチェック（メモリ使用量の制限）
        max_size = 10000
        if new_width > max_size or new_height > max_size:
            raise ValueError(
                f"リサイズ後のサイズが大きすぎます（最大{max_size}x{max_size}）"
            )

        # アスペクト比の保持
        aspect_ratio = width / height
        if abs((new_width / new_height) - aspect_ratio) > 0.1:
            logger.warning("リサイズによりアスペクト比が変更されます")

        return new_width, new_height

    except ValueError as e:
        raise ValueError(f"リサイズ指定の解析に失敗しました: {str(e)}")


def add_lgtm_to_image(image_path, options: ImageOptions):
    """画像にテキストを追加し、オプションに応じた処理を行う"""
    try:
        validate_image_path(image_path)
        validate_output_path(options.output_path)

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
            logger.warning(
                f"フォント '{options.font_path}' が見つかりません。デフォルトフォントを使用します。"
            )
            font = ImageFont.truetype(get_default_font(), font_size)

        # テキストのサイズを取得
        bbox = draw.textbbox((0, 0), options.text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # X座標の計算（マージンを考慮）
        margin = 10
        text_x = parse_position(options.text_x, width)
        if text_x is not None:
            text_x = max(
                margin, min(width - text_width - margin, text_x - text_width // 2)
            )
        else:
            text_x = (width - text_width) / 2

        # Y座標の計算（マージンを考慮）
        text_y = parse_position(options.text_y, height)
        if text_y is not None:
            text_y = max(
                margin, min(height - text_height - margin, text_y - text_height // 2)
            )
        else:
            if options.position == "top":
                text_y = parse_position("25pct", height) - text_height // 2
            elif options.position == "bottom":
                text_y = parse_position("75pct", height) - text_height // 2
            else:
                text_y = (height - text_height) / 2

        # アウトラインの描画
        if options.outline_color:
            for x_offset in range(-options.outline_width, options.outline_width + 1):
                for y_offset in range(
                    -options.outline_width, options.outline_width + 1
                ):
                    if x_offset == 0 and y_offset == 0:
                        continue
                    draw.text(
                        (text_x + x_offset, text_y + y_offset),
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

        image.save(output_path, quality=95)
        logger.info("🚀  LGTMマスターが新たな作品を生み出した！🎉")
        logger.info(f"📁  保存先: {output_path}")

    except Exception as e:
        logger.error(f"エラーが発生しました: {str(e)}")
        raise
    finally:
        if "image" in locals():
            image.close()


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
    parser.add_argument("--outline-color", "-oc", help="テキストのアウトライン色")
    parser.add_argument(
        "--outline-width",
        "-ow",
        type=int,
        default=2,
        help="アウトラインの太さ（ピクセル）",
    )
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
        outline_color=parse_color(args.outline_color),
        outline_width=args.outline_width,
        position=args.position,
        text_x=args.x,
        text_y=args.y,
        output_path=args.output,
        resize=args.resize,
    )
    add_lgtm_to_image(args.image_path, options)
