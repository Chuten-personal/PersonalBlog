#!/usr/bin/env python3
"""
将 Markdown 文章转换为 HTML 网页
支持 YAML 前置元数据：title, date, summary（可选）
用法：
  python build.py              # 转换 _posts 下所有 md 文件
  python build.py post.md      # 转换指定文件
"""

import os
import re
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    print("请先安装 markdown: pip install markdown")
    sys.exit(1)

# 项目根目录
ROOT = Path(__file__).parent
POSTS_DIR = ROOT / "_posts"
OUTPUT_DIR = ROOT / "articles"
TEMPLATE_PATH = ROOT / "templates" / "article.html"
INDEX_PATH = ROOT / "index.html"


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """解析 YAML frontmatter，返回 (meta, body)"""
    meta = {"title": "未命名", "date": "", "summary": ""}
    body = content

    if content.strip().startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_raw, body = parts[1], parts[2].lstrip("\n")
            for line in fm_raw.strip().split("\n"):
                if ":" in line:
                    key, val = line.split(":", 1)
                    meta[key.strip().lower()] = val.strip().strip("'\"")

    return meta, body


def get_summary(meta: dict, body: str, max_len: int = 100) -> str:
    """获取文章摘要：优先 frontmatter 的 summary，否则取正文首段"""
    if meta.get("summary"):
        return meta["summary"]
    # 取第一段非空文本，去除 markdown 符号
    text = re.sub(r"^#+\s*", "", body)
    text = re.sub(r"\n\n.*", "", text, flags=re.DOTALL)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*_`]", "", text).strip()
    return (text[:max_len] + "…") if len(text) > max_len else text


def md_to_html(md_content: str) -> str:
    """Markdown 转 HTML"""
    return markdown.markdown(
        md_content,
        extensions=["extra", "toc"],  # 表格、脚注、目录
    )


def render_article(meta: dict, html_body: str) -> str:
    """用模板渲染文章页"""
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    return template.replace("{{ title }}", meta["title"]).replace(
        "{{ date }}", meta["date"]
    ).replace("{{ content }}", html_body)


def build_file(md_path: Path) -> dict | None:
    """转换单个 md 文件，返回文章信息 (用于更新首页)"""
    content = md_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(content)
    html_body = md_to_html(body)
    html = render_article(meta, html_body)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = md_path.stem + ".html"
    out_path = OUTPUT_DIR / out_name
    out_path.write_text(html, encoding="utf-8")
    print(f"  [OK] {md_path.name} -> articles/{out_name}")

    return {
        "title": meta["title"],
        "date": meta["date"],
        "summary": get_summary(meta, body),
        "url": f"./articles/{out_name}",
    }


def update_index_html(articles: list[dict]) -> None:
    """将文章列表写入 index.html 的 article-list"""
    if not articles:
        return

    # 按日期倒序（最新在前）
    articles = sorted(articles, key=lambda x: x["date"], reverse=True)

    cards = []
    for a in articles:
        cards.append(
            f'''                    <a href="{a["url"]}" class="article-card">
                        <time>{a["date"]}</time>
                        <h3>{a["title"]}</h3>
                        <p>{a["summary"]}</p>
                    </a>'''
        )
    article_list_html = "\n".join(cards)

    index_content = INDEX_PATH.read_text(encoding="utf-8")
    pattern = r'(<div class="article-list">)\s*.*?\s*(</div>)'
    replacement = r"\1\n" + article_list_html + r"\n                \2"
    new_content = re.sub(pattern, replacement, index_content, flags=re.DOTALL)

    INDEX_PATH.write_text(new_content, encoding="utf-8")
    print(f"  [OK] 已更新 index.html 文章列表 ({len(articles)} 篇)")


def main():
    if len(sys.argv) > 1:
        # 转换指定文件
        paths = [Path(p) for p in sys.argv[1:]]
    else:
        # 转换 _posts 下所有 md
        if not POSTS_DIR.exists():
            POSTS_DIR.mkdir(parents=True)
            sample = POSTS_DIR / "blog-opening.md"
            sample.write_text(
                """---
title: 博客开通啦
date: 2025-02-28
---

这是我的个人博客的第一篇文章。期待在这里与你分享更多内容。""",
                encoding="utf-8",
            )
            print(f"已创建示例文章: {sample}")
        paths = list(POSTS_DIR.glob("*.md"))

    if not paths:
        print("未找到 Markdown 文件")
        return

    print("正在生成文章...")
    articles = []
    for p in sorted(paths):
        if p.suffix.lower() == ".md":
            result = build_file(p)
            if result:
                articles.append(result)

    if articles:
        update_index_html(articles)

    print("完成！")


if __name__ == "__main__":
    main()
