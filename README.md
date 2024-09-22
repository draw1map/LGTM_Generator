# LGTMジェネレーター（LGTM Generator）

このPythonスクリプトは、指定した画像の中央に「LGTM」(Looks Good To Me)というテキストを追加し、新しい画像としてJPEG形式で保存します。

## 準備

- Python 3.11.9

その他の必要なライブラリは `requirements.txt` からインストールできます。

```bash
pip install -r requirements.txt
```

## 使い方

1. スクリプトと同じディレクトリに画像ファイルを置くか、画像へのパスを指定します。
2. コマンドラインからスクリプトを実行します。

    ```bash
    python generate_lgtm.py <画像ファイルのパス>
    ```

    例:

    ```bash
    python generate_lgtm.py example.jpg
    ```

    このコマンドを実行すると、元の画像に「LGTM」テキストが中央に追加され、`example_lgtm.jpg`という名前で保存されます。

## メモ

- テキスト「LGTM」は画像の中央に自動的に配置されます。
- フォントサイズは画像の高さに比例して設定されます。
- システムにArialフォントがない場合、デフォルトフォントが使用されます。

## 出力例

元の画像:

<img src="sample_black.png" alt="Original Image" width="300"/>


出力されたLGTM画像:

<img src="sample_black_lgtm.jpg" alt="LGTM Image" width="300"/>

