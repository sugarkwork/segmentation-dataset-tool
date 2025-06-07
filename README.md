# セグメンテーションデータセット作成Web GUI

YOLOv8セグメンテーション学習用データセットを作成するためのWebアプリケーション

## プロジェクト構造

```
segmentation-dataset-tool/
├── backend/                    # FastAPI バックエンド
│   ├── app/
│   │   ├── api/               # API エンドポイント
│   │   ├── core/              # 設定・セキュリティ
│   │   ├── crud/              # データベース操作
│   │   ├── models/            # SQLAlchemy モデル
│   │   ├── schemas/           # Pydantic スキーマ
│   │   ├── services/          # ビジネスロジック
│   │   └── utils/             # ユーティリティ
│   ├── tests/                 # テストファイル
│   ├── alembic/               # データベースマイグレーション
│   └── uploads/               # アップロードファイル
├── frontend/                   # React フロントエンド
│   ├── src/
│   │   ├── components/        # Reactコンポーネント
│   │   ├── pages/             # ページコンポーネント
│   │   ├── hooks/             # カスタムフック
│   │   ├── utils/             # ユーティリティ
│   │   ├── services/          # API サービス
│   │   ├── types/             # TypeScript 型定義
│   │   └── store/             # Redux ストア
│   └── public/                # 静的ファイル
├── database/                   # データベース設定
├── docker/                     # Docker 設定
└── docs/                      # ドキュメント
```

## 技術スタック

### バックエンド
- **FastAPI**: Python Web フレームワーク
- **SQLAlchemy**: ORM
- **Alembic**: データベースマイグレーション
- **MariaDB**: データベース
- **OpenCV**: 画像処理
- **Pillow**: 画像操作

### フロントエンド
- **React 18**: UI フレームワーク
- **TypeScript**: 型安全性
- **Material-UI**: UI コンポーネント
- **Fabric.js**: Canvas 操作
- **Redux Toolkit**: 状態管理
- **React Router**: ルーティング

### インフラ
- **Docker**: コンテナ化
- **Nginx**: リバースプロキシ
- **Uvicorn**: ASGI サーバー

## 主要機能

1. **ユーザー認証**: ID/パスワード認証（将来的にOAuth対応）
2. **プロジェクト管理**: プロジェクト作成・編集・削除
3. **画像管理**: 複数画像アップロード・一覧表示
4. **セグメンテーション編集**: Photoshopライクな描画機能
5. **クラス管理**: セグメンテーションクラスの定義・管理
6. **データセット生成**: YOLOv8形式ラベル生成
7. **エクスポート**: ZIP形式でのデータセット出力

## セットアップ

### 前提条件
- Docker & Docker Compose
- Python 3.9+
- Node.js 18+
- MariaDB 10.6+

### 開発環境構築
```bash
# リポジトリクローン
git clone <repository-url>
cd segmentation-dataset-tool

# Docker Compose でサービス起動
docker-compose up -d

# バックエンド依存関係インストール
cd backend
pip install -r requirements.txt

# フロントエンド依存関係インストール
cd ../frontend
npm install

# 開発サーバー起動
npm start
```

### データベースマイグレーション
```bash
cd backend
alembic upgrade head
```

## API エンドポイント

### 認証
- `POST /auth/login`: ログイン
- `POST /auth/register`: ユーザー登録
- `POST /auth/logout`: ログアウト

### プロジェクト
- `GET /projects`: プロジェクト一覧
- `POST /projects`: プロジェクト作成
- `GET /projects/{id}`: プロジェクト詳細
- `PUT /projects/{id}`: プロジェクト更新
- `DELETE /projects/{id}`: プロジェクト削除

### 画像
- `POST /projects/{id}/images`: 画像アップロード
- `GET /projects/{id}/images`: 画像一覧
- `DELETE /images/{id}`: 画像削除

### セグメンテーション
- `GET /images/{id}/segmentations`: セグメンテーション一覧
- `POST /images/{id}/segmentations`: セグメンテーション作成
- `PUT /segmentations/{id}`: セグメンテーション更新
- `DELETE /segmentations/{id}`: セグメンテーション削除

### エクスポート
- `POST /projects/{id}/export`: データセットエクスポート

## 開発ガイドライン

### コーディング規約
- **Python**: PEP 8 準拠、Black フォーマッター使用
- **TypeScript**: ESLint + Prettier 使用
- **コミット**: Conventional Commits 形式

### テスト
- **バックエンド**: pytest + coverage
- **フロントエンド**: Jest + React Testing Library

### デプロイ
- Docker Compose による本番環境構築
- 環境変数による設定管理
- CI/CD パイプライン (GitHub Actions)

## ライセンス

MIT License