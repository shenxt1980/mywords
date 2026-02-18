# -*- coding: utf-8 -*-
"""
数据库模块 - 管理单词的存储和查询
使用 SQLite 作为本地数据库，简单易用，无需额外配置
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# 数据库文件路径，存放在项目目录下
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vocabulary.db")


class VocabularyDB:
    """单词数据库管理类"""
    
    def __init__(self):
        """初始化数据库连接，如果表不存在则创建"""
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """连接到SQLite数据库"""
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        # 启用外键约束
        self.conn.execute("PRAGMA foreign_keys = ON")
        # 设置返回字典格式的结果
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def _create_tables(self):
        """创建数据库表结构"""
        # 单词主表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL UNIQUE,
                meaning TEXT,
                phonetic TEXT,
                part_of_speech TEXT,
                example_sentence TEXT,
                selection_count INTEGER DEFAULT 1,
                print_count INTEGER DEFAULT 0,
                recitation_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引以加快查询速度
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_word ON words(word)
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_selection_count ON words(selection_count DESC)
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_print_count ON words(print_count ASC)
        ''')
        
        self.conn.commit()
    
    def add_word(self, word: str, meaning: str = "", phonetic: str = "",
                 part_of_speech: str = "", example_sentence: str = "") -> bool:
        """
        添加新单词或更新已存在单词的选择次数
        
        参数:
            word: 单词
            meaning: 中文含义
            phonetic: 音标
            part_of_speech: 词性
            example_sentence: 例句
        
        返回:
            bool: 是否成功添加
        """
        word = word.strip().lower()
        if not word:
            return False
        
        try:
            # 检查单词是否已存在
            self.cursor.execute("SELECT id FROM words WHERE word = ?", (word,))
            existing = self.cursor.fetchone()
            
            if existing:
                # 单词已存在，增加选择次数
                self.cursor.execute(
                    "UPDATE words SET selection_count = selection_count + 1, updated_at = ? WHERE word = ?",
                    (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), word)
                )
            else:
                # 插入新单词
                self.cursor.execute('''
                    INSERT INTO words (word, meaning, phonetic, part_of_speech, example_sentence)
                    VALUES (?, ?, ?, ?, ?)
                ''', (word, meaning, phonetic, part_of_speech, example_sentence))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            return False
    
    def batch_add_words(self, words: List[str]) -> Tuple[int, int]:
        """
        批量添加单词
        
        参数:
            words: 单词列表
        
        返回:
            Tuple[int, int]: (新增数量, 更新数量)
        """
        new_count = 0
        update_count = 0
        
        for word in words:
            word = word.strip().lower()
            if not word:
                continue
            
            self.cursor.execute("SELECT id FROM words WHERE word = ?", (word,))
            existing = self.cursor.fetchone()
            
            if existing:
                self.cursor.execute(
                    "UPDATE words SET selection_count = selection_count + 1 WHERE word = ?",
                    (word,)
                )
                update_count += 1
            else:
                self.cursor.execute(
                    "INSERT INTO words (word) VALUES (?)",
                    (word,)
                )
                new_count += 1
        
        self.conn.commit()
        return new_count, update_count
    
    def get_all_words(self, sort_by: str = "alphabetical") -> List[Dict]:
        """
        获取所有单词
        
        参数:
            sort_by: 排序方式
                - "alphabetical": 按字典序
                - "selection_desc": 按被选次数降序（高频词优先）
                - "print_asc": 按打印次数升序（未打印的优先）
        
        返回:
            List[Dict]: 单词列表
        """
        order_clause = {
            "alphabetical": "ORDER BY word ASC",
            "selection_desc": "ORDER BY selection_count DESC, word ASC",
            "print_asc": "ORDER BY print_count ASC, word ASC"
        }.get(sort_by, "ORDER BY word ASC")
        
        self.cursor.execute(f"SELECT * FROM words {order_clause}")
        rows = self.cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def get_word_by_id(self, word_id: int) -> Optional[Dict]:
        """根据ID获取单个单词"""
        self.cursor.execute("SELECT * FROM words WHERE id = ?", (word_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_word_by_text(self, word: str) -> Optional[Dict]:
        """根据单词文本获取单词信息"""
        self.cursor.execute("SELECT * FROM words WHERE word = ?", (word.lower(),))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_word(self, word_id: int, **kwargs) -> bool:
        """
        更新单词信息
        
        参数:
            word_id: 单词ID
            **kwargs: 要更新的字段
        
        返回:
            bool: 是否成功更新
        """
        allowed_fields = ['word', 'meaning', 'phonetic', 'part_of_speech', 'example_sentence']
        updates = []
        values = []
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if not updates:
            return False
        
        updates.append("updated_at = ?")
        values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        values.append(word_id)
        
        try:
            self.cursor.execute(
                f"UPDATE words SET {', '.join(updates)} WHERE id = ?",
                values
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"更新错误: {e}")
            return False
    
    def delete_word(self, word_id: int) -> bool:
        """删除单词"""
        try:
            self.cursor.execute("DELETE FROM words WHERE id = ?", (word_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"删除错误: {e}")
            return False
    
    def increment_print_count(self, word_ids: List[int]) -> bool:
        """增加打印次数"""
        try:
            for word_id in word_ids:
                self.cursor.execute(
                    "UPDATE words SET print_count = print_count + 1 WHERE id = ?",
                    (word_id,)
                )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"更新打印次数错误: {e}")
            return False
    
    def increment_recitation_count(self, word_ids: List[int]) -> bool:
        """增加背诵次数"""
        try:
            for word_id in word_ids:
                self.cursor.execute(
                    "UPDATE words SET recitation_count = recitation_count + 1 WHERE id = ?",
                    (word_id,)
                )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"更新背诵次数错误: {e}")
            return False
    
    def get_words_for_review(self, mode: str = "high_frequency", limit: int = 20) -> List[Dict]:
        """
        获取用于背诵的单词列表
        
        参数:
            mode: 模式
                - "high_frequency": 高频词优先
                - "random": 随机
            limit: 数量限制
        
        返回:
            List[Dict]: 单词列表
        """
        if mode == "high_frequency":
            self.cursor.execute(
                "SELECT * FROM words ORDER BY selection_count DESC, word ASC LIMIT ?",
                (limit,)
            )
        else:
            self.cursor.execute(
                "SELECT * FROM words ORDER BY RANDOM() LIMIT ?",
                (limit,)
            )
        
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        self.cursor.execute("SELECT COUNT(*) as total FROM words")
        total = self.cursor.fetchone()['total']
        
        self.cursor.execute("SELECT SUM(selection_count) as total_selections FROM words")
        total_selections = self.cursor.fetchone()['total_selections'] or 0
        
        self.cursor.execute("SELECT SUM(print_count) as total_prints FROM words")
        total_prints = self.cursor.fetchone()['total_prints'] or 0
        
        self.cursor.execute("SELECT SUM(recitation_count) as total_recitations FROM words")
        total_recitations = self.cursor.fetchone()['total_recitations'] or 0
        
        return {
            "total_words": total,
            "total_selections": total_selections,
            "total_prints": total_prints,
            "total_recitations": total_recitations
        }
    
    def search_words(self, keyword: str) -> List[Dict]:
        """搜索单词"""
        self.cursor.execute(
            "SELECT * FROM words WHERE word LIKE ? OR meaning LIKE ? ORDER BY word ASC",
            (f"%{keyword}%", f"%{keyword}%")
        )
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()


# 创建全局数据库实例
db = VocabularyDB()
