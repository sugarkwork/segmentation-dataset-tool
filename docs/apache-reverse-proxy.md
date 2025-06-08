# Apache2 リバースプロキシ設定ガイド

このガイドでは、セグメンテーションデータセット作成ツールをApache2のリバースプロキシ経由で公開する方法を説明します。

## 前提条件

- Apache2がインストール済み
- 必要なモジュールが有効化されている
- Docker Composeでアプリケーションが起動済み

## 1. 必要なApacheモジュールの有効化

```bash
# 必要なモジュールを有効化
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod proxy_wstunnel  # WebSocket対応
sudo a2enmod headers
sudo a2enmod rewrite

# Apacheを再起動
sudo systemctl restart apache2
```

## 2. 基本的なリバースプロキシ設定

### /etc/apache2/sites-available/segmentation-tool.conf

```apache
<VirtualHost *:80>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com
    
    # ログ設定
    ErrorLog ${APACHE_LOG_DIR}/segmentation-tool-error.log
    CustomLog ${APACHE_LOG_DIR}/segmentation-tool-access.log combined
    
    # プロキシ設定
    ProxyPreserveHost On
    ProxyRequests Off
    
    # バックエンドAPI
    ProxyPass /api/ http://localhost:8000/api/
    ProxyPassReverse /api/ http://localhost:8000/api/
    
    # 静的ファイル（アップロード画像など）
    ProxyPass /uploads/ http://localhost:8000/uploads/
    ProxyPassReverse /uploads/ http://localhost:8000/uploads/
    
    # APIドキュメント
    ProxyPass /docs http://localhost:8000/docs
    ProxyPassReverse /docs http://localhost:8000/docs
    ProxyPass /redoc http://localhost:8000/redoc
    ProxyPassReverse /redoc http://localhost:8000/redoc
    ProxyPass /openapi.json http://localhost:8000/openapi.json
    ProxyPassReverse /openapi.json http://localhost:8000/openapi.json
    
    # ヘルスチェック
    ProxyPass /health http://localhost:8000/health
    ProxyPassReverse /health http://localhost:8000/health
    
    # フロントエンド（React）
    ProxyPass / http://localhost:3000/
    ProxyPassReverse / http://localhost:3000/
    
    # WebSocket対応（React開発サーバー用）
    RewriteEngine On
    RewriteCond %{HTTP:Upgrade} websocket [NC]
    RewriteCond %{HTTP:Connection} upgrade [NC]
    RewriteRule ^/?(.*) "ws://localhost:3000/$1" [P,L]
    
    # ヘッダー設定
    <LocationMatch "/">
        Header set X-Forwarded-Proto "http"
    </LocationMatch>
</VirtualHost>
```

## 3. HTTPS対応設定（推奨）

### /etc/apache2/sites-available/segmentation-tool-ssl.conf

```apache
<VirtualHost *:443>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com
    
    # SSL設定
    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/yourdomain.crt
    SSLCertificateKeyFile /etc/ssl/private/yourdomain.key
    SSLCertificateChainFile /etc/ssl/certs/yourdomain-ca.crt
    
    # セキュリティヘッダー
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-XSS-Protection "1; mode=block"
    
    # ログ設定
    ErrorLog ${APACHE_LOG_DIR}/segmentation-tool-ssl-error.log
    CustomLog ${APACHE_LOG_DIR}/segmentation-tool-ssl-access.log combined
    
    # プロキシ設定
    ProxyPreserveHost On
    ProxyRequests Off
    SSLProxyEngine On
    
    # バックエンドAPI
    ProxyPass /api/ http://localhost:8000/api/
    ProxyPassReverse /api/ http://localhost:8000/api/
    
    # 静的ファイル
    ProxyPass /uploads/ http://localhost:8000/uploads/
    ProxyPassReverse /uploads/ http://localhost:8000/uploads/
    
    # APIドキュメント
    ProxyPass /docs http://localhost:8000/docs
    ProxyPassReverse /docs http://localhost:8000/docs
    ProxyPass /redoc http://localhost:8000/redoc
    ProxyPassReverse /redoc http://localhost:8000/redoc
    ProxyPass /openapi.json http://localhost:8000/openapi.json
    ProxyPassReverse /openapi.json http://localhost:8000/openapi.json
    
    # フロントエンド
    ProxyPass / http://localhost:3000/
    ProxyPassReverse / http://localhost:3000/
    
    # WebSocket対応
    RewriteEngine On
    RewriteCond %{HTTP:Upgrade} websocket [NC]
    RewriteCond %{HTTP:Connection} upgrade [NC]
    RewriteRule ^/?(.*) "ws://localhost:3000/$1" [P,L]
    
    # ヘッダー設定
    <LocationMatch "/">
        Header set X-Forwarded-Proto "https"
    </LocationMatch>
</VirtualHost>

# HTTPからHTTPSへのリダイレクト
<VirtualHost *:80>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com
    Redirect permanent / https://yourdomain.com/
</VirtualHost>
```

## 4. サブディレクトリでの公開

アプリケーションをサブディレクトリ（例: /segmentation-tool/）で公開する場合：

### /etc/apache2/sites-available/default-ssl.conf に追加

```apache
# 既存のVirtualHost内に追加
<VirtualHost *:443>
    # ... 既存の設定 ...
    
    # セグメンテーションツール
    <Location /segmentation-tool>
        ProxyPass http://localhost:3000
        ProxyPassReverse http://localhost:3000
    </Location>
    
    <Location /segmentation-tool/api>
        ProxyPass http://localhost:8000/api
        ProxyPassReverse http://localhost:8000/api
    </Location>
    
    <Location /segmentation-tool/uploads>
        ProxyPass http://localhost:8000/uploads
        ProxyPassReverse http://localhost:8000/uploads
    </Location>
    
    # WebSocket
    <Location /segmentation-tool/ws>
        ProxyPass ws://localhost:3000/ws
        ProxyPassReverse ws://localhost:3000/ws
    </Location>
</VirtualHost>
```

## 5. 環境変数の調整

サブディレクトリで公開する場合は、環境変数の調整が必要です：

### backend/.env
```env
# APIのベースパスを設定
API_BASE_PATH=/segmentation-tool/api
```

### frontend/.env
```env
# APIとPublic URLの設定
REACT_APP_API_URL=https://yourdomain.com/segmentation-tool/api
REACT_APP_WS_URL=wss://yourdomain.com/segmentation-tool/ws
PUBLIC_URL=/segmentation-tool
```

## 6. Docker Compose設定の調整

### docker-compose.yml（本番用）
```yaml
services:
  backend:
    environment:
      - BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
      - FORWARDED_ALLOW_IPS=*
  
  frontend:
    environment:
      - REACT_APP_API_URL=https://yourdomain.com/api
      - REACT_APP_WS_URL=wss://yourdomain.com/ws
```

## 7. 設定の有効化と確認

```bash
# 設定ファイルの文法チェック
sudo apache2ctl configtest

# サイトを有効化
sudo a2ensite segmentation-tool.conf
sudo a2ensite segmentation-tool-ssl.conf

# Apacheを再起動
sudo systemctl reload apache2

# ログの確認
sudo tail -f /var/log/apache2/segmentation-tool-*.log
```

## 8. セキュリティ考慮事項

### レート制限の追加
```apache
# mod_ratelimitを使用
<Location /api/>
    SetOutputFilter RATE_LIMIT
    SetEnv rate-limit 1000
</Location>
```

### IPアクセス制限
```apache
<Location /api/admin>
    Require ip 192.168.1.0/24
    Require ip 10.0.0.0/8
</Location>
```

### Basic認証の追加（開発環境）
```apache
<Location />
    AuthType Basic
    AuthName "Restricted Content"
    AuthUserFile /etc/apache2/.htpasswd
    Require valid-user
</Location>
```

## 9. パフォーマンス最適化

### 静的ファイルのキャッシュ
```apache
<LocationMatch "\.(jpg|jpeg|png|gif|ico|css|js)$">
    Header set Cache-Control "max-age=31536000, public"
</LocationMatch>
```

### 圧縮の有効化
```apache
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript application/json
</IfModule>
```

### プロキシキャッシュ
```apache
<IfModule mod_cache.c>
    CacheEnable disk /uploads/
    CacheRoot /var/cache/apache2/proxy
    CacheMaxFileSize 10000000
</IfModule>
```

## 10. トラブルシューティング

### 503 Service Unavailable
```bash
# Dockerコンテナが起動しているか確認
docker-compose ps

# ポートが正しくリッスンしているか確認
netstat -tlnp | grep -E '3000|8000'
```

### WebSocketエラー
```bash
# mod_proxy_wstunnelが有効か確認
apache2ctl -M | grep proxy_wstunnel

# ブラウザのコンソールでWebSocket接続を確認
```

### CORS エラー
```bash
# バックエンドの環境変数を確認
docker exec segmentation_backend env | grep CORS

# Apacheのヘッダー設定を追加
Header always set Access-Control-Allow-Origin "https://yourdomain.com"
```

## まとめ

この設定により、Apache2リバースプロキシ経由でセグメンテーションデータセット作成ツールを安全に公開できます。本番環境では必ずHTTPSを使用し、適切なセキュリティ対策を実施してください。