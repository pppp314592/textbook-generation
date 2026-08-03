import sys
import re
import os
import uuid
import markdown

def download_images(md_text, assets_dir):
    """Markdown内の画像URLを assets_dir へダウンロードし、参照を相対パスに置き換える。

    画像URLは `![alt](url)` 形式のものを対象とする。ローカル画像や data URI は
    そのままにする。著作権・ライセンス確認は呼び出し側（スキル手順）で行うこと。
    """
    if not os.path.isdir(assets_dir):
        os.makedirs(assets_dir, exist_ok=True)

    pattern = re.compile(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)')

    def repl(m):
        alt = m.group(1)
        url = m.group(2)
        if not url.startswith(('http://', 'https://')):
            return m.group(0)
        try:
            ext = os.path.splitext(url.split('?')[0])[1].lower()
            if ext not in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'):
                ext = '.png'
            name = 'img-%s%s' % (uuid.uuid4().hex[:12], ext)
            dest = os.path.join(assets_dir, name)
            _download(url, dest)
            return '![%s](%s)' % (alt, os.path.join('assets', name))
        except Exception as e:
            print('[image warn] ダウンロード失敗: %s (%s)' % (url, e))
            return m.group(0)

    return pattern.sub(repl, md_text)

def _download(url, dest):
    import urllib.request
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (textbook-creator)'})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = r.read()
    with open(dest, 'wb') as f:
        f.write(data)

def slugify(text, used):
    text = re.sub(r'[`*_\[\]()]', '', text).strip()
    text = re.sub(r'[\s\u3000]+', '-', text)
    text = re.sub(r'[^\w\-]', '', text, flags=re.UNICODE)
    if text == '':
        text = 'section'
    base = text
    i = 2
    while text in used:
        text = '%s-%d' % (base, i)
        i += 1
    used.add(text)
    return text

def extract_headings(lines):
    headings = []
    used = set()
    in_fence = False
    for line in lines:
        if line.strip().startswith('```'):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r'^(#{1,4})\s+(.+?)\s*$', line)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            slug = slugify(text, used)
            headings.append((level, text, slug))
    return headings

def build_toc(headings):
    lines = ['## 目次', '']
    for level, text, slug in headings:
        if level == 1:
            continue
        if text.strip() == '目次':
            continue
        lines.append('- [%s](#%s)' % (text, slug))
    lines.append('')
    return '\n'.join(lines)

def replace_toc(md_text, toc_md):
    pattern = re.compile(r'^## 目次\s*$.*?(?=^## )', re.MULTILINE | re.DOTALL)
    if pattern.search(md_text):
        return pattern.sub(lambda m: toc_md + '\n', md_text, count=1)
    return md_text

def add_ids(md_text, headings):
    lines = md_text.split('\n')
    out = []
    idx = 0
    in_fence = False
    for line in lines:
        if line.strip().startswith('```'):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        m = re.match(r'^(#{1,4})\s+(.+?)\s*$', line)
        if m and idx < len(headings):
            slug = headings[idx][2]
            idx += 1
            out.append('%s {#%s}' % (line, slug))
        else:
            out.append(line)
    return '\n'.join(out)

CSS = """
@page {
  size: A4;
  margin: 18mm 15mm 18mm 15mm;
}
@media print {
  body { font-family: "Yu Mincho", "MS Mincho", "Noto Serif JP", serif; font-size: 10.5pt; line-height: 1.7; color: #000; background: #fff; }
  h1 { page-break-before: always; font-size: 20pt; border-bottom: 2px solid #000; padding-bottom: 6px; }
  h1:first-of-type { page-break-before: avoid; }
  h2 { page-break-after: avoid; font-size: 15pt; }
  h3 { page-break-after: avoid; font-size: 12.5pt; }
  table { border-collapse: collapse; width: 100%; page-break-inside: auto; }
  th, td { border: 1px solid #000; padding: 4px 8px; font-size: 9.5pt; }
  th { background: #eee; }
  pre, code { font-family: Consolas, "Courier New", monospace; font-size: 9pt; white-space: pre-wrap; }
  pre { border: 1px solid #999; padding: 8px; page-break-inside: avoid; }
  .pagebreak { page-break-after: always; }
  a { color: #000; text-decoration: none; }
  .back-to-index { display: none !important; }
  .answer-btn { display: none !important; }
  .answer-body, .answer-body[hidden] { display: block !important; }
  .answer-tip { display: none !important; }
  img { max-width: 100%; page-break-inside: avoid; }
}
@media screen {
  body { font-family: "Yu Mincho", "MS Mincho", "Noto Serif JP", serif; font-size: 12pt; line-height: 1.8; max-width: 210mm; margin: 24px auto; padding: 0 24px; }
  table { border-collapse: collapse; width: 100%; }
  th, td { border: 1px solid #000; padding: 4px 8px; }
  th { background: #eee; }
  .answer-item { margin: 8px 0; }
  .answer-btn { cursor: pointer; border: 1px solid #555; background: #eee; padding: 2px 10px; border-radius: 4px; font-size: 9pt; }
  .answer-body { padding: 6px 10px; border-left: 3px solid #888; margin-top: 4px; }
  .answer-body[hidden] { display: none; }
  .answer-item:hover .answer-body { display: block; }
  .has-answer { position: relative; cursor: pointer; }
  .answer-tip { display: none; position: absolute; left: 0; top: 100%; z-index: 10; background: #fffbe6; border: 1px solid #bbb; padding: 6px 10px; margin-top: 4px; font-size: 10pt; line-height: 1.5; box-shadow: 0 2px 6px rgba(0,0,0,.2); }
  .has-answer:hover .answer-tip, .answer-tip.open { display: block; }
  .back-to-index { margin-bottom: 14px; font-size: 11pt; }
  .back-to-index a { color: #2563eb; text-decoration: underline; border: 1px solid #2563eb; padding: 4px 14px; border-radius: 4px; display: inline-block; }
  .back-to-index a:hover { background: #eef2ff; }
}
"""

JS = """
<script>
(function(){
  function escapeHtml(s){
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }
  function numOf(text){
    var m = text.match(/(?:练习问题|練習問題)\\s*(\\d+)[.\\s](\\d+)/);
    return m ? m[1] + '.' + m[2] : null;
  }
  function makeAnswerItem(key, p){
    var body = document.createElement('div');
    body.className = 'answer-body';
    body.hidden = true;
    body.innerHTML = p.innerHTML;
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'answer-btn';
    btn.textContent = '解答を表示';
    btn.addEventListener('click', function(){ body.hidden = !body.hidden; });
    var wrap = document.createElement('div');
    wrap.className = 'answer-item';
    wrap.id = 'answer-' + key.replace('.', '-');
    wrap.appendChild(btn);
    wrap.appendChild(body);
    p.parentNode.insertBefore(wrap, p);
    p.parentNode.removeChild(p);
  }
  document.addEventListener('DOMContentLoaded', function(){
    var answerMap = {};

    var heads = document.querySelectorAll('h3');
    heads.forEach(function(h){
      var key = numOf(h.textContent);
      if(!key) return;
      if(answerMap[key] !== undefined) return;
      var p = h.nextElementSibling;
      if(p && p.tagName === 'P'){
        answerMap[key] = p.textContent.replace(/^解答[：:]\\s*\\d+\\s*[—\\-]?\\s*/, '').trim();
        makeAnswerItem(key, p);
      }
    });

    var sectionH = null;
    var h2s = document.querySelectorAll('h2');
    h2s.forEach(function(h2){
      if(sectionH) return;
      if(/付録A/.test(h2.textContent)) sectionH = h2;
    });
    var afterSection = function(el){
      return sectionH && (sectionH.compareDocumentPosition(el) & 4) !== 0;
    };

    var ps = document.querySelectorAll('p');
    ps.forEach(function(p){
      var key = numOf(p.textContent);
      if(!key) return;
      if(answerMap[key] !== undefined) return;
      if(!afterSection(p)) return;
      var tipText = p.textContent
        .replace(/^(?:练习问题|練習問題)\\s*\\d+[.\\s]\\d+\\s*[：:]?/, '')
        .replace(/^解答[：:]?\\s*/, '')
        .trim();
      answerMap[key] = tipText;
      makeAnswerItem(key, p);
    });

    var ps2 = document.querySelectorAll('p');
    ps2.forEach(function(p){
      if(p.querySelector('.answer-tip')) return;
      var key = numOf(p.textContent);
      if(!key) return;
      if(answerMap[key] === undefined) return;
      p.classList.add('has-answer');
      p.setAttribute('data-answer-key', key);
      var tip = document.createElement('span');
      tip.className = 'answer-tip';
      tip.innerHTML = '<b>回答</b> ' + escapeHtml(answerMap[key]);
      p.appendChild(tip);
      p.addEventListener('click', function(ev){
        if(ev.target.tagName === 'A') return;
        tip.classList.toggle('open');
      });
    });
  });
})();
</script>
"""

def build_back_link(html_path):
    """全体ページ(index.html)への戻りリンクHTMLを生成する。

    印刷用HTMLは `{テーマ}/印刷用/*.html` に置かれることを前提とし、
    作業ディレクトリ直下の index.html への相対パスを計算する。
    ローカル・gh-pages どちらでも同じ相対構造で機能する。
    index.html が存在しない場合は空文字を返す（リンク無しで生成）。
    """
    html_dir = os.path.dirname(os.path.abspath(html_path))
    theme_dir = os.path.dirname(html_dir)
    root_dir = os.path.dirname(theme_dir)
    index_path = os.path.join(root_dir, 'index.html')
    if not os.path.exists(index_path):
        return ''
    rel = os.path.relpath(index_path, html_dir).replace('\\', '/')
    return ('<div class="back-to-index"><a href="%s">← 全体のページ（目次）へ戻る</a></div>'
            % rel)

def fix_image_src(html, md_path, html_path):
    """生成したHTML内の <img src="..."> を、HTML出力位置から解決できる相対パスへ変換する。

    Markdown内では {md の場所}/assets/xxx.png を 'assets/xxx.png' と書いている。
    HTMLを別フォルダ（例: 印刷用/）へ出力すると、HTMLからはその相対パスが解決できず
    画像が表示されないため、html_path からの相対パス（例: ../assets/xxx.png）に直す。
    外部URL・data URI・絶対パスは変更しない。
    """
    md_dir = os.path.dirname(os.path.abspath(md_path))
    html_dir = os.path.dirname(os.path.abspath(html_path))

    pattern = re.compile(r'(<img[^>]+src=")([^"]+)(")')

    def repl(m):
        prefix, src, suffix = m.group(1), m.group(2), m.group(3)
        if src.startswith(('http://', 'https://', 'data:')):
            return m.group(0)
        if os.path.isabs(src):
            return m.group(0)
        abs_src = os.path.normpath(os.path.join(md_dir, src))
        rel = os.path.relpath(abs_src, html_dir).replace('\\', '/')
        return prefix + rel + suffix

    return pattern.sub(repl, html)

def main():
    if len(sys.argv) < 3:
        print('Usage: md-to-html.py <input.md> <output.html> [title]')
        sys.exit(1)

    md_path = sys.argv[1]
    html_path = sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else '教科書'

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    md_text = download_images(md_text, os.path.join(os.path.dirname(os.path.abspath(md_path)), 'assets'))

    lines = md_text.split('\n')
    headings = extract_headings(lines)
    toc_md = build_toc(headings)
    md_with_toc = replace_toc(md_text, toc_md)
    md_with_ids = add_ids(md_with_toc, headings)

    html_body = markdown.markdown(
        md_with_ids,
        extensions=['tables', 'fenced_code', 'attr_list'],
    )

    html_items = ['%s' % build_back_link(html_path), html_body, JS]
    html = (
        '<!DOCTYPE html>\n'
        '<html lang="ja">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<title>%s</title>\n'
        '<style>%s</style>\n'
        '</head>\n'
        '<body>\n%s</body>\n'
        '</html>\n'
    ) % (title, CSS, '\n'.join(html_items))

    html = fix_image_src(html, md_path, html_path)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print('HTML written: %s' % html_path)

if __name__ == '__main__':
    main()
