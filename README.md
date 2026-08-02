# 教科書生成

学習用の教科書をMarkdownで作成し、PDF・印刷用HTMLへ変換して公開するプロジェクトです。

- **公開サイト（GitHub Pages）**: https://pppp314592.github.io/textbook-generation/

## 収録教科書

| テーマ | 概要 | レベル | 備考 |
|---|---|---|---|
| [G検定](./G検定/README.md) | 生成AI・AIに関する基礎知識の解説 | 初級〜中級 | 想定学習時間 30〜50時間 |
| [Makefile](./Makefile/README.md) | Makefileの実践的な活用法 | 中級 | 想定学習時間 10〜15時間 |

## 構成

```
教科書生成/
├── index.html        # 公開サイトのメインページ
├── {テーマ名}/
│   ├── README.md     # テーマ概要
│   ├── 教科書.md     # 教科書本体（Markdown）
│   ├── 検証レポート.md
│   ├── 調査/          # 最新情報メモ
│   ├── 印刷用/        # PDF・印刷用HTML
│   └── assets/        # 画像等
└── .opencode/         # 生成スキル・エージェント
```

## 公開フロー

1. 教科書をMarkdownで作成・検証
2. 印刷用HTML・PDFを生成
3. `index.html` を生成して `main` にコミット
4. `gh-pages` ブランチへ公開物を反映して GitHub Pages で配布

## 利用方法

- 閲覧: 公開サイト（GitHub Pages）から各教科書のHTML・PDFを開く
- リポジトリ内: `{テーマ名}/教科書.md` でMarkdown原稿、`{テーマ名}/印刷用/` でPDF・印刷用HTMLを確認
