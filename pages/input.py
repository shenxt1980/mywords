# -*- coding: utf-8 -*-
"""
单词采集页面 - 简化版
"""

import os
import re
import flet as ft

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db


def extract_english_words(text: str):
    """从文本中提取英文单词"""
    pattern = r"[a-zA-Z]+(?:[-'][a-zA-Z]+)*"
    words = re.findall(pattern, text)
    unique_words = sorted(set(word.lower() for word in words if len(word) > 1))
    return unique_words


class InputPage:
    """单词采集页面"""
    
    def __init__(self, page: ft.Page, on_navigate=None):
        self.page = page
        self.extracted_words = []
        self.selected_words = set()
    
    def build(self):
        # 标题
        title = ft.Text("单词采集", size=24, weight=ft.FontWeight.BOLD)
        
        # 文本输入
        self.text_input = ft.TextField(
            label="在此粘贴或输入英文文本",
            multiline=True,
            min_lines=5,
            max_lines=10,
            hint_text="例如: Hello world, this is a test sentence.",
        )
        
        # 提取按钮
        self.extract_btn = ft.ElevatedButton(
            "提取单词",
            on_click=self.on_extract_click,
        )
        
        # 清除按钮
        self.clear_btn = ft.OutlinedButton(
            "清除",
            on_click=self.on_clear_click,
        )
        
        # 状态文本
        self.status_text = ft.Text("", color="green")
        
        # 单词显示区域
        self.word_list = ft.Column(scroll=ft.ScrollMode.AUTO, height=200)
        
        # 选中计数
        self.count_text = ft.Text("已选中: 0 个")
        
        # 提交按钮
        self.submit_btn = ft.ElevatedButton(
            "提交选中单词",
            on_click=self.on_submit_click,
            bgcolor="purple",
            color="white",
        )
        
        # 全选按钮
        self.select_all_btn = ft.TextButton("全选", on_click=self.on_select_all)
        
        # 取消全选按钮
        self.deselect_btn = ft.TextButton("取消全选", on_click=self.on_deselect_all)
        
        # 布局
        return ft.Column(
            controls=[
                title,
                ft.Divider(),
                self.text_input,
                ft.Row([self.extract_btn, self.clear_btn]),
                self.status_text,
                ft.Divider(),
                ft.Text("提取的单词 (点击选择):"),
                self.word_list,
                ft.Row([self.select_all_btn, self.deselect_btn]),
                ft.Row([self.count_text, self.submit_btn]),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
    
    def on_extract_click(self, e):
        """提取单词按钮点击"""
        text = self.text_input.value
        
        if not text or not text.strip():
            self.status_text.value = "请先输入文本!"
            self.status_text.color = "red"
            self.page.update()
            return
        
        # 提取单词
        self.extracted_words = extract_english_words(text)
        
        if not self.extracted_words:
            self.status_text.value = "未找到英文单词!"
            self.status_text.color = "orange"
            self.page.update()
            return
        
        # 显示单词
        self.selected_words.clear()
        self.word_list.controls.clear()
        
        for word in self.extracted_words:
            chip = ft.Chip(
                label=ft.Text(word),
                on_click=lambda e, w=word: self.on_word_click(w),
            )
            self.word_list.controls.append(chip)
        
        self.status_text.value = f"已提取 {len(self.extracted_words)} 个单词"
        self.status_text.color = "green"
        self.count_text.value = "已选中: 0 个"
        
        self.page.update()
    
    def on_word_click(self, word):
        """单词点击"""
        if word in self.selected_words:
            self.selected_words.remove(word)
        else:
            self.selected_words.add(word)
        
        self.count_text.value = f"已选中: {len(self.selected_words)} 个"
        self.page.update()
    
    def on_select_all(self, e):
        """全选"""
        self.selected_words = set(self.extracted_words)
        self.count_text.value = f"已选中: {len(self.selected_words)} 个"
        self.page.update()
    
    def on_deselect_all(self, e):
        """取消全选"""
        self.selected_words.clear()
        self.count_text.value = "已选中: 0 个"
        self.page.update()
    
    def on_submit_click(self, e):
        """提交单词"""
        if not self.selected_words:
            self.status_text.value = "请先选择单词!"
            self.status_text.color = "red"
            self.page.update()
            return
        
        # 保存到数据库
        words_list = list(self.selected_words)
        new_count, update_count = db.batch_add_words(words_list)
        
        self.status_text.value = f"成功添加 {new_count} 个新单词, 更新 {update_count} 个"
        self.status_text.color = "green"
        self.selected_words.clear()
        self.count_text.value = "已选中: 0 个"
        
        self.page.update()
    
    def on_clear_click(self, e):
        """清除"""
        self.text_input.value = ""
        self.extracted_words = []
        self.selected_words.clear()
        self.word_list.controls.clear()
        self.status_text.value = ""
        self.count_text.value = "已选中: 0 个"
        self.page.update()
