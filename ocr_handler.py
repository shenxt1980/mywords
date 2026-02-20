# -*- coding: utf-8 -*-
"""
OCR处理模块 - 从图片中识别文字
使用 EasyOCR 库，支持中英文识别，纯Python实现，无需额外安装软件
"""

import os
import re
from typing import List, Optional
import base64
from io import BytesIO

# OCR库导入状态
OCR_AVAILABLE = False
OCR_ERROR_MSG = ""

try:
    import easyocr
    OCR_AVAILABLE = True
except ImportError as e:
    OCR_ERROR_MSG = f"EasyOCR未安装，请运行: pip install easyocr。错误: {e}"
except Exception as e:
    OCR_ERROR_MSG = f"EasyOCR加载失败: {e}"


class OCRHandler:
    """OCR文字识别处理器"""
    
    def __init__(self):
        """初始化OCR阅读器"""
        self.reader = None
        self._initialized = False
        self._init_error = None
    
    def _lazy_init(self):
        """延迟初始化OCR阅读器（首次使用时才加载）"""
        if self._initialized:
            return self.reader is not None
        
        self._initialized = True
        
        if not OCR_AVAILABLE:
            self._init_error = OCR_ERROR_MSG
            return False
        
        try:
            # 创建EasyOCR阅读器，只识别英文（更稳定）
            # gpu=False 使用CPU模式，避免GPU相关问题
            self.reader = easyocr.Reader(
                ['en'],
                gpu=False,
                download_enabled=True,
                verbose=False
            )
            return True
        except Exception as e:
            self._init_error = f"OCR初始化失败: {e}"
            print(self._init_error)
            return False
    
    def is_available(self) -> tuple:
        """
        检查OCR是否可用
        
        返回:
            tuple: (是否可用, 错误信息)
        """
        if not self._initialized:
            self._lazy_init()
        
        if self.reader is not None:
            return True, ""
        else:
            return False, self._init_error or "OCR未初始化"
    
    def recognize_image(self, image_path: str) -> tuple:
        """
        识别图片中的文字
        
        参数:
            image_path: 图片文件路径
        
        返回:
            tuple: (成功标志, 识别结果文本或错误信息)
        """
        # 延迟初始化
        if not self._lazy_init():
            return False, self._init_error or "OCR未初始化"
        
        if not os.path.exists(image_path):
            return False, f"图片文件不存在: {image_path}"
        
        try:
            # 使用PIL和numpy读取图片，更可靠
            from PIL import Image
            import numpy as np
            
            # 打开图片
            img = Image.open(image_path)
            
            # 转换为RGB模式（处理RGBA等格式）
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 转换为numpy数组
            img_array = np.array(img)
            
            # 检查图片是否有效
            if img_array is None or img_array.size == 0:
                return False, "图片读取失败，图片可能损坏"
            
            # 识别图片
            results = self.reader.readtext(img_array, detail=0)
            
            if not results:
                return True, ""  # 图片中没有检测到文字
            
            # 将识别结果合并为文本
            full_text = "\n".join(results)
            return True, full_text
            
        except Exception as e:
            error_msg = f"图片识别失败: {e}"
            print(error_msg)
            return False, error_msg
    
    def recognize_bytes(self, image_bytes: bytes) -> tuple:
        """
        识别字节数据中的图片文字
        
        参数:
            image_bytes: 图片的字节数据
        
        返回:
            tuple: (成功标志, 识别结果文本或错误信息)
        """
        if not self._lazy_init():
            return False, self._init_error or "OCR未初始化"
        
        try:
            # 将字节转换为numpy数组
            import numpy as np
            from PIL import Image
            
            # 使用PIL打开图片
            image = Image.open(BytesIO(image_bytes))
            # 转换为numpy数组
            image_array = np.array(image)
            
            # 识别图片
            results = self.reader.readtext(image_array, detail=0)
            
            if not results:
                return True, ""
            
            full_text = "\n".join(results)
            return True, full_text
            
        except Exception as e:
            error_msg = f"图片识别失败: {e}"
            print(error_msg)
            return False, error_msg
    
    def extract_english_words(self, text: str) -> List[str]:
        """
        从文本中提取英文单词
        
        参数:
            text: 输入文本
        
        返回:
            List[str]: 英文单词列表（去重、排序）
        """
        # 使用正则表达式匹配英文单词
        # 匹配由字母、连字符、撇号组成的单词
        pattern = r"[a-zA-Z]+(?:[-'][a-zA-Z]+)*"
        words = re.findall(pattern, text)
        
        # 转小写，去重，排序
        unique_words = sorted(set(word.lower() for word in words if len(word) > 1))
        
        return unique_words
    
    def extract_all_words(self, text: str) -> List[dict]:
        """
        从文本中提取所有单词（包括中英文混合）
        
        参数:
            text: 输入文本
        
        返回:
            List[dict]: 单词信息列表
        """
        words_info = []
        
        # 提取英文单词
        english_pattern = r"[a-zA-Z]+(?:[-'][a-zA-Z]+)*"
        english_words = re.findall(english_pattern, text)
        
        for word in english_words:
            if len(word) > 1:  # 过滤单字母
                words_info.append({
                    "text": word,
                    "type": "english",
                    "lower": word.lower()
                })
        
        # 提取中文词汇（简单的单字和双字词）
        chinese_pattern = r"[\u4e00-\u9fff]+"
        chinese_words = re.findall(chinese_pattern, text)
        
        for word in chinese_words:
            if len(word) >= 1:
                words_info.append({
                    "text": word,
                    "type": "chinese",
                    "lower": word
                })
        
        # 按原文顺序去重
        seen = set()
        unique_words = []
        for w in words_info:
            key = w["lower"]
            if key not in seen:
                seen.add(key)
                unique_words.append(w)
        
        return unique_words


def extract_words_from_text(text: str) -> List[str]:
    """
    从文本中提取英文单词的便捷函数
    
    参数:
        text: 输入文本
    
    返回:
        List[str]: 英文单词列表
    """
    handler = OCRHandler()
    return handler.extract_english_words(text)


def extract_words_smart(text: str) -> List[dict]:
    """
    智能提取文本中的所有单词
    
    参数:
        text: 输入文本
    
    返回:
        List[dict]: 单词信息列表
    """
    handler = OCRHandler()
    return handler.extract_all_words(text)


# 创建全局OCR实例
ocr_handler = OCRHandler()
