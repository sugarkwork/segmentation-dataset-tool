#!/bin/bash

set -e

echo "=== YOLOv8セグメンテーションデータセット作成ツール 起動スクリプト ==="

# 環境設定ファイルの確認・作成
echo "1. 環境設定ファイルの確認..."
if [ ! -f "backend/.env" ]; then
    echo "backend/.env が見つかりません。テンプレートをコピーします..."
    cp backend/.env.example backend/.env
    echo "⚠️  backend/.env を編集してください（特にSECRET_KEY）"
fi

if [ ! -f "frontend/.env" ]; then
    echo "frontend/.env が見つかりません。テンプレートをコピーします..."
    cp frontend/.env.example frontend/.env
fi

# Docker/Docker Composeの確認
echo "2. Dockerの確認..."
if ! command -v docker &> /dev/null; then
    echo "❌ Dockerがインストールされていません"
    echo "インストール手順: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Composeがインストールされていません"
    echo "インストール手順: https://docs.docker.com/compose/install/"
    exit 1
fi

# Dockerの起動確認
if ! docker info &> /dev/null; then
    echo "❌ Docker Engineが起動していません"
    echo "以下のコマンドで起動してください:"
    echo "  sudo systemctl start docker"
    exit 1
fi

# 既存のコンテナを停止
echo "3. 既存のコンテナを停止..."
docker-compose down 2>/dev/null || true

# アップロードディレクトリの作成
echo "4. ディレクトリの作成..."
mkdir -p uploads temp

# サービスの起動
echo "5. サービスを起動中..."
docker-compose up -d

# 起動確認
echo "6. サービスの起動確認..."
sleep 10

# ヘルスチェック
echo "7. ヘルスチェック実行中..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ バックエンドAPI: 正常"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ バックエンドAPIが起動しません"
        echo "ログを確認してください: docker-compose logs backend"
        exit 1
    fi
    sleep 2
done

for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null; then
        echo "✅ フロントエンド: 正常"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ フロントエンドが起動しません"
        echo "ログを確認してください: docker-compose logs frontend"
        exit 1
    fi
    sleep 2
done

# データベース接続確認
echo "8. データベース接続確認..."
if docker exec segmentation_db mysql -u app_user -papp_password -e "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ データベース: 正常"
else
    echo "❌ データベース接続エラー"
    echo "ログを確認してください: docker-compose logs database"
    exit 1
fi

echo ""
echo "🎉 起動完了！"
echo ""
echo "📱 アクセス先:"
echo "  - フロントエンド:    http://localhost:3000"
echo "  - バックエンドAPI:   http://localhost:8000"
echo "  - API ドキュメント:  http://localhost:8000/docs"
echo ""
echo "👤 テストユーザー:"
echo "  - 管理者: admin / password"
echo "  - 一般:   testuser / password"
echo ""
echo "🔧 管理コマンド:"
echo "  - ログ確認:    docker-compose logs -f"
echo "  - 停止:        docker-compose down"
echo "  - 再起動:      docker-compose restart"
echo ""
echo "❓ トラブルが発生した場合:"
echo "  - ログ確認:    docker-compose logs"
echo "  - コンテナ状態: docker-compose ps"
echo "  - リセット:    docker-compose down -v && docker-compose up -d"