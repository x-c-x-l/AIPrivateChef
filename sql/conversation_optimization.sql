-- 多轮对话优化 - 数据库表结构

-- 1. 对话摘要表
CREATE TABLE IF NOT EXISTS conversation_summaries (
    id INT PRIMARY KEY AUTO_INCREMENT,
    thread_id VARCHAR(100) NOT NULL,
    user_id INT NOT NULL,
    summary TEXT NOT NULL COMMENT '对话摘要内容',
    key_points TEXT COMMENT '关键要点（JSON格式）',
    message_count INT DEFAULT 0 COMMENT '摘要包含的消息数量',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_thread_id (thread_id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话摘要表';

-- 2. 对话分支表
CREATE TABLE IF NOT EXISTS conversation_branches (
    id INT PRIMARY KEY AUTO_INCREMENT,
    thread_id VARCHAR(100) NOT NULL COMMENT '分支会话ID',
    parent_thread_id VARCHAR(100) NOT NULL COMMENT '父会话ID',
    branch_message_id INT NOT NULL COMMENT '分支点消息ID',
    user_id INT NOT NULL,
    branch_name VARCHAR(200) COMMENT '分支名称',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_thread_id (thread_id),
    INDEX idx_parent_thread_id (parent_thread_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话分支表';

-- 3. 消息索引表（用于搜索优化）
CREATE TABLE IF NOT EXISTS message_search_index (
    id INT PRIMARY KEY AUTO_INCREMENT,
    message_id INT NOT NULL,
    thread_id VARCHAR(100) NOT NULL,
    user_id INT NOT NULL,
    content_tokens TEXT COMMENT '分词后的内容',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_message_id (message_id),
    INDEX idx_thread_id (thread_id),
    INDEX idx_user_id (user_id),
    FULLTEXT INDEX ft_content (content_tokens)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='消息搜索索引表';

-- 4. 用户偏好表
CREATE TABLE IF NOT EXISTS user_preferences (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    dietary_restrictions TEXT COMMENT '饮食限制（JSON格式）',
    favorite_cuisines TEXT COMMENT '偏好菜系（JSON格式）',
    cooking_skill VARCHAR(20) DEFAULT 'beginner' COMMENT '烹饪水平：beginner/intermediate/advanced',
    summary_enabled TINYINT(1) DEFAULT 1 COMMENT '是否启用自动摘要',
    summary_threshold INT DEFAULT 20 COMMENT '触发摘要的消息数量阈值',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户偏好表';
