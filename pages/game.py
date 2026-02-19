# -*- coding: utf-8 -*-
"""
连连看游戏页面 - 简化版
"""

import os
import random
import flet as ft

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db


class GamePage:
    """连连看游戏页面"""
    
    def __init__(self, page: ft.Page, on_navigate=None):
        self.page = page
        self.words = []
        self.selected = None
        self.score = 0
        self.matched = 0
    
    def build(self):
        title = ft.Text("连连看游戏", size=24, weight=ft.FontWeight.W_BOLD)
        
        self.count_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("4"),
                ft.dropdown.Option("6"),
            ],
            value="4",
            width=80,
        )
        
        start_btn = ft.ElevatedButton("开始游戏", on_click=self.start_game, bgcolor="green", color="white")
        
        self.score_text = ft.Text("得分: 0", size=18, weight=ft.FontWeight.W_BOLD, color="purple")
        self.progress_text = ft.Text("", color="grey")
        self.status_text = ft.Text("")
        
        self.game_area = ft.Column(scroll=ft.ScrollMode.AUTO)
        
        return ft.Column([
            title,
            ft.Divider(),
            ft.Row([ft.Text("配对数:"), self.count_dropdown, start_btn]),
            ft.Row([self.score_text, self.progress_text]),
            ft.Divider(),
            self.game_area,
            self.status_text,
        ], scroll=ft.ScrollMode.AUTO, expand=True)
    
    def start_game(self, e):
        count = int(self.count_dropdown.value)
        
        all_words = db.get_all_words("random")
        words_with_meaning = [w for w in all_words if w.get('meaning')]
        
        if len(words_with_meaning) < count:
            self.status_text.value = f"需要至少{count}个有含义的单词"
            self.status_text.color = "red"
            self.page.update()
            return
        
        self.words = random.sample(words_with_meaning, count)
        self.score = 0
        self.matched = 0
        self.selected = None
        
        self.score_text.value = "得分: 0"
        self.progress_text.value = f"配对: 0 / {count}"
        self.status_text.value = "游戏开始! 点击方块匹配"
        self.status_text.color = "green"
        
        self.display_game()
    
    def display_game(self):
        self.game_area.controls.clear()
        
        # 创建所有方块
        blocks = []
        for w in self.words:
            blocks.append({'text': w['word'], 'pair': w['id'], 'type': 'en', 'matched': False})
            meaning = w['meaning'][:12] if len(w['meaning']) > 12 else w['meaning']
            blocks.append({'text': meaning, 'pair': w['id'], 'type': 'cn', 'matched': False})
        
        random.shuffle(blocks)
        
        rows = []
        row_controls = []
        
        for i, b in enumerate(blocks):
            btn = ft.Container(
                content=ft.Text(b['text'], size=11, text_align=ft.TextAlign.CENTER),
                bgcolor="blue" if b['type'] == 'en' else "green",
                border_radius=8,
                padding=10,
                width=100,
                height=50,
                visible=not b['matched'],
                on_click=lambda e, idx=i: self.on_block_click(idx),
            )
            b['button'] = btn
            row_controls.append(btn)
            
            if len(row_controls) >= 4:
                rows.append(ft.Row(row_controls, alignment=ft.MainAxisAlignment.CENTER))
                row_controls = []
        
        if row_controls:
            rows.append(ft.Row(row_controls, alignment=ft.MainAxisAlignment.CENTER))
        
        for r in rows:
            self.game_area.controls.append(r)
        
        self.page.update()
    
    def on_block_click(self, idx):
        # 找到点击的方块
        blocks = []
        for w in self.words:
            blocks.append({'text': w['word'], 'pair': w['id'], 'type': 'en'})
            blocks.append({'text': w['meaning'][:12], 'pair': w['id'], 'type': 'cn'})
        
        if self.selected is None:
            self.selected = idx
        else:
            if idx != self.selected:
                # 检查匹配
                block1 = blocks[self.selected]
                block2 = blocks[idx]
                
                if block1['pair'] == block2['pair'] and block1['type'] != block2['type']:
                    # 匹配成功
                    self.score += 10
                    self.matched += 1
                    self.status_text.value = "匹配正确! +10分"
                    self.status_text.color = "green"
                    
                    # 更新显示
                    self.display_game()
                    
                    if self.matched >= len(self.words):
                        self.status_text.value = f"游戏完成! 得分: {self.score}"
                        self.status_text.color = "purple"
                else:
                    self.score = max(0, self.score - 2)
                    self.status_text.value = "匹配失败 -2分"
                    self.status_text.color = "red"
                
                self.score_text.value = f"得分: {self.score}"
                self.progress_text.value = f"配对: {self.matched} / {len(self.words)}"
            
            self.selected = None
        
        self.page.update()
