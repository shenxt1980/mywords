# -*- coding: utf-8 -*-
"""
背诵复习页面 - 简化版
"""

import os
import random
import flet as ft

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db


class ReviewPage:
    """背诵复习页面"""
    
    def __init__(self, page: ft.Page, on_navigate=None):
        self.page = page
        self.words = []
        self.index = 0
        self.show_meaning = False
    
    def build(self):
        title = ft.Text("背诵复习", size=24, weight=ft.FontWeight.W_BOLD)
        
        # 设置
        self.count_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("10"),
                ft.dropdown.Option("20"),
                ft.dropdown.Option("30"),
            ],
            value="10",
            width=100,
        )
        
        start_btn = ft.ElevatedButton("开始浏览模式", on_click=self.start_browse, bgcolor="blue", color="white")
        next_btn = ft.ElevatedButton("下一个", on_click=self.next_word)
        show_btn = ft.ElevatedButton("显示含义", on_click=self.show_answer)
        
        # 单词显示
        self.word_text = ft.Text("", size=28, weight=ft.FontWeight.W_BOLD, color="blue")
        self.meaning_text = ft.Text("", size=18, color="green", visible=False)
        self.progress_text = ft.Text("", color="grey")
        self.status_text = ft.Text("")
        
        return ft.Column([
            title,
            ft.Divider(),
            ft.Row([ft.Text("数量:"), self.count_dropdown, start_btn]),
            ft.Divider(),
            ft.Container(height=30),
            self.progress_text,
            ft.Container(height=20),
            self.word_text,
            ft.Container(height=10),
            self.meaning_text,
            ft.Container(height=30),
            ft.Row([show_btn, next_btn]),
            self.status_text,
        ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
    
    def start_browse(self, e):
        count = int(self.count_dropdown.value)
        self.words = db.get_words_for_review("random", count)
        
        if not self.words:
            self.status_text.value = "没有单词可背诵，请先添加"
            self.status_text.color = "red"
            self.page.update()
            return
        
        self.index = 0
        self.show_meaning = False
        self.show_current()
        self.status_text.value = f"开始背诵，共{len(self.words)}个单词"
        self.status_text.color = "green"
        self.page.update()
    
    def show_current(self):
        if self.index >= len(self.words):
            self.word_text.value = "背诵完成!"
            self.meaning_text.value = ""
            self.progress_text.value = ""
            return
        
        w = self.words[self.index]
        self.word_text.value = w['word']
        self.meaning_text.value = w.get('meaning') or '（待补充）'
        self.meaning_text.visible = False
        self.show_meaning = False
        self.progress_text.value = f"{self.index + 1} / {len(self.words)}"
        self.page.update()
    
    def show_answer(self, e):
        self.meaning_text.visible = True
        self.show_meaning = True
        self.page.update()
    
    def next_word(self, e):
        self.index += 1
        if self.index >= len(self.words):
            # 完成
            db.increment_recitation_count([w['id'] for w in self.words])
            self.word_text.value = "背诵完成!"
            self.meaning_text.value = f"共背诵{len(self.words)}个单词"
            self.meaning_text.visible = True
            self.progress_text.value = ""
            self.status_text.value = "背诵完成!"
            self.status_text.color = "green"
        else:
            self.show_current()
        
        self.page.update()
