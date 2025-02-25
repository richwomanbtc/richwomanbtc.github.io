#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path

import jwt
import requests
import yaml
from dotenv import load_dotenv

# 環境変数のロード
load_dotenv()

# 設定変数
API_KEY = os.getenv("RESEARCHMAP_API_KEY")
API_SECRET = os.getenv("RESEARCHMAP_API_SECRET")
PERMALINK = "kenjikun"  # ResearchMapのパーマリンク
BASE_URL = "https://api.researchmap.jp"
DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_data"
)
CONTENT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_contents"
)


def generate_jwt():
    """JWT認証トークンの生成"""
    now = int(time.time())
    payload = {
        "iss": API_KEY,
        "iat": now,
        "exp": now + 300,  # 5分間有効
    }

    # JWTトークンの生成
    jwt_token = jwt.encode(payload, API_SECRET, algorithm="HS256")
    return jwt_token


def get_access_token(jwt_token):
    """アクセストークンの取得"""
    token_url = f"{BASE_URL}/oauth2/token"

    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": jwt_token,
        "scope": "read public_only researchers",
        "version": "2",
    }

    response = requests.post(token_url, data=data)

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"アクセストークン取得エラー: {response.text}")
        return None


def fetch_researcher_data(access_token):
    """研究者情報の取得"""
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

    # 研究者情報の取得
    researcher_url = f"{BASE_URL}/{PERMALINK}?format=json"
    response = requests.get(researcher_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"研究者情報取得エラー: {response.text}")
        return None


def save_json_data(data):
    """データをJSONファイルに保存"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # 最終更新日時を追加
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    file_path = os.path.join(DATA_DIR, "research_data.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"JSONデータを保存しました: {file_path}")


def convert_to_markdown(data):
    """ResearchMapデータをMarkdownファイルに変換"""
    if not os.path.exists(CONTENT_DIR):
        os.makedirs(CONTENT_DIR)

    # プロフィール情報をMarkdownに変換
    profile_md = generate_profile_markdown(data)
    with open(os.path.join(CONTENT_DIR, "profile.md"), "w", encoding="utf-8") as f:
        f.write(profile_md)

    # 研究キーワードをMarkdownに変換
    keywords_md = generate_keywords_markdown(data)
    with open(
        os.path.join(CONTENT_DIR, "research_keywords.md"), "w", encoding="utf-8"
    ) as f:
        f.write(keywords_md)

    # 論文情報をMarkdownに変換
    papers_md = generate_papers_markdown(data)
    with open(os.path.join(CONTENT_DIR, "papers.md"), "w", encoding="utf-8") as f:
        f.write(papers_md)

    # 書籍情報をMarkdownに変換
    books_md = generate_books_markdown(data)
    with open(os.path.join(CONTENT_DIR, "books.md"), "w", encoding="utf-8") as f:
        f.write(books_md)

    # 発表情報をMarkdownに変換
    presentations_md = generate_presentations_markdown(data)
    with open(
        os.path.join(CONTENT_DIR, "presentations.md"), "w", encoding="utf-8"
    ) as f:
        f.write(presentations_md)

    # プロジェクト情報をMarkdownに変換
    projects_md = generate_projects_markdown(data)
    with open(os.path.join(CONTENT_DIR, "projects.md"), "w", encoding="utf-8") as f:
        f.write(projects_md)

    # 受賞情報をMarkdownに変換
    awards_md = generate_awards_markdown(data)
    with open(os.path.join(CONTENT_DIR, "awards.md"), "w", encoding="utf-8") as f:
        f.write(awards_md)

    # メタデータファイルを作成
    metadata = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "researchmap.jp/kenjikun",
    }
    with open(os.path.join(CONTENT_DIR, "metadata.yml"), "w", encoding="utf-8") as f:
        yaml.dump(metadata, f, allow_unicode=True, default_flow_style=False)

    print(f"Markdownファイルを生成しました: {CONTENT_DIR}")


def generate_profile_markdown(data):
    """プロフィール情報のMarkdownを生成"""
    md = "---\n"
    md += "title: プロフィール\n"
    md += "layout: page\n"
    md += "---\n\n"
    md += "# プロフィール\n\n"

    if "basic" in data and data["basic"]:
        basic = data["basic"]
        if "affiliation_name" in basic and basic["affiliation_name"]:
            md += f"- **所属**: {basic['affiliation_name']}\n"
        if "position" in basic and basic["position"]:
            md += f"- **役職**: {basic['position']}\n"
        if "degree" in basic and basic["degree"]:
            md += f"- **学位**: {basic['degree']}\n"
        if "url" in basic and basic["url"]:
            md += f"- **ウェブサイト**: [{basic['url']}]({basic['url']})\n"
        if "email" in basic and basic["email"]:
            md += f"- **メール**: {basic['email']}\n"
    else:
        md += "プロフィール情報はありません。\n"

    return md


def generate_keywords_markdown(data):
    """研究キーワード情報のMarkdownを生成"""
    md = "---\n"
    md += "title: 研究キーワード\n"
    md += "layout: page\n"
    md += "---\n\n"
    md += "# 研究キーワード\n\n"

    if "research_interests" in data and data["research_interests"]:
        for item in data["research_interests"]:
            md += f"- {item.get('research_interest', '')}\n"
    else:
        md += "研究キーワード情報はありません。\n"

    return md


def generate_papers_markdown(data):
    """論文情報のMarkdownを生成"""
    md = "---\n"
    md += "title: 論文\n"
    md += "layout: page\n"
    md += "---\n\n"
    md += "# 論文\n\n"

    if "published_papers" in data and data["published_papers"]:
        for i, paper in enumerate(data["published_papers"]):
            md += f"## {i+1}. {paper.get('title', '')}\n\n"
            if "authors" in paper and paper["authors"]:
                md += f"**著者**: {paper['authors']}\n\n"
            if "journal_name" in paper and paper["journal_name"]:
                journal = paper["journal_name"]
                if "publication_date" in paper and paper["publication_date"]:
                    journal += f", {paper['publication_date']}"
                md += f"**掲載**: {journal}\n\n"
            if "doi" in paper and paper["doi"]:
                md += f"**DOI**: [{paper['doi']}](https://doi.org/{paper['doi']})\n\n"
            md += "---\n\n"
    else:
        md += "論文情報はありません。\n"

    return md


def generate_books_markdown(data):
    """書籍情報のMarkdownを生成"""
    md = "---\n"
    md += "title: 書籍\n"
    md += "layout: page\n"
    md += "---\n\n"
    md += "# 書籍\n\n"

    if "books_etc" in data and data["books_etc"]:
        for i, book in enumerate(data["books_etc"]):
            md += f"## {i+1}. {book.get('title', '')}\n\n"
            if "authors" in book and book["authors"]:
                md += f"**著者**: {book['authors']}\n\n"
            if "publisher" in book and book["publisher"]:
                publisher = book["publisher"]
                if "publication_date" in book and book["publication_date"]:
                    publisher += f", {book['publication_date']}"
                md += f"**出版**: {publisher}\n\n"
            md += "---\n\n"
    else:
        md += "書籍情報はありません。\n"

    return md


def generate_presentations_markdown(data):
    """発表情報のMarkdownを生成"""
    md = "---\n"
    md += "title: 講演・発表\n"
    md += "layout: page\n"
    md += "---\n\n"
    md += "# 講演・発表\n\n"

    if "presentations" in data and data["presentations"]:
        for i, presentation in enumerate(data["presentations"]):
            md += f"## {i+1}. {presentation.get('title', '')}\n\n"
            if "presenters" in presentation and presentation["presenters"]:
                md += f"**発表者**: {presentation['presenters']}\n\n"
            if "event_name" in presentation and presentation["event_name"]:
                event = presentation["event_name"]
                if "event_date" in presentation and presentation["event_date"]:
                    event += f", {presentation['event_date']}"
                md += f"**イベント**: {event}\n\n"
            md += "---\n\n"
    else:
        md += "発表情報はありません。\n"

    return md


def generate_projects_markdown(data):
    """研究プロジェクト情報のMarkdownを生成"""
    md = "---\n"
    md += "title: 研究プロジェクト\n"
    md += "layout: page\n"
    md += "---\n\n"
    md += "# 研究プロジェクト\n\n"

    if "research_projects" in data and data["research_projects"]:
        for i, project in enumerate(data["research_projects"]):
            md += f"## {i+1}. {project.get('title', '')}\n\n"
            period = ""
            if "start_date" in project and project["start_date"]:
                period += project["start_date"]
            period += " - "
            if "end_date" in project and project["end_date"]:
                period += project["end_date"]
            else:
                period += "現在"
            md += f"**期間**: {period}\n\n"
            if "role" in project and project["role"]:
                md += f"**役割**: {project['role']}\n\n"
            if "description" in project and project["description"]:
                md += f"**説明**:\n\n{project['description']}\n\n"
            md += "---\n\n"
    else:
        md += "研究プロジェクト情報はありません。\n"

    return md


def generate_awards_markdown(data):
    """受賞情報のMarkdownを生成"""
    md = "---\n"
    md += "title: 受賞\n"
    md += "layout: page\n"
    md += "---\n\n"
    md += "# 受賞\n\n"

    if "awards" in data and data["awards"]:
        for i, award in enumerate(data["awards"]):
            md += f"## {i+1}. {award.get('award_name', '')}\n\n"
            if "award_date" in award and award["award_date"]:
                md += f"**受賞日**: {award['award_date']}\n\n"
            if "summary" in award and award["summary"]:
                md += f"**概要**:\n\n{award['summary']}\n\n"
            md += "---\n\n"
    else:
        md += "受賞情報はありません。\n"

    return md


def main():
    """メイン処理"""
    # JWTトークンの生成
    jwt_token = generate_jwt()
    if not jwt_token:
        print("JWTトークン生成に失敗しました")
        return

    # アクセストークンの取得
    access_token = get_access_token(jwt_token)
    if not access_token:
        print("アクセストークン取得に失敗しました")
        return

    # 研究者情報の取得
    researcher_data = fetch_researcher_data(access_token)
    if not researcher_data:
        print("研究者情報取得に失敗しました")
        return

    # JSONデータの保存
    save_json_data(researcher_data)

    # Markdownファイルに変換
    convert_to_markdown(researcher_data)

    print("処理完了")


if __name__ == "__main__":
    main()
