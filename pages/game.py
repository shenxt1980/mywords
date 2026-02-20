# -*- coding: utf-8 -*-
"""
连连看游戏页面
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
        self.blocks = []  # 保存打乱后的方块
        self.selected_idx = None
        self.score = 0
        self.matched = 0
    
    def build(self):
        title = ft.Text("连连看游戏", size=24, weight=ft.FontWeight.BOLD)
        
        self.count_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("4"),
                ft.dropdown.Option("6"),
            ],
            value="4",
            width=80,
        )
        
        start_btn = ft.ElevatedButton("开始游戏", on_click=self.start_game, bgcolor="green", color="white")
        
        self.score_text = ft.Text("得分: 0", size=18, weight=ft.FontWeight.BOLD, color="purple")
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
        self.selected_idx = None
        
        self.score_text.value = "得分: 0"
        self.progress_text.value = f"配对: 0 / {count}"
        self.status_text.value = "游戏开始! 点击方块匹配英文和中文"
        self.status_text.color = "green"
        
        self.display_game()
    
    def display_game(self):
        self.game_area.controls.clear()
        
        # 如果是首次显示，创建方块
        if not self.blocks:
            self.blocks = []
            for w in self.words:
                self.blocks.append({
                    'text': w['word'],
                    'pair_id': w['id'],
                    'type': 'en',
                    'matched': False
                })
                meaning = w['meaning']
                if len(meaning) > 15:
                    meaning = meaning[:15] + "..."
                self.blocks.append({
                    'text': meaning,
                    'pair_id': w['id'],
                    'type': 'cn',
                    'matched': False
                })
            random.shuffle(self.blocks)
        
        # 创建显示
        rows = []
        row_controls = []
        
        for i, b in enumerate(self.blocks):
            if b['matched']:
                continue
            
            is_selected = (self.selected_idx == i)
            bgcolor = "purple" if is_selected else ("blue" if b['type'] == 'en' else "green")
            
            btn = ft.Container(
                content=ft.Text(b['text'], size=11, text_align=ft.TextAlign.CENTER, color="white"),
                bgcolor=bgcolor,
                border_radius=8,
                padding=10,
                width=100,
                height=50,
                on_click=lambda e, idx=i: self.on_block_click(idx),
            )
            row_controls.append(btn)
            
            if len(row_controls) >= 4:
                rows.append(ft.Row(row_controls, alignment=ft.MainAxisAlignment.CENTER, spacing=10))
                row_controls = []
        
        if row_controls:
            while len(row_controls) < 4:
                row_controls.append(ft.Container(width=100, height=50))
            rows.append(ft.Row(row_controls, alignment=ft.MainAxisAlignment.CENTER, spacing=10))
        
        self.game_area.controls.clear()
        for r in rows:
            self.game_area.controls.append(r)
        
        self.page.update()
    
    def on_block_click(self, idx):
        if self.blocks[idx]['matched']:
            return
        
        if self.selected_idx is None:
            # 第一次选择
            self.selected_idx = idx
            self.display_game()
        elif self.selected_idx == idx:
            # 取消选择
            self.selected_idx = None
            self.display_game()
        else:
            # 第二次选择，检查匹配
            block1 = self.blocks[self.selected_idx]
            block2 = self.blocks[idx]
            
            # 匹配条件：pair_id相同 且 type不同
            if block1['pair_id'] == block2['pair_id'] and block1['type'] != block2['type']:
                # 匹配成功
                block1['matched'] = True
                block2['matched'] = True
                self.score += 10
                self.matched += 1
                self.status_text.value = f"匹配正确! +10分"
                self.status_text.color = "green"
                
                if self.matched >= len(self.words):
                    self.status_text.value = f"恭喜完成! 得分: {self.score}"
                    self.status_text.color = "purple"
                    # 记录背诵次数
                    word_ids = [w['id'] for w in self.words]
                    db.increment_recitation_count(word_ids)
            else:
                # 匹配失败
                self.score = max(0, self.score - 2)
                self.status_text.value = f"匹配失败 -2分 (正确: {block1['text']} ↔ ?)"
                self.status_text.color = "red"
            
            self.selected_idx = None
            self.score_text.value = f"得分: {self.score}"
            self.progress_text.value = f"配对: {self.matched} / {len(self.words)}"
            self.display_game()
