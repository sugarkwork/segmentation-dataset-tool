# 🚀 クイックスタート

YOLOv8セグメンテーションデータセット作成ツールを5分でセットアップする手順です。

## 前提条件

- Docker & Docker Compose がインストール済み
- Git がインストール済み
- 8GB以上のメモリ

## 1分セットアップ

```bash
# 1. リポジトリをクローン
git clone https://github.com/sugarkwork/segmentation-dataset-tool.git
cd segmentation-dataset-tool

# 2. 環境設定ファイルをコピー
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. 起動
./start.sh
```

## アクセス

起動完了後、以下のURLにアクセスできます：

- **Webアプリ**: http://localhost:3000
- **API**: http://localhost:8000
- **APIドキュメント**: http://localhost:8000/docs

## テストユーザー

以下のアカウントでログインできます：

| ユーザー名 | パスワード | 権限 |
|-----------|----------|------|
| admin     | password | 管理者 |
| testuser  | password | 一般ユーザー |

## トラブルシューティング

問題が発生した場合：

```bash
# 診断実行
./troubleshoot.sh

# ログ確認
docker-compose logs

# 完全リセット
docker-compose down -v
docker-compose up -d
```

## 次のステップ

1. [詳細な導入手順](./導入手順書.md)
2. [技術要件書](./技術要件書.md)
3. [使用方法](./README.md)

## サポート

問題や質問がある場合は、[Issues](https://github.com/sugarkwork/segmentation-dataset-tool/issues) でお知らせください。