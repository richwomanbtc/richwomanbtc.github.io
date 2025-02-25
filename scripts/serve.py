#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import webbrowser
from pathlib import Path

from livereload import Server


def main():
    """ローカル開発サーバーを起動"""
    project_root = Path(__file__).parent.parent.absolute()

    # プロジェクトルートに移動
    os.chdir(project_root)

    # サーバーの作成
    server = Server()

    # ウォッチするファイル/ディレクトリの設定
    server.watch("index.html")
    server.watch("assets/css/*.css")
    server.watch("assets/js/*.js")
    server.watch("_auto_contents/*.md")
    server.watch("_contents/*.md")

    # サーバーの起動
    port = 8000
    url = f"http://localhost:{port}"

    print(f"ローカルサーバーを起動します: {url}")
    print(f"プロジェクトルート: {project_root}")
    print("Ctrl+Cで終了します")

    # ブラウザを開く
    webbrowser.open(url)

    # サーバー実行
    server.serve(port=port, root=project_root)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nサーバーを停止しました")
        sys.exit(0)
