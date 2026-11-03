#!/usr/bin/env python3
"""LinuC レベル1 教科書の印刷用HTMLとPDFを生成する。

使い方:
    python build.py
    python build.py --no-pdf
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import markdown

BASE = Path(__file__).resolve().parent
SRC = BASE / "教科書.md"
OUT_DIR = BASE / "印刷用"
HTML_OUT = OUT_DIR / "教科書-印刷版.html"
PDF_OUT = OUT_DIR / "教科書.pdf"

TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LinuC レベル1 教科書</title>
<style>
@page {
  size: A4;
  margin: 18mm 15mm 18mm 15mm;
}
@media print {
  body { font-family: "Yu Mincho", "MS Mincho", "Noto Serif JP", serif; font-size: 10.5pt; line-height: 1.7; color: #000; background: #fff; }
  h1 { page-break-before: always; font-size: 20pt; border-bottom: 2px solid #000; padding-bottom: 6px; }
  h1:first-of-type { page-break-before: avoid; }
  h2 { page-break-after: avoid; font-size: 15pt; }
  h2.chapter { page-break-before: always; }
  h3 { page-break-after: avoid; font-size: 12.5pt; }
  table { border-collapse: collapse; width: 100%; page-break-inside: auto; }
  tr { page-break-inside: avoid; }
  th, td { border: 1px solid #000; padding: 4px 8px; font-size: 9.5pt; vertical-align: top; }
  th { background: #eee; }
  pre, code { font-family: Consolas, "Courier New", monospace; font-size: 9pt; white-space: pre-wrap; }
  pre { border: 1px solid #999; padding: 8px; page-break-inside: avoid; background: #fafafa; }
  .pagebreak { page-break-after: always; }
  a { color: #000; text-decoration: none; }
  .back-to-index { display: none !important; }
  .answer-btn { display: none !important; }
  .answer-body, .answer-body[hidden] { display: block !important; padding: 0 !important; border-left: 0 !important; margin: 0 !important; }
  .answer-tip { display: none !important; }
  .answer-item { margin: 4px 0; }
  img { max-width: 100%; page-break-inside: avoid; }
}
@media screen {
  body { font-family: "Yu Mincho", "MS Mincho", "Noto Serif JP", serif; font-size: 12pt; line-height: 1.8; max-width: 210mm; margin: 24px auto; padding: 0 24px; }
  table { border-collapse: collapse; width: 100%; }
  th, td { border: 1px solid #000; padding: 4px 8px; vertical-align: top; }
  th { background: #eee; }
  pre { border: 1px solid #999; padding: 8px; background: #fafafa; overflow-x: auto; }
  code { font-family: Consolas, "Courier New", monospace; }
  .answer-item { margin: 8px 0; }
  .answer-btn { cursor: pointer; border: 1px solid #555; background: #eee; padding: 2px 10px; border-radius: 4px; font-size: 9pt; }
  .answer-body { padding: 6px 10px; border-left: 3px solid #888; margin-top: 4px; }
  .answer-body[hidden] { display: none; }
  .has-answer { position: relative; cursor: pointer; }
  .has-answer:hover { background: #fffbe6; }
  .answer-tip { display: none; position: absolute; left: 0; top: 100%; z-index: 10; background: #fffbe6; border: 1px solid #bbb; padding: 6px 10px; margin-top: 4px; font-size: 10pt; line-height: 1.5; box-shadow: 0 2px 6px rgba(0,0,0,.2); max-width: 90%; }
  .answer-tip.open { display: block; }
  .back-to-index { margin-bottom: 14px; font-size: 11pt; }
  .back-to-index a { color: #2563eb; text-decoration: underline; border: 1px solid #2563eb; padding: 4px 14px; border-radius: 4px; display: inline-block; }
  .back-to-index a:hover { background: #eef2ff; }
}
</style>
</head>
<body>
<div class="back-to-index"><a href="../../index.html">← 全体のページ（目次）へ戻る</a></div>
{{BODY}}
<script>
(function () {
  function answerKey(text) {
    var m = text.match(/^解答\\s*(\\d+)\\.(\\d+)/);
    return m ? m[1] + "." + m[2] : null;
  }
  function questionKey(text) {
    var m = text.match(/^練習問題\\s*(\\d+)\\.(\\d+)/);
    return m ? m[1] + "." + m[2] : null;
  }
  var answers = {};
  var answerParagraphs = [];
  document.querySelectorAll("p").forEach(function (p) {
    var key = answerKey(p.textContent.trim());
    if (key && answers[key] === undefined) {
      answers[key] = p.innerHTML;
      answerParagraphs.push(p);
    }
  });
  answerParagraphs.forEach(function (p) {
    var key = answerKey(p.textContent.trim());
    var body = document.createElement("div");
    body.className = "answer-body";
    body.hidden = true;
    body.innerHTML = answers[key];
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "answer-btn";
    btn.textContent = "解答を表示";
    btn.addEventListener("click", function () { body.hidden = !body.hidden; });
    var wrap = document.createElement("div");
    wrap.className = "answer-item";
    wrap.appendChild(btn);
    wrap.appendChild(body);
    p.parentNode.replaceChild(wrap, p);
  });
  document.querySelectorAll("p").forEach(function (p) {
    var key = questionKey(p.textContent.trim());
    if (!key || answers[key] === undefined) return;
    p.classList.add("has-answer");
    var tip = document.createElement("span");
    tip.className = "answer-tip";
    tip.textContent = "解答: " + answers[key]
      .replace(/<[^>]+>/g, "")
      .replace(/^解答\\s*\\d+\\.\\d+\\s*/, "")
      .trim();
    p.appendChild(tip);
    p.addEventListener("click", function (ev) {
      if (ev.target.tagName === "A") return;
      tip.classList.toggle("open");
    });
  });
})();
</script>
</body>
</html>
"""


def render_html() -> str:
    text = SRC.read_text(encoding="utf-8")
    body = markdown.markdown(
        text,
        extensions=["extra", "toc", "sane_lists", "tables", "fenced_code"],
        extension_configs={"toc": {"toc_depth": "2-3"}},
    )
    body = re.sub(
        r'<h2 id="([^"]+)">((?:第\d+章|付録[A-Z])[^<]*)</h2>',
        r'<h2 class="chapter" id="\1">\2</h2>',
        body,
    )
    return TEMPLATE.replace("{{BODY}}", body)


def build_pdf() -> None:
    candidates = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]
    browser = next((p for p in candidates if p.exists()), None)
    if browser is None:
        raise SystemExit("Chrome または Edge が見つかりません。--no-pdf でHTMLのみ生成してください。")

    cmd = [
        str(browser),
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=15000",
        f"--print-to-pdf={PDF_OUT}",
        HTML_OUT.as_uri(),
    ]
    subprocess.run(cmd, check=True, timeout=180)
    if not PDF_OUT.exists():
        raise SystemExit("PDF の生成に失敗しました。")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-pdf", action="store_true", help="HTMLのみ生成する")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    HTML_OUT.write_text(render_html(), encoding="utf-8")
    print(f"HTML: {HTML_OUT}")
    if not args.no_pdf:
        build_pdf()
        print(f"PDF:  {PDF_OUT}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"コマンドが失敗しました: {exc}", file=sys.stderr)
        raise
