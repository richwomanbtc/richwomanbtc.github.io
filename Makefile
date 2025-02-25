.PHONY: install setup fetch serve clean help

# デフォルトのターゲット
.DEFAULT_GOAL := help

# 必要なディレクトリを作成
DIRS := _data _auto_contents _contents

# ヘルプメッセージ
help:
	@echo "使用可能なコマンド:"
	@echo "  make install    - Poetryと依存関係をインストール"
	@echo "  make setup      - 必要なディレクトリ構造を作成"
	@echo "  make fetch      - ResearchMapからデータを取得（自動コンテンツ生成）"
	@echo "  make serve      - ローカル開発サーバーを起動"
	@echo "  make new_content - 新しい手動コンテンツを作成"
	@echo "  make clean      - 生成されたデータを削除（手動コンテンツは保持）"
	@echo "  make all        - インストール、セットアップ、データ取得を実行"

# Poetryと依存関係のインストール
install:
	@echo "Poetryと依存関係をインストールしています..."
	@command -v poetry >/dev/null 2>&1 || curl -sSL https://install.python-poetry.org | python3 -
	@poetry install
	@echo "インストール完了！"

# 必要なディレクトリ構造の作成
setup:
	@echo "必要なディレクトリを作成しています..."
	@mkdir -p $(DIRS)
	@echo "セットアップ完了！"

# 新しい手動コンテンツの作成
new_content:
	@read -p "コンテンツ名（英語、ファイル名になります）: " name; \
	read -p "タイトル（日本語OK）: " title; \
	echo "---\ntitle: $$title\nlayout: page\nmanual_content: true\n---\n\n# $$title\n\nここにコンテンツを入力してください。" > _contents/$$name.md; \
	echo "新しいコンテンツ '_contents/$$name.md' を作成しました。エディタで編集してください。"

# ResearchMapからデータを取得
fetch:
	@echo "ResearchMapからデータを取得しています..."
	@poetry run python scripts/fetch_researchmap.py
	@echo "データ取得完了！"

# ローカル開発サーバーの起動
serve:
	@echo "ローカル開発サーバーを起動しています..."
	@poetry run python scripts/serve.py

# 生成されたデータの削除（手動コンテンツは残す）
clean:
	@echo "自動生成されたデータを削除しています..."
	@rm -rf _data/* _auto_contents/*
	@echo "クリーンアップ完了！"

# すべての手順を実行
all: install setup fetch
	@echo "すべての準備が完了しました！"
	@echo "サーバーを起動するには 'make serve' を実行してください。"
	@echo "手動コンテンツを追加するには 'make new_content' を実行してください。"

# 既存のMakefileにpoetryを使った依存関係インストールを追加
install:
	poetry install

update-research:
	poetry run python scripts/fetch_researchmap.py

build:
	poetry run python scripts/build_site.py 