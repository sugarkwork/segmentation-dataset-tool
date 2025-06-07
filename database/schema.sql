-- セグメンテーションデータセット作成ツール データベーススキーマ
-- MariaDB 10.6+ 対応

CREATE DATABASE IF NOT EXISTS segmentation_dataset 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE segmentation_dataset;

-- ユーザーテーブル
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    avatar_url VARCHAR(500),
    
    -- OAuth fields for future integration
    github_id VARCHAR(50) UNIQUE,
    twitter_id VARCHAR(50) UNIQUE,
    oauth_provider VARCHAR(20), -- 'local', 'github', 'twitter'
    
    -- User preferences
    theme VARCHAR(20) DEFAULT 'light', -- 'light', 'dark'
    language VARCHAR(10) DEFAULT 'ja', -- 'ja', 'en'
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_github_id (github_id),
    INDEX idx_twitter_id (twitter_id)
);

-- プロジェクトテーブル
CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id INT NOT NULL,
    
    -- Dataset configuration
    train_split DECIMAL(3,2) DEFAULT 0.80,
    val_split DECIMAL(3,2) DEFAULT 0.20,
    test_split DECIMAL(3,2) DEFAULT 0.00,
    
    -- Project settings
    image_width INT DEFAULT 640,
    image_height INT DEFAULT 640,
    auto_save BOOLEAN DEFAULT TRUE,
    
    -- Export settings
    export_format VARCHAR(20) DEFAULT 'yolo',
    simplify_polygons BOOLEAN DEFAULT TRUE,
    simplify_tolerance DECIMAL(5,2) DEFAULT 2.0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_owner_id (owner_id),
    INDEX idx_created_at (created_at)
);

-- 画像テーブル
CREATE TABLE images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INT NOT NULL,
    
    -- Image properties
    width INT NOT NULL,
    height INT NOT NULL,
    format VARCHAR(10) NOT NULL,
    
    -- Dataset assignment
    dataset_type VARCHAR(10) DEFAULT 'train',
    
    -- Processing status
    is_processed BOOLEAN DEFAULT FALSE,
    has_annotations BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    thumbnail_path VARCHAR(500),
    notes TEXT,
    
    project_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project_id (project_id),
    INDEX idx_dataset_type (dataset_type),
    INDEX idx_is_processed (is_processed)
);

-- クラス定義テーブル
CREATE TABLE class_definitions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Visual properties
    color VARCHAR(7) NOT NULL, -- Hex color code
    opacity INT DEFAULT 128,   -- 0-255
    
    -- YOLO class index
    class_index INT NOT NULL,
    
    -- Display settings
    is_visible BOOLEAN DEFAULT TRUE,
    stroke_width INT DEFAULT 2,
    
    project_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE KEY uk_project_class_name (project_id, name),
    UNIQUE KEY uk_project_class_index (project_id, class_index),
    INDEX idx_project_id (project_id)
);

-- セグメンテーションテーブル
CREATE TABLE segmentations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    
    -- Canvas data (stored as base64 encoded image)
    mask_data LONGTEXT NOT NULL,
    
    -- Bounding box
    bbox_x DECIMAL(10,6),
    bbox_y DECIMAL(10,6),
    bbox_width DECIMAL(10,6),
    bbox_height DECIMAL(10,6),
    
    -- Area calculation
    area DECIMAL(15,6),
    
    -- Layer properties
    layer_index INT DEFAULT 0,
    is_visible BOOLEAN DEFAULT TRUE,
    is_locked BOOLEAN DEFAULT FALSE,
    opacity INT DEFAULT 255,
    
    -- Processing status
    is_processed BOOLEAN DEFAULT FALSE,
    needs_simplification BOOLEAN DEFAULT TRUE,
    
    image_id INT NOT NULL,
    class_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES class_definitions(id) ON DELETE CASCADE,
    INDEX idx_image_id (image_id),
    INDEX idx_class_id (class_id),
    INDEX idx_layer_index (layer_index)
);

-- アノテーションテーブル
CREATE TABLE annotations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- YOLO format data
    normalized_coordinates LONGTEXT NOT NULL,
    original_coordinates LONGTEXT,
    
    -- Polygon properties
    point_count INT NOT NULL,
    is_simplified BOOLEAN DEFAULT FALSE,
    simplification_tolerance DECIMAL(5,2),
    
    -- Quality metrics
    polygon_area DECIMAL(15,6),
    perimeter DECIMAL(15,6),
    compactness DECIMAL(8,6),
    
    -- Validation status
    is_valid BOOLEAN DEFAULT TRUE,
    validation_errors TEXT,
    
    -- Export status
    is_exported BOOLEAN DEFAULT FALSE,
    export_format VARCHAR(20),
    
    segmentation_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (segmentation_id) REFERENCES segmentations(id) ON DELETE CASCADE,
    INDEX idx_segmentation_id (segmentation_id),
    INDEX idx_is_exported (is_exported)
);

-- データベース制約追加
ALTER TABLE projects ADD CONSTRAINT chk_split_sum 
    CHECK (train_split + val_split + test_split BETWEEN 0.99 AND 1.01);

-- サンプルデータ挿入（開発用）
INSERT INTO users (username, email, hashed_password, full_name, is_superuser) VALUES
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj7D7QmH9D6G', 'Administrator', TRUE),
('testuser', 'test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj7D7QmH9D6G', 'Test User', FALSE);

-- インデックス最適化
ANALYZE TABLE users, projects, images, class_definitions, segmentations, annotations;