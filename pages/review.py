# -*- coding: utf-8 -*-
"""
背诵复习页面 - 计划模式和默写模式
"""

import os
import random
import flet as ft
from typing import List, Dict, Callable, Optional

# 导入其他模块
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db


class ReviewPage:
    """背诵复习页面"""
    
    def __init__(self, page: ft.Page, on_navigate: Callable = None):
        """
        初始化背诵复习页面
        
        参数:
            page: Flet页面对象
            on_navigate: 导航回调函数
        """
        self.page = page
        self.on_navigate = on_navigate
        
        # 状态变量
        self.review_words: List[Dict] = []  # 待背诵单词列表
        self.current_index = 0  # 当前单词索引
        self.current_word: Optional[Dict] = None  # 当前单词
        self.mode = "browse"  # 模式: browse, dictation_en, dictation_cn
        self.correct_count = 0  # 正确数量
        self.total_count = 0  # 总数量
        
        # UI组件
        self.word_display = None
        self.meaning_display = None
        self.progress_text = None
        self.status_text = None
        self.answer_input = None
    
    def build(self) -> ft.Control:
        """构建页面UI"""
        
        # 标题
        title = ft.Text(
            "背诵复习",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.PURPLE_700
        )
        
        # 模式选择
        mode_text = ft.Text("选择背诵模式:", size=14, weight=ft.FontWeight.BOLD)
        
        mode_buttons = ft.Row(
            controls=[
                ft.ElevatedButton(
                    "浏览模式",
                    icon=ft.icons.VISIBILITY,
                    on_click=lambda e: self._start_review("browse"),
                    bgcolor=ft.colors.BLUE_600,
                    color=ft.colors.WHITE,
                ),
                ft.ElevatedButton(
                    "默写（看中文写英文）",
                    icon=ft.icons.EDIT,
                    on_click=lambda e: self._start_review("dictation_en"),
                    bgcolor=ft.colors.GREEN_600,
                    color=ft.colors.WHITE,
                ),
                ft.ElevatedButton(
                    "默写（看英文写中文）",
                    icon=ft.icons.EDIT_NOTE,
                    on_click=lambda e: self._start_review("dictation_cn"),
                    bgcolor=ft.colors.ORANGE_600,
                    color=ft.colors.WHITE,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            wrap=True,
        )
        
        # 排序选择
        sort_row = ft.Row(
            controls=[
                ft.Text("排序:", size=14),
                ft.RadioGroup(
                    content=ft.Row(
                        controls=[
                            ft.Radio(value="high_frequency", label="高频词优先"),
                            ft.Radio(value="random", label="随机"),
                        ]
                    ),
                    value="high_frequency",
                    on_change=self._on_sort_change,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
        # 数量选择
        count_row = ft.Row(
            controls=[
                ft.Text("数量:", size=14),
                ft.Dropdown(
                    options=[
                        ft.dropdown.Option("10"),
                        ft.dropdown.Option("20"),
                        ft.dropdown.Option("30"),
                        ft.dropdown.Option("50"),
                        ft.dropdown.Option("100"),
                    ],
                    value="20",
                    width=100,
                    on_change=self._on_count_change,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
        self.count_dropdown = count_row.controls[1]
        self.sort_radio = sort_row.controls[1]
        
        # 进度显示
        self.progress_text = ft.Text(
            "",
            size=14,
            color=ft.colors.GREY_600,
        )
        
        # 单词显示区域
        self.word_display = ft.Container(
            content=ft.Text(
                "请选择模式开始背诵",
                size=28,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
            alignment=ft.alignment.center,
            padding=30,
            bgcolor=ft.colors.BLUE_50,
            border_radius=15,
            width=400,
            height=100,
        )
        
        # 音标显示
        self.phonetic_display = ft.Text(
            "",
            size=16,
            color=ft.colors.GREY_600,
            text_align=ft.TextAlign.CENTER,
        )
        
        # 含义显示区域
        self.meaning_display = ft.Container(
            content=ft.Text(
                "",
                size=18,
                text_align=ft.TextAlign.CENTER,
            ),
            alignment=ft.alignment.center,
            padding=20,
            bgcolor=ft.colors.GREEN_50,
            border_radius=15,
            width=400,
            height=80,
            visible=False,
        )
        
        # 答案输入框（默写模式用）
        self.answer_input = ft.TextField(
            label="输入答案",
            visible=False,
            on_submit=self._on_submit_answer,
            width=300,
        )
        
        # 结果显示
        self.result_text = ft.Text(
            "",
            size=16,
            text_align=ft.TextAlign.CENTER,
        )
        
        # 控制按钮
        control_buttons = ft.Row(
            controls=[
                ft.ElevatedButton(
                    "显示答案",
                    icon=ft.icons.VISIBILITY,
                    on_click=self._on_show_answer,
                    bgcolor=ft.colors.AMBER_600,
                    color=ft.colors.WHITE,
                    visible=True,
                ),
                ft.ElevatedButton(
                    "认识",
                    icon=ft.icons.CHECK,
                    on_click=lambda e: self._on_mark_result(True),
                    bgcolor=ft.colors.GREEN_600,
                    color=ft.colors.WHITE,
                    visible=False,
                ),
                ft.ElevatedButton(
                    "不认识",
                    icon=ft.icons.CLOSE,
                    on_click=lambda e: self._on_mark_result(False),
                    bgcolor=ft.colors.RED_600,
                    color=ft.colors.WHITE,
                    visible=False,
                ),
                ft.ElevatedButton(
                    "下一个",
                    icon=ft.icons.ARROW_FORWARD,
                    on_click=self._on_next,
                    bgcolor=ft.colors.BLUE_600,
                    color=ft.colors.WHITE,
                ),
                ft.ElevatedButton(
                    "结束",
                    icon=ft.icons.STOP,
                    on_click=self._on_end,
                    bgcolor=ft.colors.GREY_500,
                    color=ft.colors.WHITE,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            wrap=True,
        )
        
        self.show_answer_btn = control_buttons.controls[0]
        self.known_btn = control_buttons.controls[1]
        self.unknown_btn = control_buttons.controls[2]
        self.next_btn = control_buttons.controls[3]
        self.end_btn = control_buttons.controls[4]
        
        # 状态文本
        self.status_text = ft.Text("", size=14)
        
        # 单词卡片区域
        card_section = ft.Container(
            content=ft.Column(
                controls=[
                    self.progress_text,
                    ft.Container(height=20),
                    ft.Row([self.word_display], alignment=ft.MainAxisAlignment.CENTER),
                    self.phonetic_display,
                    ft.Container(height=10),
                    ft.Row([self.meaning_display], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(height=10),
                    ft.Row([self.answer_input], alignment=ft.MainAxisAlignment.CENTER),
                    self.result_text,
                    ft.Container(height=20),
                    control_buttons,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=20,
            visible=True,
        )
        
        self.card_section = card_section
        
        # 主布局
        return ft.Column(
            controls=[
                title,
                ft.Container(height=20),
                mode_text,
                ft.Container(height=10),
                mode_buttons,
                ft.Container(height=20),
                sort_row,
                ft.Container(height=10),
                count_row,
                ft.Container(height=20),
                ft.Divider(),
                card_section,
                ft.Container(height=10),
                self.status_text,
            ],
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )
    
    def _on_sort_change(self, e):
        """排序方式改变"""
        pass  # 保存设置，开始时使用
    
    def _on_count_change(self, e):
        """数量改变"""
        pass  # 保存设置，开始时使用
    
    def _start_review(self, mode: str):
        """开始背诵"""
        self.mode = mode
        sort_mode = self.sort_radio.value
        limit = int(self.count_dropdown.value)
        
        # 获取单词列表
        self.review_words = db.get_words_for_review(sort_mode, limit)
        
        if not self.review_words:
            self.status_text.value = "⚠️ 没有可背诵的单词，请先添加单词"
            self.status_text.color = ft.colors.ORANGE_600
            self.page.update()
            return
        
        # 重置状态
        self.current_index = 0
        self.correct_count = 0
        self.total_count = len(self.review_words)
        
        # 显示第一个单词
        self._show_current_word()
        
        # 根据模式调整UI
        if mode == "browse":
            self.answer_input.visible = False
            self.show_answer_btn.visible = True
            self.known_btn.visible = False
            self.unknown_btn.visible = False
            self.meaning_display.visible = False
        else:
            self.answer_input.visible = True
            self.answer_input.value = ""
            self.show_answer_btn.visible = True
            self.known_btn.visible = False
            self.unknown_btn.visible = False
            self.meaning_display.visible = False
        
        self.status_text.value = f"✓ 开始背诵，共 {self.total_count} 个单词"
        self.status_text.color = ft.colors.GREEN_600
        self.page.update()
    
    def _show_current_word(self):
        """显示当前单词"""
        if self.current_index >= len(self.review_words):
            self._show_result()
            return
        
        self.current_word = self.review_words[self.current_index]
        word = self.current_word.get('word', '')
        meaning = self.current_word.get('meaning', '') or '（待补充含义）'
        phonetic = self.current_word.get('phonetic', '') or ''
        
        # 根据模式显示
        if self.mode == "browse":
            self.word_display.content.value = word
            self.phonetic_display.value = phonetic
            self.meaning_display.content.value = meaning
            self.meaning_display.visible = False
        elif self.mode == "dictation_en":
            # 看中文写英文
            self.word_display.content.value = meaning
            self.phonetic_display.value = ""
            self.meaning_display.content.value = f"答案: {word}"
            self.meaning_display.visible = False
            self.answer_input.value = ""
            self.answer_input.visible = True
        elif self.mode == "dictation_cn":
            # 看英文写中文
            self.word_display.content.value = word
            self.phonetic_display.value = phonetic
            self.meaning_display.content.value = f"答案: {meaning}"
            self.meaning_display.visible = False
            self.answer_input.value = ""
            self.answer_input.visible = True
        
        self.result_text.value = ""
        self.progress_text.value = f"进度: {self.current_index + 1} / {self.total_count}"
        
        # 重置按钮状态
        self.show_answer_btn.visible = True
        self.known_btn.visible = False
        self.unknown_btn.visible = False
        
        self.page.update()
    
    def _on_show_answer(self, e):
        """显示答案"""
        self.meaning_display.visible = True
        self.show_answer_btn.visible = False
        self.known_btn.visible = True
        self.unknown_btn.visible = True
        self.page.update()
    
    def _on_submit_answer(self, e):
        """提交答案"""
        if not self.answer_input.value.strip():
            return
        
        self._check_answer()
    
    def _check_answer(self):
        """检查答案"""
        user_answer = self.answer_input.value.strip().lower()
        
        if self.mode == "dictation_en":
            correct_answer = self.current_word.get('word', '').lower()
        else:
            correct_answer = self.current_word.get('meaning', '').lower()
        
        # 简单的答案比较
        is_correct = user_answer == correct_answer or user_answer in correct_answer or correct_answer in user_answer
        
        if is_correct:
            self.result_text.value = "✓ 正确！"
            self.result_text.color = ft.colors.GREEN_600
            self.correct_count += 1
        else:
            self.result_text.value = f"✗ 错误！正确答案: {correct_answer}"
            self.result_text.color = ft.colors.RED_600
        
        self.meaning_display.visible = True
        self.show_answer_btn.visible = False
        self.known_btn.visible = False
        self.unknown_btn.visible = False
        
        self.page.update()
    
    def _on_mark_result(self, is_correct: bool):
        """标记结果（浏览模式用）"""
        if is_correct:
            self.correct_count += 1
        self._on_next(None)
    
    def _on_next(self, e):
        """下一个单词"""
        self.current_index += 1
        if self.current_index >= len(self.review_words):
            self._show_result()
        else:
            self._show_current_word()
    
    def _show_result(self):
        """显示背诵结果"""
        # 更新背诵次数
        word_ids = [w['id'] for w in self.review_words]
        db.increment_recitation_count(word_ids)
        
        # 显示结果
        accuracy = (self.correct_count / self.total_count * 100) if self.total_count > 0 else 0
        
        self.word_display.content.value = "背诵完成！"
        self.word_display.content.size = 24
        self.phonetic_display.value = ""
        self.meaning_display.content.value = f"正确率: {accuracy:.1f}% ({self.correct_count}/{self.total_count})"
        self.meaning_display.visible = True
        self.meaning_display.bgcolor = ft.colors.GREEN_100 if accuracy >= 70 else ft.colors.ORANGE_100
        
        self.answer_input.visible = False
        self.result_text.value = ""
        self.show_answer_btn.visible = False
        self.known_btn.visible = False
        self.unknown_btn.visible = False
        self.next_btn.visible = False
        
        self.status_text.value = "✓ 背诵完成！继续加油！"
        self.status_text.color = ft.colors.GREEN_600
        
        self.page.update()
    
    def _on_end(self, e):
        """结束背诵"""
        self.review_words = []
        self.current_index = 0
        self.current_word = None
        
        self.word_display.content.value = "请选择模式开始背诵"
        self.word_display.content.size = 28
        self.phonetic_display.value = ""
        self.meaning_display.visible = False
        self.answer_input.visible = False
        self.result_text.value = ""
        self.progress_text.value = ""
        
        self.show_answer_btn.visible = True
        self.known_btn.visible = False
        self.unknown_btn.visible = False
        self.next_btn.visible = True
        
        self.status_text.value = ""
        self.page.update()
