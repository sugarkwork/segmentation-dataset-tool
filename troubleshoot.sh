#!/bin/bash

echo "=== YOLOv8セグメンテーションツール トラブルシューティング ==="

echo "📊 システム情報:"
echo "  OS: $(uname -s)"
echo "  Docker: $(docker --version 2>/dev/null || echo 'Not installed')"
echo "  Docker Compose: $(docker-compose --version 2>/dev/null || echo 'Not installed')"
echo "  メモリ: $(free -h 2>/dev/null | grep Mem || echo 'N/A')"
echo "  ディスク: $(df -h . | tail -1)"
echo ""

echo "🐳 Dockerコンテナ状態:"
docker-compose ps 2>/dev/null || echo "Docker Composeが実行されていません"
echo ""

echo "📋 コンテナリソース使用状況:"
docker stats --no-stream 2>/dev/null || echo "Docker統計を取得できません"
echo ""

echo "🔌 ポート使用状況:"
echo "  Port 3000: $(lsof -ti:3000 2>/dev/null && echo 'Used' || echo 'Free')"
echo "  Port 8000: $(lsof -ti:8000 2>/dev/null && echo 'Used' || echo 'Free')"
echo "  Port 3306: $(lsof -ti:3306 2>/dev/null && echo 'Used' || echo 'Free')"
echo ""

echo "🏥 ヘルスチェック:"
if curl -s http://localhost:8000/health > /dev/null; then
    echo "  ✅ Backend API: 正常"
else
    echo "  ❌ Backend API: 異常"
fi

if curl -s http://localhost:3000 > /dev/null; then
    echo "  ✅ Frontend: 正常"
else
    echo "  ❌ Frontend: 異常"
fi

if docker exec segmentation_db mysql -u app_user -papp_password -e "SELECT 1;" > /dev/null 2>&1; then
    echo "  ✅ Database: 正常"
else
    echo "  ❌ Database: 異常"
fi
echo ""

echo "📝 最新ログ（最後の20行）:"
echo "--- Backend ---"
docker-compose logs --tail=20 backend 2>/dev/null || echo "Backendログを取得できません"
echo ""
echo "--- Frontend ---"
docker-compose logs --tail=20 frontend 2>/dev/null || echo "Frontendログを取得できません"
echo ""
echo "--- Database ---"
docker-compose logs --tail=20 database 2>/dev/null || echo "Databaseログを取得できません"
echo ""

echo "🔧 推奨対処法:"
echo "1. 全ログ確認:     docker-compose logs"
echo "2. サービス再起動: docker-compose restart"
echo "3. 完全リセット:   docker-compose down -v && docker-compose up -d"
echo "4. イメージ再構築: docker-compose build --no-cache"
echo "5. 環境設定確認:   cat backend/.env frontend/.env"

echo ""
echo "💾 詳細ログ保存:"
echo "docker-compose logs > debug.log 2>&1"
echo "このファイルをサポートに送付してください"