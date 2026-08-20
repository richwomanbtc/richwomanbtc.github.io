# richwomanbtc.github.io

[Kenji Kubo の研究者ページ](https://richwomanbtc.github.io/)です。公開されている
[researchmap](https://researchmap.jp/kenjikun) のプロフィールを週1回取得し、公開用 HTML
へ変換して GitHub Pages に反映します。

## 自動更新の流れ

1. `.github/workflows/update_research.yml` が毎週日曜 09:17 JST または手動実行時に
   Researchmap 同期を起動します。
2. `researchmap_site.client` が timeout と retry 付きで Researchmap API を取得し、
   JSON-LD の最低限の構造を検証します。
3. `researchmap_site.render` が公開用 Markdown を正規化し、Actions 内で HTML 断片へ
   変換します。ブラウザ側は第三者 Markdown CDN に依存しません。
4. 全生成に成功した場合だけ `_auto_contents` を一括で置き換えます。取得・変換に
   失敗した場合は非ゼロ終了し、古い公開データは変更しません。
5. 生成物を `main` に記録し、追跡済みファイルだけから作ったスナップショットを
   GitHub Pages の公開元である `page` ブランチへ同期します。

通常の `main` への push は独立した `.github/workflows/deploy.yml` が検証・配信します。
そのため、Researchmap 同期 workflow が停止中でも、サイト本体の修正は配信できます。

Researchmap が一時停止している場合も、atomic sync により最後に成功した生成物を保持します。
同期 workflow は既存生成物を `page` へ維持したうえで failure になり、障害を通知します。
上流障害がサイト全体の配信停止や空データへの置換に波及することはありません。

成功時は `last_updated` を更新し、失敗時も空の heartbeat commit を `main` に記録するため、
静的な公開リポジトリでも週次 activity が残ります。GitHub は public repository に60日間
activity がないと scheduled workflow を自動停止するため、この記録は更新履歴と停止予防を
兼ねています。

## ローカル開発

Python 3.11 以上と Node.js（JavaScript の構文確認用）が必要です。

```bash
make install
make sync
make check
make serve
```

`http://localhost:8000` を開くと公開前の表示を確認できます。`make fetch` は以前の操作との
互換用で、`make sync` と同じ処理です。

## 設定とディレクトリ

- `site.toml`: Researchmap permalink、メールアドレス、SNS リンク
- `researchmap_site/`: API client、設定、Markdown renderer、atomic sync
- `_auto_contents/`: 自動生成物。直接編集しないでください
- `_contents/`: 手動管理する本文
- `assets/`: ブラウザ側の CSS、JavaScript、画像
- `tests/`: API failure、変換、atomic replacement の regression tests

API の生 JSON はページから利用していないため保存しません。公開物を必要な情報だけに
限定し、JSON と Markdown の二重管理も避けています。`page` ブランチへ配信するのも
`index.html`、`assets`、`_auto_contents`、`.nojekyll` だけです。

## Actions が停止した場合

状態を確認し、inactivity により無効化されていたら write 権限のあるアカウントで再開します。

```bash
gh workflow view update_research.yml
gh workflow enable update_research.yml
gh workflow run update_research.yml
```

手動実行後は Actions の成功だけでなく、`main` と `page` の更新コミット、および公開ページの
`Last synchronized` が更新されたことまで確認してください。
