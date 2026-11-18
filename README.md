# 最終課題 Google のリポジトリ情報のスクレイピング

GitHub の Google のリポジトリ一覧（https://github.com/orgs/google/repositories）を
スクレイピングして、以下の情報を全件分取得する。

- リポジトリ名
- 主要な言語
- スターの数

取得したデータは SQLite の DB（`google_repos.db`）に保存し、SELECT 文で表示する。

## 実行方法

```
pip install requests beautifulsoup4
python main.py
```

## 注意点

- GitHub の API は使わず、HTML をスクレイピングしている
- サーバーに負荷をかけないように、1 ページごとに `time.sleep(1)` を入れている