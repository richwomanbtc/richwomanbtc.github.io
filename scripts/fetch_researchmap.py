#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

# 設定変数
PERMALINK = "kenjikun"  # ResearchMapのパーマリンク
BASE_URL = "https://api.researchmap.jp"
DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_data"
)
AUTO_CONTENT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_auto_contents"
)


def fetch_researcher_data():
    """研究者情報の取得"""
    # 研究者情報の取得
    researcher_url = f"{BASE_URL}/{PERMALINK}?format=json"
    response = requests.get(researcher_url)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error: Could not fetch data from researchmap", file=sys.stderr)
        return None


def save_json_data(data):
    """データをJSONファイルに保存"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # 最終更新日時を追加
    now = datetime.utcnow()  # UTCで現在時刻を取得
    update_time = now.strftime("%Y-%m-%d %H:%M")  # フォーマット
    data["last_updated"] = f"{update_time} (UTC)"  # UTC明記

    file_path = os.path.join(DATA_DIR, "research_data.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"JSONデータを保存しました: {file_path}")

    # メタデータYAMLの作成
    metadata_path = os.path.join(AUTO_CONTENT_DIR, "metadata.yml")
    with open(metadata_path, "w", encoding="utf-8") as f:
        f.write(f"last_updated: {data['last_updated']}\n")
        f.write(f"permalink: {PERMALINK}\n")


def convert_to_markdown(data):
    """データをMarkdownに変換して保存"""
    if not os.path.exists(AUTO_CONTENT_DIR):
        os.makedirs(AUTO_CONTENT_DIR)

    # プロフィール情報をMarkdownに変換
    profile_md = generate_profile_markdown(data)
    with open(os.path.join(AUTO_CONTENT_DIR, "profile.md"), "w", encoding="utf-8") as f:
        f.write(profile_md)

    # 研究キーワードをMarkdownに変換
    keywords_md = generate_keywords_markdown(data)
    if keywords_md:  # コンテンツがある場合のみファイルを作成
        with open(
            os.path.join(AUTO_CONTENT_DIR, "research_keywords.md"),
            "w",
            encoding="utf-8",
        ) as f:
            f.write(keywords_md)
    else:
        # コンテンツがない場合、既存のファイルを削除
        keywords_file = os.path.join(AUTO_CONTENT_DIR, "research_keywords.md")
        if os.path.exists(keywords_file):
            os.remove(keywords_file)

    # 論文情報をMarkdownに変換
    papers_md = generate_papers_markdown(data)
    if papers_md:  # コンテンツがある場合のみファイルを作成
        with open(
            os.path.join(AUTO_CONTENT_DIR, "papers.md"), "w", encoding="utf-8"
        ) as f:
            f.write(papers_md)
    else:
        # コンテンツがない場合、既存のファイルを削除
        papers_file = os.path.join(AUTO_CONTENT_DIR, "papers.md")
        if os.path.exists(papers_file):
            os.remove(papers_file)

    # 書籍情報をMarkdownに変換
    books_md = generate_books_markdown(data)
    if books_md:  # 書籍情報がある場合のみファイルを作成
        with open(
            os.path.join(AUTO_CONTENT_DIR, "books.md"), "w", encoding="utf-8"
        ) as f:
            f.write(books_md)
    else:
        # 書籍情報がない場合、既存のファイルを削除
        books_file = os.path.join(AUTO_CONTENT_DIR, "books.md")
        if os.path.exists(books_file):
            os.remove(books_file)

    # 発表情報をMarkdownに変換
    presentations_md = generate_presentations_markdown(data)
    if presentations_md:  # コンテンツがある場合のみファイルを作成
        with open(
            os.path.join(AUTO_CONTENT_DIR, "presentations.md"), "w", encoding="utf-8"
        ) as f:
            f.write(presentations_md)
    else:
        # コンテンツがない場合、既存のファイルを削除
        presentations_file = os.path.join(AUTO_CONTENT_DIR, "presentations.md")
        if os.path.exists(presentations_file):
            os.remove(presentations_file)

    # 研究プロジェクト情報をMarkdownに変換
    projects_md = generate_projects_markdown(data)
    if projects_md:  # コンテンツがある場合のみファイルを作成
        with open(
            os.path.join(AUTO_CONTENT_DIR, "projects.md"), "w", encoding="utf-8"
        ) as f:
            f.write(projects_md)
    else:
        # コンテンツがない場合、既存のファイルを削除
        projects_file = os.path.join(AUTO_CONTENT_DIR, "projects.md")
        if os.path.exists(projects_file):
            os.remove(projects_file)

    # 受賞情報をMarkdownに変換
    awards_md = generate_awards_markdown(data)
    if awards_md:  # コンテンツがある場合のみファイルを作成
        with open(
            os.path.join(AUTO_CONTENT_DIR, "awards.md"), "w", encoding="utf-8"
        ) as f:
            f.write(awards_md)
    else:
        # コンテンツがない場合、既存のファイルを削除
        awards_file = os.path.join(AUTO_CONTENT_DIR, "awards.md")
        if os.path.exists(awards_file):
            os.remove(awards_file)

    print("Markdownファイルを生成しました")


def generate_profile_markdown(data):
    """プロフィール情報のMarkdownを生成"""
    md = "---\n"
    md += "title: Profile\n"
    md += "layout: page\n"
    md += "auto_content: true\n"
    md += "---\n\n"
    md += "# Profile\n\n"

    # 名前は表示しない

    # 学位（英語表記に変換）
    degree_mapping = {
        "博士(理学)": "Ph.D. in Science",
        "博士（理学）": "Ph.D. in Science",
        "博士(工学)": "Ph.D. in Engineering",
        "博士（工学）": "Ph.D. in Engineering",
        "修士(理学)": "Master of Science",
        "修士（理学）": "Master of Science",
        "修士(工学)": "Master of Engineering",
        "修士（工学）": "Master of Engineering",
        "学士(理学)": "Bachelor of Science",
        "学士（理学）": "Bachelor of Science",
    }

    if "degrees" in data and data["degrees"]:
        for degree_info in data["degrees"]:
            if "degree" in degree_info and isinstance(degree_info["degree"], dict):
                degree_ja = degree_info["degree"].get("ja", "")
                degree_en = degree_info["degree"].get("en", "")

                if degree_ja in degree_mapping:
                    degree = degree_mapping[degree_ja]
                elif degree_en:
                    degree = degree_en
                else:
                    degree = degree_ja

                if degree:
                    md += f"**Degree**: {degree}\n\n"
                break  # 最初の学位だけ表示

    # メールアドレスを追加
    md += "**Email**: kenji.kubo [at] weblab.t.u-tokyo.ac.jp\n\n"

    # TwitterアイコンをFontAwesome 5で使用する正しいクラス名に修正
    md += '<div class="social-links">\n'
    md += '  <a href="https://x.com/richwomanbtc" target="_blank" title="Twitter/X"><i class="fab fa-twitter"></i></a>\n'
    md += '  <a href="https://www.youtube.com/@richwomanbtc4675" target="_blank" title="YouTube"><i class="fab fa-youtube"></i></a>\n'
    md += '  <a href="https://github.com/richwomanbtc" target="_blank" title="GitHub"><i class="fab fa-github"></i></a>\n'
    md += "</div>\n\n"

    # 職歴リスト（英語で表示）
    research_exp = None
    if "@graph" in data:
        for item in data["@graph"]:
            if "@type" in item and item["@type"] == "research_experience":
                research_exp = item
                break

    if research_exp and "items" in research_exp:
        md += "## Career\n\n"
        # 日付の新しい順にソート
        sorted_exp = sorted(
            research_exp["items"], key=lambda x: x.get("from_date", ""), reverse=True
        )

        # 企業名の英語対応マッピング
        company_mapping = {
            "株式会社松尾研究所": "Matsuo Institute Inc.",
            "株式会社メルカリ": "Mercari Inc.",
            "大和証券株式会社": "Daiwa Securities Co., Ltd.",
        }

        for exp in sorted_exp:
            if "affiliation" in exp and isinstance(exp["affiliation"], dict):
                # 日本語の組織名を英語に変換
                affiliation_ja = exp["affiliation"].get("ja", "")
                affiliation_en = exp["affiliation"].get("en", "")

                if affiliation_ja in company_mapping:
                    affiliation = company_mapping[affiliation_ja]
                elif affiliation_en:
                    affiliation = affiliation_en
                else:
                    affiliation = affiliation_ja

                # 期間
                period = ""
                if "from_date" in exp and exp["from_date"]:
                    period += exp["from_date"]
                if "to_date" in exp and exp["to_date"]:
                    if exp["to_date"] == "9999":
                        period += " - Present"
                    else:
                        period += f" - {exp['to_date']}"

                # 役職も英語で
                position = ""
                if "job" in exp and isinstance(exp["job"], dict):
                    position = exp["job"].get("en", "") or exp["job"].get("ja", "")

                # 部署も英語で
                section = ""
                if "section" in exp and isinstance(exp["section"], dict):
                    section = exp["section"].get("en", "") or exp["section"].get(
                        "ja", ""
                    )

                if affiliation:
                    md += f"- **{affiliation}**"
                    if section:
                        md += f" {section}"
                    if position:
                        md += f", {position}"
                    if period:
                        md += f" ({period})"
                    md += "\n"

        md += "\n"

    # 学歴セクションを追加
    education = None
    if "@graph" in data:
        for item in data["@graph"]:
            if "@type" in item and item["@type"] == "education":
                education = item
                break

    if education and "items" in education:
        md += "## Education\n\n"
        # 日付の新しい順にソート
        sorted_edu = sorted(
            education["items"], key=lambda x: x.get("from_date", ""), reverse=True
        )

        for edu in sorted_edu:

            # 学校名（英語優先）
            school = ""
            if "affiliation" in edu and isinstance(edu["affiliation"], dict):
                school = edu["affiliation"].get("en", "") or edu["affiliation"].get(
                    "ja", ""
                )

            # 学部/研究科（英語優先）
            department = ""
            if "department" in edu and isinstance(edu["department"], dict):
                department = edu["department"].get("en", "") or edu["department"].get(
                    "ja", ""
                )

            # 課程（英語優先）
            course = ""
            if "course" in edu and isinstance(edu["course"], dict):
                course = edu["course"].get("en", "") or edu["course"].get("ja", "")

            # 期間
            period = ""
            if "from_date" in edu and edu["from_date"]:
                period += edu["from_date"]
            if "to_date" in edu and edu["to_date"]:
                if edu["to_date"] == "9999":
                    period += " - Present"
                else:
                    period += f" - {edu['to_date']}"

            if school:
                md += f"- **{school}**"
                if department:
                    md += f", {department}"
                # if course:
                #     md += f" ({course})"
                if period:
                    md += f" ({period})"
                md += "\n"

        md += "\n"

    return md


def generate_keywords_markdown(data):
    """研究キーワードのMarkdownを生成"""
    md = "---\n"
    md += "title: Research Keywords\n"
    md += "layout: page\n"
    md += "auto_content: true\n"
    md += "---\n\n"
    md += "# Research Keywords\n\n"

    # APIレスポンスの構造に合わせて、@graphフィールド内のresearch_areasを探す
    research_areas = None
    if "@graph" in data:
        for item in data["@graph"]:
            if "@type" in item and item["@type"] == "research_areas":
                research_areas = item
                break

    if research_areas and "items" in research_areas:
        for area in research_areas["items"]:
            # 研究分野
            discipline = None
            if "discipline" in area and isinstance(area["discipline"], dict):
                discipline = area["discipline"].get("ja", "") or area["discipline"].get(
                    "en", ""
                )

            # 研究フィールド
            field = None
            if "research_field" in area and isinstance(area["research_field"], dict):
                field = area["research_field"].get("ja", "") or area[
                    "research_field"
                ].get("en", "")

            if discipline and field:
                md += f"- **{discipline}**: {field}\n"
            elif discipline:
                md += f"- {discipline}\n"
            elif field:
                md += f"- {field}\n"

        md += "\n"
    else:
        md = ""  # コンテンツがない場合は何も表示しない

    return md


def generate_papers_markdown(data):
    """論文情報のMarkdownを生成"""
    md = "---\n"
    md += "title: Publications\n"
    md += "layout: page\n"
    md += "auto_content: true\n"
    md += "---\n\n"
    md += "# Publications\n\n"

    # APIレスポンスの構造に合わせて、@graphフィールド内のpublished_papersを探す
    papers_data = None
    if "@graph" in data:
        for item in data["@graph"]:
            if "@type" in item and item["@type"] == "published_papers":
                papers_data = item
                break

    if papers_data and "items" in papers_data:
        for paper in papers_data["items"]:
            # タイトルの処理
            title = None
            if "paper_title" in paper:
                if isinstance(paper["paper_title"], dict):
                    title = paper["paper_title"].get("ja", "") or paper[
                        "paper_title"
                    ].get("en", "")
                else:
                    title = str(paper["paper_title"])
            elif "title" in paper:
                if isinstance(paper["title"], dict):
                    title = paper["title"].get("ja", "") or paper["title"].get("en", "")
                else:
                    title = str(paper["title"])

            if title:
                # 論文タイプを確認（博士論文かどうか）
                is_thesis = paper.get("published_paper_type", "") == "doctoral_thesis"

                # 査読付き論文のアイコン追加
                is_reviewed = paper.get("referee", False)

                if is_reviewed and is_thesis:
                    md += f"- **{title}** ![Peer Reviewed](https://img.shields.io/badge/Peer-Reviewed-blue) ![Thesis](https://img.shields.io/badge/Doctoral-Thesis-purple)\n"
                elif is_reviewed:
                    md += f"- **{title}** ![Peer Reviewed](https://img.shields.io/badge/Peer-Reviewed-blue)\n"
                elif is_thesis:
                    md += f"- **{title}** ![Thesis](https://img.shields.io/badge/Doctoral-Thesis-purple)\n"
                else:
                    md += f"- **{title}**\n"
            else:
                md += "- **Unknown Title**\n"

            # 著者の処理
            author_names = []
            if "authors" in paper:
                if isinstance(paper["authors"], dict):
                    # 言語ごとの著者リスト {"ja": [...], "en": [...]}
                    for lang, authors_list in paper["authors"].items():
                        if isinstance(authors_list, list):
                            for author in authors_list:
                                if isinstance(author, dict) and "name" in author:
                                    author_names.append(author["name"])
                elif isinstance(paper["authors"], list):
                    # 著者のリスト
                    for author in paper["authors"]:
                        if isinstance(author, dict) and "name" in author:
                            if isinstance(author["name"], dict):
                                author_name = author["name"].get("ja", "") or author[
                                    "name"
                                ].get("en", "")
                            else:
                                author_name = str(author["name"])
                            author_names.append(author_name)
                        elif isinstance(author, str):
                            author_names.append(author)

            if author_names:
                md += f"  {', '.join(author_names)}\n"

            # 掲載誌の処理
            journal = None
            if "publication_name" in paper:
                if isinstance(paper["publication_name"], dict):
                    journal = paper["publication_name"].get("ja", "") or paper[
                        "publication_name"
                    ].get("en", "")
                else:
                    journal = str(paper["publication_name"])
            elif "publication" in paper:
                if isinstance(paper["publication"], dict):
                    journal = paper["publication"].get("ja", "") or paper[
                        "publication"
                    ].get("en", "")
                else:
                    journal = str(paper["publication"])

            if journal:
                md += f"  Journal: {journal}\n"

            # 発行年の処理
            if "publication_date" in paper and paper["publication_date"]:
                year = (
                    paper["publication_date"].split("-")[0]
                    if "-" in paper["publication_date"]
                    else paper["publication_date"]
                )
                md += f"  Year: {year}\n"

            # DOIの処理（リンク付き）
            if (
                "identifiers" in paper
                and "doi" in paper["identifiers"]
                and paper["identifiers"]["doi"]
            ):
                doi = paper["identifiers"]["doi"][0]
                md += f"  DOI: [{doi}](https://doi.org/{doi})\n"
            elif "doi" in paper and paper["doi"]:
                doi = paper["doi"]
                md += f"  DOI: [{doi}](https://doi.org/{doi})\n"

            md += "\n"
    else:
        md = ""  # コンテンツがない場合は何も表示しない

    return md


def generate_books_markdown(data):
    """書籍情報のMarkdownを生成"""
    md = "---\n"
    md += "title: Books\n"
    md += "layout: page\n"
    md += "auto_content: true\n"
    md += "---\n\n"
    md += "# Books\n\n"

    # APIレスポンスの構造に合わせて、@graphフィールド内のbooksを探す
    books_data = None
    if "@graph" in data:
        for item in data["@graph"]:
            if "@type" in item and item["@type"] == "books":
                books_data = item
                break

    if books_data and "items" in books_data and len(books_data["items"]) > 0:
        for book in books_data["items"]:
            # タイトルの処理
            title = None
            if "book_title" in book:
                if isinstance(book["book_title"], dict):
                    title = book["book_title"].get("ja", "") or book["book_title"].get(
                        "en", ""
                    )
                else:
                    title = str(book["book_title"])
            elif "title" in book:
                if isinstance(book["title"], dict):
                    title = book["title"].get("ja", "") or book["title"].get("en", "")
                else:
                    title = str(book["title"])

            if title:
                md += f"- **{title}**\n"
            else:
                md += "- **Unknown Book Title**\n"

            # 著者の処理
            author_names = []
            if "authors" in book:
                if isinstance(book["authors"], dict):
                    # 言語ごとの著者リスト {"ja": [...], "en": [...]}
                    for lang, authors_list in book["authors"].items():
                        if isinstance(authors_list, list):
                            for author in authors_list:
                                if isinstance(author, dict) and "name" in author:
                                    author_names.append(author["name"])
                elif isinstance(book["authors"], list):
                    # 著者のリスト
                    for author in book["authors"]:
                        if isinstance(author, dict) and "name" in author:
                            if isinstance(author["name"], dict):
                                author_name = author["name"].get("ja", "") or author[
                                    "name"
                                ].get("en", "")
                            else:
                                author_name = str(author["name"])
                            author_names.append(author_name)
                        elif isinstance(author, str):
                            author_names.append(author)

            if author_names:
                md += f"  Authors: {', '.join(author_names)}\n"

            # 出版社の処理
            publisher = None
            if "publisher" in book:
                if isinstance(book["publisher"], dict):
                    publisher = book["publisher"].get("ja", "") or book[
                        "publisher"
                    ].get("en", "")
                else:
                    publisher = str(book["publisher"])

            if publisher:
                md += f"  Publisher: {publisher}\n"

            # 発行年の処理
            if "publication_date" in book and book["publication_date"]:
                year = (
                    book["publication_date"].split("-")[0]
                    if "-" in book["publication_date"]
                    else book["publication_date"]
                )
                md += f"  Year: {year}\n"

            # ISBNの処理
            if (
                "identifiers" in book
                and "isbn" in book["identifiers"]
                and book["identifiers"]["isbn"]
            ):
                md += f"  ISBN: {book['identifiers']['isbn'][0]}\n"
            elif "isbn" in book and book["isbn"]:
                md += f"  ISBN: {book['isbn']}\n"

            md += "\n"
    else:
        # 情報がない場合はメッセージを表示しないこととしコンテンツを空にする
        md = ""

    return md


def generate_presentations_markdown(data):
    """発表情報のMarkdownを生成"""
    md = "---\n"
    md += "title: Presentations\n"
    md += "layout: page\n"
    md += "auto_content: true\n"
    md += "---\n\n"
    md += "# Presentations\n\n"

    # APIレスポンスの構造に合わせて、@graphフィールド内のpresentationsを探す
    presentations_data = None
    if "@graph" in data:
        for item in data["@graph"]:
            if "@type" in item and item["@type"] == "presentations":
                presentations_data = item
                break

    if presentations_data and "items" in presentations_data:
        for presentation in presentations_data["items"]:
            # タイトルの処理
            title = None
            if "presentation_title" in presentation:
                if isinstance(presentation["presentation_title"], dict):
                    title = presentation["presentation_title"].get(
                        "ja", ""
                    ) or presentation["presentation_title"].get("en", "")
                else:
                    title = str(presentation["presentation_title"])
            elif "title" in presentation:
                if isinstance(presentation["title"], dict):
                    title = presentation["title"].get("ja", "") or presentation[
                        "title"
                    ].get("en", "")
                else:
                    title = str(presentation["title"])

            if title:
                # 査読ありかどうかを確認
                is_reviewed = presentation.get("referee", False)
                if is_reviewed:
                    md += f"- **{title}** ![Peer Reviewed](https://img.shields.io/badge/Peer-Reviewed-blue)\n"
                else:
                    md += f"- **{title}**\n"
            else:
                md += "- **Unknown Presentation Title**\n"

            # 著者の処理
            author_names = []
            if "presenters" in presentation:
                if isinstance(presentation["presenters"], dict):
                    # 言語ごとの著者リスト {"ja": [...], "en": [...]}
                    for lang, presenters_list in presentation["presenters"].items():
                        if isinstance(presenters_list, list):
                            for presenter in presenters_list:
                                if isinstance(presenter, dict) and "name" in presenter:
                                    author_names.append(presenter["name"])
                elif isinstance(presentation["presenters"], list):
                    # 著者のリスト
                    for presenter in presentation["presenters"]:
                        if isinstance(presenter, dict) and "name" in presenter:
                            if isinstance(presenter["name"], dict):
                                author_name = presenter["name"].get(
                                    "ja", ""
                                ) or presenter["name"].get("en", "")
                            else:
                                author_name = str(presenter["name"])
                            author_names.append(author_name)
                        elif isinstance(presenter, str):
                            author_names.append(presenter)
            elif "authors" in presentation:
                # authorsフィールドの処理（古いAPIかもしれない）
                if isinstance(presentation["authors"], list):
                    for author in presentation["authors"]:
                        if isinstance(author, dict) and "name" in author:
                            if isinstance(author["name"], dict):
                                author_name = author["name"].get("ja", "") or author[
                                    "name"
                                ].get("en", "")
                            else:
                                author_name = str(author["name"])
                            author_names.append(author_name)
                        elif isinstance(author, str):
                            author_names.append(author)

            if author_names:
                md += f" {', '.join(author_names)}\n"

            # 学会名の処理
            conference = None
            if "conference_name" in presentation:
                if isinstance(presentation["conference_name"], dict):
                    conference = presentation["conference_name"].get(
                        "ja", ""
                    ) or presentation["conference_name"].get("en", "")
                else:
                    conference = str(presentation["conference_name"])
            elif "conference" in presentation:
                if isinstance(presentation["conference"], dict):
                    conference = presentation["conference"].get(
                        "ja", ""
                    ) or presentation["conference"].get("en", "")
                else:
                    conference = str(presentation["conference"])

            if conference:
                md += f"  Conference: {conference}\n"

            # 会議詳細情報の追加
            if "meeting" in presentation and presentation["meeting"]:
                md += f"  Meeting: {presentation['meeting']}\n"

            if "event" in presentation and presentation["event"]:
                if isinstance(presentation["event"], dict):
                    event = presentation["event"].get("ja", "") or presentation[
                        "event"
                    ].get("en", "")
                    if event:
                        md += f"  Event: {event}\n"
                else:
                    md += f"  Event: {presentation['event']}\n"

            # 発表年の処理
            if (
                "presentation_date" in presentation
                and presentation["presentation_date"]
            ):
                year = (
                    presentation["presentation_date"].split("-")[0]
                    if "-" in presentation["presentation_date"]
                    else presentation["presentation_date"]
                )
                md += f"  Year: {year}\n"
            elif "year" in presentation and presentation["year"]:
                md += f"  Year: {presentation['year']}\n"

            md += "\n"
    else:
        md = ""  # コンテンツがない場合は何も表示しない

    return md


def generate_projects_markdown(data):
    """研究プロジェクト情報のMarkdownを生成"""
    md = "---\n"
    md += "title: Research Projects\n"
    md += "layout: page\n"
    md += "auto_content: true\n"
    md += "---\n\n"
    md += "# Research Projects\n\n"

    # APIレスポンスの構造に合わせて、@graphフィールド内のcompetitive_fundingsを探す
    projects_data = None
    if "@graph" in data:
        for item in data["@graph"]:
            if "@type" in item and item["@type"] == "competitive_fundings":
                projects_data = item
                break

    if projects_data and "items" in projects_data and len(projects_data["items"]) > 0:
        for project in projects_data["items"]:
            # プロジェクトタイトルの処理
            title = None
            if "research_project_title" in project:
                if isinstance(project["research_project_title"], dict):
                    title = project["research_project_title"].get("ja", "") or project[
                        "research_project_title"
                    ].get("en", "")
                else:
                    title = str(project["research_project_title"])
            elif "title" in project:
                if isinstance(project["title"], dict):
                    title = project["title"].get("ja", "") or project["title"].get(
                        "en", ""
                    )
                else:
                    title = str(project["title"])

            if title:
                md += f"- **{title}**\n"
            else:
                md += "- **Unknown Project Title**\n"

            # 資金制度の処理
            funding_system = None
            if "funding_system" in project:
                if isinstance(project["funding_system"], dict):
                    funding_system = project["funding_system"].get("ja", "") or project[
                        "funding_system"
                    ].get("en", "")
                else:
                    funding_system = str(project["funding_system"])

            if funding_system:
                md += f"  Funding System: {funding_system}\n"

            # 期間の処理
            period = ""
            if "from_date" in project and project["from_date"]:
                period += project["from_date"]
            if "to_date" in project and project["to_date"]:
                if project["to_date"] == "9999":
                    period += " - Present"
                else:
                    period += f" - {project['to_date']}"

            if period:
                md += f"  Period: {period}\n"

            md += "\n"
    else:
        md = ""  # コンテンツがない場合は何も表示しない

    return md


def generate_awards_markdown(data):
    """受賞情報のMarkdownを生成"""
    md = "---\n"
    md += "title: Awards\n"
    md += "layout: page\n"
    md += "auto_content: true\n"
    md += "---\n\n"
    md += "# Awards\n\n"

    # APIレスポンスの構造に合わせて、@graphフィールド内のawardsを探す
    awards_data = None
    if "@graph" in data:
        for item in data["@graph"]:
            if "@type" in item and item["@type"] == "awards":
                awards_data = item
                break

    if awards_data and "items" in awards_data and len(awards_data["items"]) > 0:
        for award in awards_data["items"]:
            # 賞名の処理
            award_name = None
            if "award_name" in award:
                if isinstance(award["award_name"], dict):
                    award_name = award["award_name"].get("ja", "") or award[
                        "award_name"
                    ].get("en", "")
                else:
                    award_name = str(award["award_name"])
            elif "name" in award:
                if isinstance(award["name"], dict):
                    award_name = award["name"].get("ja", "") or award["name"].get(
                        "en", ""
                    )
                else:
                    award_name = str(award["name"])

            if award_name:
                md += f"- **{award_name}**\n"
            else:
                md += "- **Unknown Award**\n"

            # 授与組織の処理
            organization = None
            if "award_organization" in award:
                if isinstance(award["award_organization"], dict):
                    organization = award["award_organization"].get("ja", "") or award[
                        "award_organization"
                    ].get("en", "")
                else:
                    organization = str(award["award_organization"])
            elif "organization" in award:
                if isinstance(award["organization"], dict):
                    organization = award["organization"].get("ja", "") or award[
                        "organization"
                    ].get("en", "")
                else:
                    organization = str(award["organization"])

            if organization:
                md += f"  Organization: {organization}\n"

            # 受賞年の処理
            if "award_date" in award and award["award_date"]:
                year = (
                    award["award_date"].split("-")[0]
                    if "-" in award["award_date"]
                    else award["award_date"]
                )
                md += f"  Year: {year}\n"
            elif "date" in award and award["date"]:
                year = (
                    award["date"].split("-")[0]
                    if "-" in award["date"]
                    else award["date"]
                )
                md += f"  Year: {year}\n"

            md += "\n"
    else:
        md = ""  # コンテンツがない場合は何も表示しない

    return md


def main():
    """メイン処理"""
    # 研究者情報の取得
    researcher_data = fetch_researcher_data()
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
