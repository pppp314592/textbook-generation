# deploy-pages.ps1
# gh-pages ブランチに公開物（index.html・各テーマの印刷用HTML/PDF/assets）を反映して push する。
#
# 使い方:
#   powershell -ExecutionPolicy Bypass -File ".opencode\skills\publish-github\deploy-pages.ps1" -WorkDir .
#
# 前提:
#   - git と gh（GitHub CLI）が利用可能で、ログイン済み。
#   - 作業ディレクトリが git リポジトリで、main ブランチに公開物がコミット済み。
#   - リモート origin が設定済み。

param(
    [string]$WorkDir = "."
)

$ErrorActionPreference = "Stop"
Push-Location $WorkDir
try {
    # 0. 前提チェック
    $branch = (git branch --show-current)
    if (-not $branch) { throw "git リポジトリではありません。まず git init してください。" }
    if ($branch -ne "main") { Write-Host "注意: 現在のブランチは $branch です。main で公開物をコミットしてください。" }

    $remote = (git remote get-url origin 2>$null)
    if (-not $remote) { throw "リモート origin が設定されていません。" }
    Write-Host "remote: $remote"

    $user = (gh api user -q .login 2>$null)
    if (-not $user) { throw "gh でログインしていません。gh auth login を実行してください。" }
    Write-Host "github user: $user"

    # 1. 公開物を一時ディレクトリへコピー
    $tmp = Join-Path $env:TEMP ("ghpages_" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $tmp -Force | Out-Null
    try {
        # index.html
        if (Test-Path ".\index.html") { Copy-Item ".\index.html" (Join-Path $tmp "index.html") }

        # テーマフォルダ（README.md を持つディレクトリ）
        Get-ChildItem -Directory | ForEach-Object {
            $theme = $_.Name
            $readme = Join-Path $theme "README.md"
            if (-not (Test-Path $readme)) { return }

            $dest = Join-Path $tmp $theme
            New-Item -ItemType Directory -Path $dest -Force | Out-Null

            # 印刷用フォルダ全体（HTML・PDF）をコピー
            $printDir = Join-Path $theme "印刷用"
            if (Test-Path $printDir) {
                Copy-Item $printDir (Join-Path $dest "印刷用") -Recurse -Force
            }

            # assets をコピー（印刷用HTMLが ../assets/ を参照するため、テーマ直下に置く）
            $assetsDir = Join-Path $theme "assets"
            if (Test-Path $assetsDir) {
                Copy-Item $assetsDir (Join-Path $dest "assets") -Recurse -Force
            }
        }

        # 2. gh-pages ブランチへ切り替え、一時コピーを反映
        git branch -D gh-pages 2>$null
        git checkout --orphan gh-pages
        git rm -rf --cached . 2>$null | Out-Null

        # 作業ツリーをクリアして一時コピーへ置き換え
        Get-ChildItem -Force | Where-Object { $_.Name -notin @(".git", $tmp) } | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        Copy-Item (Join-Path $tmp "*") . -Recurse -Force

        # 3. コミットして push
        git add -A
        $hasChange = git diff --cached --name-only
        if ($hasChange) {
            git commit -m "deploy: gh-pages update"
            git push origin gh-pages --force
            Write-Host "gh-pages pushed."
        } else {
            Write-Host "gh-pages に変更はありません。"
        }

        # 4. Pages 設定（gh-pages ブランチ / root）
        $repo = (gh repo view --json nameWithOwner -q .nameWithOwner)
        try {
            gh api -X PUT "repos/$repo/pages" -f "source[branch]=gh-pages" -f "source[path]=/" -f "source[build_type]=legacy" 2>$null
            Write-Host "GitHub Pages 設定: gh-pages ブランチ (/)"
        } catch {
            Write-Host "Pages 設定は手動で行ってください: Settings -> Pages -> Branch: gh-pages / (root)"
        }
    } finally {
        # 一時ディレクトリを削除
        Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
    }
} finally {
    Pop-Location
}
