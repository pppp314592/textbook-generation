#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""generate-index.py — テーマ一覧からメインページ index.html を自動生成する。

使い方:
    python generate-index.py {作業ディレクトリ} [出力ファイル] [タイトル] [説明]

- 作業ディレクトリ直下で README.md を持つディレクトリを「テーマ」とみなす。
- 各テーマについて README.md・教科書.md・印刷用/教科書.pdf・印刷用/教科書-印刷版.html
  へのリンクを生成する。
- README.md の先頭に「対象読者」「レベル」「進行状況」等の行があれば表示する。
"""

import sys
import os
import re
import html
from datetime import date
from pathlib import Path


def read_first_lines(path, max_lines=40):
    """README.md から指定行数だけ読み、行リストで返す。"""
    try:
        with open(path, encoding="utf-8") as f:
            return [ln.rstrip("\n") for ln in f.readlines()[:max_lines]]
    except (OSError, UnicodeDecodeError):
        return []


def extract_meta(lines):
    """README.md の行から キー: 値 形式（対象読者/レベル/進行状況 等）を抽出する。

    '- 対象読者: xxx' や '対象読者: xxx' の形式に対応。
    """
    meta = {}
    keys = ("対象読者", "対象レベル", "レベル", "進行状況", "想定学習時間")
    for ln in lines:
        m = re.match(r"^\s*-?\s*(対象読者|レベル|進行状況|想定学習時間)\s*[:：]\s*(.+)$", ln)
        if m:
            meta[m.group(1)] = m.group(2).strip()
    return meta


def has_link(path):
    return path.is_file()


def esc(text):
    return html.escape(text)


def main():
    args = sys.argv[1:]
    work_dir = Path(args[0]).resolve() if args else Path(".").resolve()
    out_file = Path(args[1]) if len(args) > 1 else Path(work_dir) / "index.html"
    title = args[2] if len(args) > 2 else work_dir.name
    description = args[3] if len(args) > 3 else "作成した教科書の一覧とダウンロードリンク"

    themes = []
    for child in sorted(work_dir.iterdir()):
        if not child.is_dir():
            continue
        readme = child / "README.md"
        if not readme.is_file():
            continue
        lines = read_first_lines(readme)
        meta = extract_meta(lines)

        links = {}
        candidates = {
            "PDF": ("印刷用/教科書.pdf", child / "印刷用" / "教科書.pdf"),
            "印刷用HTML": ("印刷用/教科書-印刷版.html", child / "印刷用" / "教科書-印刷版.html"),
        }
        for label, (rel, p) in candidates.items():
            if has_link(p):
                links[label] = rel.replace("\\", "/")

        # カードタイトルのリンク先（Pages で閲覧可能な印刷用HTML・PDFを優先）
        primary_rel = None
        for rel in ("印刷用/教科書-印刷版.html", "印刷用/教科書.pdf"):
            if (child / rel).is_file():
                primary_rel = rel
                break

        themes.append({
            "name": child.name,
            "meta": meta,
            "links": links,
            "primary_rel": primary_rel,
        })

    # 有効なテーマが無い場合はエラーで終了
    if not themes:
        print(f"error: {work_dir} 直下に README.md を持つテーマフォルダがありません。", file=sys.stderr)
        sys.exit(1)

    today = date.today().isoformat()

    theme_cards = []
    for t in themes:
        name = esc(t["name"])
        meta_lines = []
        for k, v in t["meta"].items():
            meta_lines.append(f'<span class="meta-item"><b>{esc(k)}</b>: {esc(v)}</span>')
        meta_html = "".join(meta_lines) if meta_lines else ""

        link_html = []
        for label, rel in t["links"].items():
            href = f"{name}/{rel}"
            link_html.append(f'<a class="link-btn" href="{esc(href)}">{esc(label)}</a>')
        links_html = "".join(link_html) if link_html else '<span class="no-link">公開リンクなし</span>'

        if t["primary_rel"]:
            title_href = f'{name}/{t["primary_rel"]}'
        else:
            title_href = "#"
        theme_cards.append(f"""    <section class="card">
      <h2><a href="{esc(title_href)}">{name}</a></h2>
      <div class="meta">{meta_html}</div>
      <div class="links">{links_html}</div>
    </section>""")

    html_doc = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: "Yu Gothic", "Hiragino Kaku Gothic ProN", Meiryo, sans-serif;
          background: #f7f8fa; color: #222; line-height: 1.7; padding: 2rem 1rem; }}
  .container {{ max-width: 900px; margin: 0 auto; }}
  header {{ text-align: center; padding: 2rem 0 2.5rem; }}
  header h1 {{ font-size: 2rem; margin-bottom: .5rem; }}
  header p {{ color: #555; }}
  .date {{ display: block; margin-top: 1rem; color: #888; font-size: .85rem; }}
  .card {{ background: #fff; border: 1px solid #e0e0e0; border-radius: 8px;
          padding: 1.5rem; margin-bottom: 1.25rem; box-shadow: 0 1px 3px rgba(0,0,0,.06); }}
  .card h2 {{ font-size: 1.25rem; margin-bottom: .5rem; }}
  .card h2 a {{ color: #1a5fb4; text-decoration: none; }}
  .card h2 a:hover {{ text-decoration: underline; }}
  .meta {{ margin-bottom: .75rem; }}
  .meta-item {{ display: inline-block; background: #f1f3f5; border-radius: 4px;
                padding: 2px 8px; margin: 2px 4px 2px 0; font-size: .85rem; }}
  .links {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  .link-btn {{ display: inline-block; border: 1px solid #1a5fb4; color: #1a5fb4;
               border-radius: 5px; padding: 4px 12px; font-size: .9rem; text-decoration: none; }}
  .link-btn:hover {{ background: #1a5fb4; color: #fff; }}
  .no-link {{ color: #999; font-size: .9rem; }}
  footer {{ text-align: center; margin-top: 2.5rem; color: #999; font-size: .85rem; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>{esc(title)}</h1>
    <p>{esc(description)}</p>
    <span class="date">作成日: {today}</span>
  </header>

  <main>
    {chr(10).join(theme_cards)}
  </main>

  <footer>
    <p>本サイトは GitHub Pages で公開されています。</p>
  </footer>
</div>
</body>
</html>
"""

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(html_doc, encoding="utf-8")
    print(f"index written: {out_file}")
    print(f"themes: {len(themes)}")
    for t in themes:
        print(f"  - {t['name']}: {', '.join(t['links'].keys())}")


if __name__ == "__main__":
    main()
