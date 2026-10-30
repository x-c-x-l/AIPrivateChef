-- 创建收藏表
CREATE TABLE IF NOT EXISTS recipe_favorites (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    thread_id VARCHAR(100) NOT NULL,
    message_id INT,
    recipe_name VARCHAR(200),
    recipe_content TEXT,
    recipe_image VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_thread_id (thread_id),
    INDEX idx_message_id (message_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='食谱收藏表';

-- 如果需要完整的数据库初始化，可以运行以下SQL：

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    status INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 会话记录表
CREATE TABLE IF NOT EXISTS agent_record (
    id VARCHAR(100) PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(50),
    content TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会话记录表';

-- 消息表
CREATE TABLE IF NOT EXISTS agent_message (
    id INT PRIMARY KEY AUTO_INCREMENT,
    thread_id VARCHAR(100) NOT NULL,
    user_id INT NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT,
    image_url VARCHAR(500),
    message_type VARCHAR(20) DEFAULT 'text',
    status INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_thread_id (thread_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='消息表';
