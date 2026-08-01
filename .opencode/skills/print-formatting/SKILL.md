---
name: print-formatting
description: 作成した教科書をA4印刷に適した形式に変換する。Markdownの教科書からA4印刷用のCSS付きHTMLを作成し、ヘッドレスブラウザでPDF化する。印刷・PDF化・A4化・紙に出す・配布用PDF・レイアウト調整といった言葉を使ったとき、または教科書生成後に印刷用形式への変換を頼まれたときに使う。
---

# 印刷用形式変換スキル

作成したMarkdown教科書をA4印刷・PDF配布に適した形式へ変換する。

## テーマフォルダ構成

変換結果はテーマごとのフォルダに配置する。

```
{作業ディレクトリ}/
└── {テーマ名}/
    ├── README.md              # テーマ概要・進行状況（PDF化も記録）
    ├── 教科書.md              # 変換元の教科書本体
    └── 印刷用/
        ├── 教科書-印刷版.html # A4印刷用HTML
        └── 教科書.pdf         # 生成PDF
```

- 対象のテーマフォルダが無い場合は作成する。
- HTML・PDFは `{テーマ名}/印刷用/` に配置する。

## 手順

1. **対象の確定**
   - 変換対象のMarkdown教科書のパスを確認する。未指定ならテーマフォルダ内の作成済み教科書（`{テーマ名}/教科書.md`）を探して選択する。

2. **HTMLへの変換（スクリプトを使用）**
   - 同梱の `md-to-html.py` を実行してHTMLを生成する:
     - `python ".opencode\skills\print-formatting\md-to-html.py" "{テーマ名}\教科書.md" "{テーマ名}\印刷用\教科書-印刷版.html" "{タイトル}"`
   - このスクリプトが自動で以下を処理する:
     1. **目次リンクの確実な生成**: 全見出しを走査して固有のアンカーIDを割り当て（重複は `-2`, `-3` で回避）、`## 目次` の内容を見出しから自動生成したリンクに置き換える。Markdown中の手書きリンクに依存しないためリンク切れが起きない
     2. **練習問題のインタラクティブ化**: 付録の「練習問題の解答」を、画面上ではクリック（またはマウスオーバー）で解答を表示・非表示できるボタン付き要素に変換する。各章の練習問題本文にもマウスオーバーで解答がポップアップ表示される
     3. **A4印刷CSSの埋め込み**: ヘッダ・フッタに日時・URL・ページ番号を出さない印刷設定（下記参照）
     4. **Web画像のダウンロード**: Markdown内の `![...](https://...)` 形式の画像URLを `{テーマ名}/assets/` へダウンロードし、参照を相対パス（`assets/img-....png`）に置き換える。ローカル画像やdata URIはそのまま
   - スクリプトがない環境やPythonが無い場合は、Markdownを読み込んで手動で単一の自己完結型HTML（`{テーマ名}/印刷用/教科書-印刷版.html`）に変換する。
   - 手動変換の場合も以下の要件を満たすこと:
     - スタイルは `<style>` に埋め込み、外部ファイル・外部リソース（画像を除く）に依存させない
     - 目次リンクは `<h1>`〜`<h3>` の `id` 属性と必ず一致させる（下記「リンクの確実化」参照）
     - 練習問題の解答はボタン/マウスオーバーで開閉できる要素にし、印刷時は開いた状態で表示する

3. **A4印刷CSS**
   - **ヘッダ・フッタの抑制**: 印刷時にヘッダへ日時、フッタへURL・ページ番号が出ないようにする。`@page` には margin box を定義しない（`@top-center` 等を置かない）。ブラウザ印刷ダイアログでも「ヘッダーとフッター」のチェックを外すよう案内する。PDF化は `html-to-pdf.ps1` の `--print-to-pdf-no-header` でヘッダ・フッタなしになる。
   - 以下のCSSを必ず含める:

```css
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
  /* 練習問題: 印刷時は解答を常時表示する */
  .answer-btn { display: none !important; }
  .answer-body, .answer-body[hidden] { display: block !important; }
  .answer-tip { display: none !important; }
}
@media screen {
  body { font-family: "Yu Mincho", "MS Mincho", "Noto Serif JP", serif; font-size: 12pt; line-height: 1.8; max-width: 210mm; margin: 24px auto; padding: 0 24px; }
  /* 練習問題: 画面上ではマウスオーバー/クリックで解答を表示 */
  .answer-item { margin: 8px 0; }
  .answer-btn { cursor: pointer; border: 1px solid #555; background: #eee; padding: 2px 10px; border-radius: 4px; font-size: 9pt; }
  .answer-body { padding: 6px 10px; border-left: 3px solid #888; margin-top: 4px; }
  .answer-body[hidden] { display: none; }
  .answer-item:hover .answer-body { display: block; }
  .has-answer { position: relative; cursor: pointer; }
  .answer-tip { display: none; position: absolute; left: 0; top: 100%; z-index: 10; background: #fffbe6; border: 1px solid #bbb; padding: 6px 10px; margin-top: 4px; font-size: 10pt; line-height: 1.5; box-shadow: 0 2px 6px rgba(0,0,0,.2); }
  .has-answer:hover .answer-tip, .answer-tip.open { display: block; }
}
```

4. **表紙の追加**
   - HTML冒頭に表紙ページを追加する: タイトル（大）、副題、対象読者・レベル・想定学習時間、作成日。表紙の後には `<div class="pagebreak"></div>` を入れる。
   - 目次ページを表紙の後に置き、`page-break-after` で改ページする。

## リンクの確実化

目次や相互参照のリンクが機能しない問題を防ぐため、以下のルールでリンクを生成する。

- **自動生成を優先**: `md-to-html.py` を使う場合、見出しIDと目次リンクはスクリプトが同じロジックで生成するため必ず一致する。手動で書かない。
- **手動変換の場合**:
  1. 各見出し（`<h1>`〜`<h3>`）に `id` 属性を付与する。IDはその見出しのテキストを基にした slug にする（例: 第1章なら `id="chapter1"` のように決定的なID）。
  2. 目次の `<a href="#...">` は、必ずその見出しの `id` と完全一致させる。
  3. リンク対象を決めたら、`id` を付ける工程と目次を書く工程を1回で終わらせる（2回に分けるとずれる原因になる）。
  4. 日本語slugの文字エンコーディングで壊れやすい場合は、英数字ベースのID（`chapter1`, `sec2-3` 等）を使う方が安全。
- **検証**: HTML生成後に、`href="#..."` がすべて `<h1>`〜`<h3>` の `id` に存在することを確認する（grep等で `id="` と `href="#` の一覧を突き合わせる）。

## 画像の取得と著作権

教科書に参考画像が必要な場合、Webから取得して埋め込む。**必ず著作権・ライセンスを確認してから使うこと。**

- **取得方法**: 教科書のMarkdownに `![説明文](https://...画像URL)` の形式で画像URLを書く。`md-to-html.py` が変換時に自動でダウンロードして `{テーマ名}/assets/` に保存し、参照を相対パスに置き換える。
- **著作権・ライセンス確認（必須）**:
  1. 自由に使える画像を選ぶ: パブリックドメイン、CC0（例: Wikimedia Commons のCC0/パブリックドメイン画像、Unsplash等のフリー素材）、または自前で作成した図。
  2. ライセンス上「出典明記が必要」な画像（CC BY等）は、画像のキャプションまたは出典欄に**著作者名とライセンス**を必ず明記する。
  3. 権利者が明示していない画像・商用利用不可の画像・著作権保護期間内の作品・Webサイト上のロゴやスクリーンショットは**使わない**。
- **保存場所**: ダウンロードした画像は `{テーマ名}/assets/` に置く。原稿のMarkdownには相対パス（`assets/...`）で記載する。
- **画像を追加する際の確認**: HTML変換後に画像が表示されること、`assets/` にファイルが存在することを確認する。ダウンロードに失敗した画像URLは変換時に警告が出るため、別の画像URLに差し替える。
- 図やグラフは、可能なら画像URLに頼らずテキスト・表・テキストベースの図で表現する方が確実。

5. **PDF化**
   - 同梱の `html-to-pdf.ps1` を実行してPDFを生成する:
     - `powershell -ExecutionPolicy Bypass -File ".opencode\skills\print-formatting\html-to-pdf.ps1" -InputHtml "{テーマ名}\印刷用\教科書-印刷版.html" -OutputPdf "{テーマ名}\印刷用\教科書.pdf"`
   - スクリプトは自動でChromiumまたはEdgeを見つけてヘッドレス印刷する。見つからない場合は `-Browser "C:\...\chrome.exe"` でパスを指定する。

6. **確認**
   - 生成されたPDFのファイルサイズと存在を確認し、ページ数（おおよそ）を報告する。
   - 表が横にはみ出していないか、ページ内で切れそうな表・コードがないかを確認し、必要ならCSSやレイアウトを調整して再生成する。
   - **ヘッダ・フッタに日時・URL・ページ番号が出ていないことを確認する**（PDFの1ページ目〜数ページ目を確認。出ている場合は `--print-to-pdf-no-header` が付いているか、`@page` margin boxが無いか確認）。
   - **目次リンクが全て機能することを確認する**（HTMLをブラウザで開き、目次の各リンクをクリックして該当見出しへ移動するか確認。あるいは `href="#"` と `id="` の突き合わせで全件検証）。
   - **練習問題の解答が画面上で開閉できることを確認する**（HTMLをブラウザで開き、解答ボタンのクリックとマウスオーバーで解答が表示されるか確認。PDF側では解答が常時表示されていることを確認）。
   - **画像が表示されることを確認する**（HTMLをブラウザで開き、画像が表示されるか、`{テーマ名}/assets/` に画像ファイルが存在するかを確認。ダウンロード失敗の警告が出た画像URLは差し替える）。
   - `README.md` の進行状況を「PDF化済み」に更新する。

## 注意

- 元のMarkdownは変更しない。HTMLとPDFは別ファイルとして出力する。
- 画像がある場合は相対パスをHTMLから解決できる場所（`{テーマ名}/assets/`）に置く。
- 文字化けを防ぐためHTMLは `<meta charset="UTF-8">` を必ず入れる。
