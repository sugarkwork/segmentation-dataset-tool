-- サンプルデータ（開発・テスト用）
-- このファイルは開発環境でのみ使用してください

-- テストユーザーの作成
INSERT INTO users (username, email, hashed_password, full_name, is_superuser, oauth_provider) VALUES
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj7D7QmH9D6G', 'Administrator', TRUE, 'local'),
('testuser', 'test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj7D7QmH9D6G', 'Test User', FALSE, 'local'),
('demo', 'demo@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj7D7QmH9D6G', 'Demo User', FALSE, 'local');

-- サンプルプロジェクトの作成
INSERT INTO projects (name, description, owner_id, train_split, val_split, test_split) VALUES
('サンプルプロジェクト', 'YOLOv8セグメンテーション学習用のサンプルプロジェクト', 1, 0.70, 0.20, 0.10),
('車両検出プロジェクト', '車両セグメンテーション用データセット', 2, 0.80, 0.20, 0.00),
('人物検出プロジェクト', '人物セグメンテーション用データセット', 1, 0.75, 0.25, 0.00);

-- サンプルクラス定義
INSERT INTO class_definitions (name, display_name, description, color, class_index, project_id) VALUES
-- プロジェクト1のクラス
('person', '人物', '人間の全身', '#FF0000', 0, 1),
('car', '車', '乗用車', '#00FF00', 1, 1),
('bicycle', '自転車', '自転車', '#0000FF', 2, 1),
('dog', '犬', '犬', '#FFFF00', 3, 1),
('cat', '猫', '猫', '#FF00FF', 4, 1),

-- プロジェクト2のクラス（車両）
('sedan', 'セダン', 'セダン型乗用車', '#FF4444', 0, 2),
('suv', 'SUV', 'SUV車', '#44FF44', 1, 2),
('truck', 'トラック', '貨物車', '#4444FF', 2, 2),
('bus', 'バス', 'バス', '#FFAA00', 3, 2),
('motorcycle', 'オートバイ', 'オートバイ', '#AA00FF', 4, 2),

-- プロジェクト3のクラス（人物）
('person_full', '人物（全身）', '人物の全身', '#FF6666', 0, 3),
('person_upper', '人物（上半身）', '人物の上半身', '#66FF66', 1, 3),
('face', '顔', '人物の顔', '#6666FF', 2, 3),
('hand', '手', '人物の手', '#FFFF66', 3, 3);

-- サンプル画像メタデータ（実際の画像ファイルは含まれていません）
INSERT INTO images (filename, original_filename, file_path, file_size, width, height, format, project_id, dataset_type) VALUES
-- プロジェクト1の画像
('sample_001.jpg', 'street_scene_001.jpg', '/uploads/1/sample_001.jpg', 1024000, 1920, 1080, 'jpg', 1, 'train'),
('sample_002.jpg', 'street_scene_002.jpg', '/uploads/1/sample_002.jpg', 956000, 1920, 1080, 'jpg', 1, 'train'),
('sample_003.jpg', 'street_scene_003.jpg', '/uploads/1/sample_003.jpg', 1156000, 1920, 1080, 'jpg', 1, 'val'),

-- プロジェクト2の画像
('car_001.jpg', 'parking_lot_001.jpg', '/uploads/2/car_001.jpg', 856000, 1280, 720, 'jpg', 2, 'train'),
('car_002.jpg', 'highway_001.jpg', '/uploads/2/car_002.jpg', 1200000, 1920, 1080, 'jpg', 2, 'train'),

-- プロジェクト3の画像
('people_001.jpg', 'crowd_scene_001.jpg', '/uploads/3/people_001.jpg', 2048000, 3840, 2160, 'jpg', 3, 'train');

-- 使用方法の説明
-- パスワード: 'password' （全ユーザー共通）
-- 
-- 1. Webアプリケーション（http://localhost:3000）にアクセス
-- 2. 上記のユーザー名（admin, testuser, demo）のいずれかでログイン
-- 3. サンプルプロジェクトを選択して編集開始
-- 4. 実際の画像をアップロードしてセグメンテーション作業を開始