---
name: publish-github
description: 教科書生成プロジェクトをGitで管理し、GitHubに公開し、GitHub Pagesで配布する。git管理・git init・コミット・リポジトリ作成・push・GitHub Pages・gh-pages・公開・メインページ・目次ページ・index.html・デプロイ・配布・アップロードといった言葉を使ったとき、または教科書生成後に配布・公開を頼まれたときに使う。
---

# GitHub公開・配布スキル

作成した教科書プロジェクト（作業ディレクトリ全体）を、以下の流れでGit管理・GitHub公開・GitHub Pages配布まで一気通貫で行う。

1. **Git管理**: 作業ディレクトリをgitリポジトリ化し、`.gitignore` を配置して初回コミットする
2. **メインページ作成**: テーマ一覧から各テーマのREADME・教科書・PDF・印刷用HTMLへリンクする `index.html` を生成する
3. **GitHub公開**: GitHubリポジトリを作成し、`main` ブランチをpushする
4. **GitHub Pages公開**: 公開用ファイルを `gh-pages` ブランチに配置し、Pagesで公開する

## 前提

- `git` と `gh`（GitHub CLI）がインストールされていること。`gh auth status` でログイン済みであること。
- ユーザー名・リポジトリ名・公開レベル（public/private）が未指定の場合は、**開始時にユーザーへ確認する**（スキル内で勝手に決めない）。

## テーマフォルダ構成

このスキルは、次の構成で生成された教科書プロジェクトを前提とする。

```
{作業ディレクトリ}/
├── .opencode/                 # スキル・エージェント・コマンド（git管理対象）
├── {テーマ名}/
│   ├── README.md              # テーマ概要
│   ├── 教科書.md              # 教科書本体（Markdown）
│   ├── 検証レポート.md
│   ├── 調査/最新情報メモ.md
│   ├── 印刷用/
│   │   ├── 教科書-印刷版.html # Pages公開対象（gh-pagesへ）
│   │   └── 教科書.pdf         # Pages公開対象（gh-pagesへ）
│   └── assets/                # 画像等（印刷用HTMLが参照）
└── .gitignore                 # 本スキルが作成
```

- テーマは複数あってよい。メインページは全テーマを一覧表示する。
- 公開対象ファイル（印刷用HTML・PDF・assets）は、**メインブランチ側にも残し、gh-pagesブランチへコピーして公開する**方式をとる（後述）。

## ステップ1: Git管理

### 1-1. gitリポジトリ初期化

既にリポジトリでないことを確認し、初期化する。

```
git init
```

### 1-2. .gitignoreの作成

同梱の `.gitignore.template` をコピーして配置する（無ければスキルの手順に従って作成する）。

```
{作業ディレクトリ}/.gitignore
```

最低限以下を含める:

```gitignore
# Python
__pycache__/
*.pyc

# Node / その他キャッシュ
node_modules/

# OS
.DS_Store
Thumbs.db

# 環境設定
.env
```

**注意**: `.opencode/` は**コミットする**（スキル・エージェント・コマンド自体をgit管理して配布可能にする）。`印刷用/*.pdf` はGitHubリポジトリで配布・Pages公開するため**除外しない**。

### 1-3. 初回コミット

```
git add -A
git commit -m "initial commit"
```

コミットメッセージは簡潔に。テーマを新規追加した場合のコミットは `add: {テーマ名} 教科書` のようにする。

## ステップ2: メインページの作成

### 2-1. index.htmlの生成

同梱の `generate-index.py` を実行してメインページを生成する。

```
python ".opencode\skills\publish-github\generate-index.py" . index.html
```

- このスクリプトは、作業ディレクトリ直下のテーマフォルダ（`README.md` を持つディレクトリ）を走査し、テーマごとに以下へのリンクを自動生成する:
  - `{テーマ名}/README.md`
  - `{テーマ名}/教科書.md`
  - `{テーマ名}/印刷用/教科書.pdf`
  - `{テーマ名}/印刷用/教科書-印刷版.html`
- タイトル・説明は既定値があるが、必要なら引数で上書きできる（下記「generate-index.py 仕様」）。
- 生成後、ブラウザまたはヘッドレスで開いてリンクが機能することを確認する。

### 2-2. index.htmlの構成（既定）

- ページタイトル: 作業ディレクトリ名（`教科書生成` 等）
- テーマ一覧: 各テーマのカード（README / 教科書 / PDF / 印刷用HTML へのリンク）
- 各テーマの対象読者・レベル・進行状況は `{テーマ名}/README.md` から抽出して表示
- 作成日を表示

### 2-3. メインページをGitHubで確認できるように

`index.html` は作業ディレクトリ直下に置き、gitにコミットする。このページがGitHubリポジトリのルートに置かれることで、`https://{user}.github.io/{repo}/` で表示できる。

## ステップ3: GitHubリポジトリ作成とpush

ユーザーから**リポジトリ名と公開レベル**を確認し、以下を実行する。

```
gh repo create {repo名} --{public|private} --source . --remote origin --push
```

- `--source .` で現在のディレクトリをリポジトリにし、`--remote origin` でリモートを追加、`--push` で初回pushする。
- リポジトリが既に存在する場合は `git remote add origin {URL}` と `git push -u origin main` で対応する。
- 既定ブランチ名が `master` になっている場合は `git branch -M main` で `main` に揃える。

## ステップ4: GitHub Pages公開（gh-pagesブランチ方式）

### 4-1. 公開用ファイルの準備

同梱の `deploy-pages.ps1` を実行する。

```
powershell -ExecutionPolicy Bypass -File ".opencode\skills\publish-github\deploy-pages.ps1" -WorkDir .
```

このスクリプトは以下を自動で行う:

1. `gh-pages` ブランチを、`main` ブランチの公開物だけを持つツリーで作成・更新する
2. 公開物として以下を gh-pages に含める:
   - `index.html`（メインページ）
   - 各テーマの `印刷用/教科書-印刷版.html`（**assets参照を `{テーマ名}/印刷用/../assets` ではなく、gh-pagesルートから解決できるパスに書き換える**）
   - 各テーマの `印刷用/教科書.pdf`
   - 各テーマの `assets/` 一式
3. `gh-pages` ブランチを push する

> **画像パスの注意**: 印刷用HTMLは `印刷用/` 配下から `../assets/xxx` を参照している。gh-pages ブランチでは同じ相対位置（`{テーマ名}/印刷用/教科書-印刷版.html` と `{テーマ名}/assets/`）を保てば、リンクはそのまま機能する。deploy-pages.ps1 はこの配置を維持する。

### 4-2. Pages 設定

`gh` で gh-pages ブランチを公開ソースに設定する。

```
gh api -X PUT repos/{user}/{repo}/pages \
  -f source.branch=gh-pages -f source.path=/
```

または、ブラウザで Settings → Pages → Branch で `gh-pages` / `/(root)` を選択する。

### 4-3. 公開URL

公開URLは `https://{user}.github.io/{repo}/`。メインページから各テーマのHTML・PDFへリンクできる。

## 再公開（テーマ追加・更新後）

テーマを新規追加または内容を更新したら:

1. `generate-index.py` で `index.html` を再生成
2. `main` にコミット・push
3. `deploy-pages.ps1` で gh-pages を再構築・push

この3ステップで更新が反映される。Pages の反映には数十秒〜数分かかる場合がある。

## 確認手順

- `git status` で管理対象が意図通りか確認（`.opencode/` が含まれ、`__pycache__` 等が除外されているか）
- `index.html` をブラウザで開き、各テーマへのリンク（README/教科書/PDF/HTML）が機能するか確認
- `gh-pages` ブランチに `index.html`・各テーマのHTML/PDF/assets が含まれるか確認
- 公開URLをヘッドレスブラウザまたは `gh api` でアクセスし、200応答・画像表示を確認
- 完了後、`README.md` または作業メモに公開URLを記録する

## 付属ファイル

| ファイル | 役割 |
|---|---|
| `generate-index.py` | メインページ `index.html` をテーマ一覧から自動生成 |
| `deploy-pages.ps1` | 公開物を `gh-pages` ブランチへ反映して push |
| `.gitignore.template` | リポジトリ用 `.gitignore` の雛形 |

## 注意

- **GitHub ユーザー名・リポジトリ名・公開レベルは、公開の直前にユーザーへ確認してから実行する。** 勝手にリポジトリを作成・公開しない。
- リポジトリに誤って機密情報（APIキー・パスワード等）をコミットしない。コミット前に `git status` と差分を確認する。
- 印刷用HTMLが assets を参照する場合、gh-pages での相対パス整合を必ず確認する（画像が切れたらレイアウトが崩れる）。
- コミット・push・Pages設定はユーザーの明示的な依頼があった場合のみ行う。このスキルを読み込んだだけでは実行しない。
