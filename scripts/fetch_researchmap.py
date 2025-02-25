def generate_profile_markdown(data):
    """プロフィール情報のMarkdownを生成"""
    md = "---\n"
    md += "title: Profile\n"
    md += "layout: page\n"
    md += "auto_content: true\n"
    md += "---\n\n"
    md += "# Profile\n\n"

    # 名前は表示しない

    # 学位情報 - 英語の値を直接使用
    if "degrees" in data and data["degrees"]:
        for degree_info in data["degrees"]:
            if "degree" in degree_info and isinstance(degree_info["degree"], dict):
                # 英語の学位情報を優先
                degree_en = degree_info["degree"].get("en", "")
                degree_ja = degree_info["degree"].get("ja", "")

                degree = degree_en if degree_en else degree_ja

                if degree:
                    md += f"**Degree**: {degree}\n\n"
                break  # 最初の学位だけ表示

    # メールアドレスを追加
    md += "**Email**: kenji.kubo [at] weblab.t.u-tokyo.ac.jp\n\n"

    # SNSアイコン
    md += '<div class="social-links">\n'
    md += '  <a href="https://x.com/richwomanbtc" target="_blank" title="Twitter/X"><i class="fab fa-twitter"></i></a>\n'
    md += '  <a href="https://www.youtube.com/@richwomanbtc4675" target="_blank" title="YouTube"><i class="fab fa-youtube"></i></a>\n'
    md += '  <a href="https://github.com/richwomanbtc" target="_blank" title="GitHub"><i class="fab fa-github"></i></a>\n'
    md += "</div>\n\n"

    # 職歴リスト - 英語表記を直接使用
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

        for exp in sorted_exp:
            if "affiliation" in exp and isinstance(exp["affiliation"], dict):
                # 英語の組織名を優先して使用 (変換マッピングは使用しない)
                affiliation_en = exp["affiliation"].get("en", "")
                affiliation_ja = exp["affiliation"].get("ja", "")

                affiliation = affiliation_en if affiliation_en else affiliation_ja

                # 期間
                period = ""
                if "from_date" in exp and exp["from_date"]:
                    period += exp["from_date"]
                if "to_date" in exp and exp["to_date"]:
                    if exp["to_date"] == "9999":
                        period += " - Present"
                    else:
                        period += f" - {exp['to_date']}"

                # 役職も英語を優先
                position = ""
                if "job" in exp and isinstance(exp["job"], dict):
                    position = exp["job"].get("en", "") or exp["job"].get("ja", "")

                # 部署も英語を優先
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

    # 学歴情報 - 英語表記を直接使用
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
            if "school" in edu and isinstance(edu["school"], dict):
                school = edu["school"].get("en", "") or edu["school"].get("ja", "")

            # 学部/研究科（英語優先）
            faculty = ""
            if "faculty" in edu and isinstance(edu["faculty"], dict):
                faculty = edu["faculty"].get("en", "") or edu["faculty"].get("ja", "")

            # 学科/専攻（英語優先）
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
                if faculty:
                    md += f", {faculty}"
                if department:
                    md += f", {department}"
                if course:
                    md += f" ({course})"
                if period:
                    md += f" {period}"
                md += "\n"

        md += "\n"

    return md
