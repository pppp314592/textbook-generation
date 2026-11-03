# LinuC レベル1 試験対策教科書

LinuC-1 Version 10.0（2026年時点）の公式出題範囲に沿った試験対策教科書です。

## 成果物

| ファイル | 内容 |
| --- | --- |
| `教科書.md` | 原稿（Markdown） |
| `印刷用/教科書-印刷版.html` | 印刷用HTML（画面では解答ツールチップ付き） |
| `印刷用/教科書.pdf` | A4 PDF（74ページ） |
| `build.py` | HTML／PDF生成スクリプト |
| `調査/最新情報メモ.md` | 公式情報の調査メモ |

## ビルド

Python 3 と `markdown` パッケージ、Chrome または Edge が必要です。

```bash
python -m pip install markdown
python build.py          # HTML と PDF を生成
python build.py --no-pdf # HTML のみ生成
```

## 構成

- はじめに／学習目標／LinuCとは／試験概要／本書の使い方
- 第1章〜第12章（公式主題 1.01〜1.11 ＋ 総まとめ）
- 付録A 練習問題の解答（62問）
- 付録B コマンド早見表
- 付録C 用語集
- 付録D 参考情報

## 注意

試験制度・出題範囲・受験料は変更される可能性があります。受験前には必ず [LinuC 公式サイト](https://linuc.org/linuc1/) を確認してください。
