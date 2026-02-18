# -*- coding: utf-8 -*-
"""
单词采集页面 - 支持文本导入和图片OCR识别
"""

import os
import flet as ft
from typing import List, Dict, Callable

# 导入其他模块
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from ocr_handler import ocr_handler


class InputPage:
    """单词采集页面"""
    
    def __init__(self, page: ft.Page, on_navigate: Callable = None):
        """
        初始化单词采集页面
        
        参数:
            page: Flet页面对象
            on_navigate: 导航回调函数
        """
        self.page = page
        self.on_navigate = on_navigate
        
        # 状态变量
        self.recognized_text = ""  # OCR识别的文本
        self.extracted_words: List[str] = []  # 提取的单词列表
        self.selected_words: set = set()  # 用户选中的单词
        
        # UI组件
        self.text_input = None
        self.word_container = None
        self.status_text = None
        self.selected_count_text = None
    
    def build(self) -> ft.Control:
        """构建页面UI"""
        
        # 标题
        title = ft.Text(
            "单词采集",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.BLUE_700
        )
        
        # 说明文字
        description = ft.Text(
            "通过粘贴文本或上传图片来采集陌生单词",
            size=14,
            color=ft.colors.GREY_600
        )
        
        # 文本输入区域
        self.text_input = ft.TextField(
            label="粘贴或输入文本",
            multiline=True,
            min_lines=5,
            max_lines=10,
            hint_text="在此粘贴阅读理解文章或其他文本...",
            border_color=ft.colors.BLUE_400,
            focused_border_color=ft.colors.BLUE_700,
        )
        
        # 按钮行
        buttons_row = ft.Row(
            controls=[
                ft.ElevatedButton(
                    "提取单词",
                    icon=ft.icons.TEXT_FIELDS,
                    on_click=self._on_extract_from_text,
                    bgcolor=ft.colors.BLUE_600,
                    color=ft.colors.WHITE,
                ),
                ft.ElevatedButton(
                    "上传图片",
                    icon=ft.icons.IMAGE,
                    on_click=self._on_upload_image,
                    bgcolor=ft.colors.GREEN_600,
                    color=ft.colors.WHITE,
                ),
                ft.ElevatedButton(
                    "清除",
                    icon=ft.icons.CLEAR,
                    on_click=self._on_clear,
                    bgcolor=ft.colors.GREY_400,
                    color=ft.colors.WHITE,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )
        
        # OCR状态文本
        ocr_status = ft.Text(
            "",
            size=12,
            color=ft.colors.ORANGE_700,
        )
        self.ocr_status_text = ocr_status
        
        # 检查OCR状态
        available, error = ocr_handler.is_available()
        if not available:
            ocr_status.value = f"⚠️ OCR不可用: {error}"
            ocr_status.color = ft.colors.RED_500
        else:
            ocr_status.value = "✓ OCR已就绪"
            ocr_status.color = ft.colors.GREEN_600
        
        # 单词显示区域
        self.word_container = ft.Column(
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            height=300,
        )
        
        # 单词显示容器
        word_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("提取的单词（点击选择）", size=16, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    self.word_container,
                ]
            ),
            bgcolor=ft.colors.GREY_50,
            padding=10,
            border_radius=10,
            border=ft.border.all(1, ft.colors.GREY_300),
        )
        
        # 选中计数和提交按钮
        self.selected_count_text = ft.Text(
            "已选中: 0 个单词",
            size=14,
            color=ft.colors.BLUE_700,
            weight=ft.FontWeight.BOLD,
        )
        
        submit_button = ft.ElevatedButton(
            "提交选中单词",
            icon=ft.icons.SAVE,
            on_click=self._on_submit,
            bgcolor=ft.colors.PURPLE_600,
            color=ft.colors.WHITE,
            width=200,
            height=45,
        )
        
        # 状态文本
        self.status_text = ft.Text("", size=14, color=ft.colors.GREEN_700)
        
        # 全选/取消全选按钮
        select_buttons = ft.Row(
            controls=[
                ft.TextButton(
                    "全选",
                    icon=ft.icons.SELECT_ALL,
                    on_click=self._on_select_all,
                ),
                ft.TextButton(
                    "取消全选",
                    icon=ft.icons.DESELECT,
                    on_click=self._on_deselect_all,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
        # 主布局
        return ft.Column(
            controls=[
                title,
                ft.Container(height=10),
                description,
                ft.Container(height=20),
                self.text_input,
                ft.Container(height=10),
                buttons_row,
                ft.Container(height=5),
                ocr_status,
                ft.Container(height=20),
                word_section,
                ft.Container(height=10),
                select_buttons,
                ft.Container(height=10),
                ft.Row(
                    controls=[self.selected_count_text, submit_button],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=10),
                self.status_text,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
    
    def _on_extract_from_text(self, e):
        """从文本中提取单词"""
        text = self.text_input.value
        if not text or not text.strip():
            self.status_text.value = "⚠️ 请先输入或粘贴文本"
            self.status_text.color = ft.colors.RED_500
            self.page.update()
            return
        
        # 提取英文单词
        self.extracted_words = ocr_handler.extract_english_words(text)
        
        if not self.extracted_words:
            self.status_text.value = "⚠️ 未在文本中找到英文单词"
            self.status_text.color = ft.colors.ORANGE_600
            self.page.update()
            return
        
        # 清空选中状态
        self.selected_words.clear()
        
        # 显示单词列表
        self._display_words()
        
        self.status_text.value = f"✓ 已提取 {len(self.extracted_words)} 个单词"
        self.status_text.color = ft.colors.GREEN_600
        self.page.update()
    
    def _on_upload_image(self, e):
        """上传图片并识别"""
        # 创建文件选择器
        file_picker = ft.FilePicker(on_result=self._on_file_picker_result)
        self.page.overlay.append(file_picker)
        self.page.update()
        
        # 打开文件选择对话框
        file_picker.pick_files(
            allowed_extensions=["png", "jpg", "jpeg", "bmp", "gif"],
            allow_multiple=False
        )
    
    def _on_file_picker_result(self, e: ft.FilePickerResultEvent):
        """处理文件选择结果"""
        if not e.files:
            return
        
        file = e.files[0]
        file_path = file.path
        
        self.status_text.value = "⏳ 正在识别图片，请稍候..."
        self.status_text.color = ft.colors.BLUE_600
        self.page.update()
        
        # 识别图片
        success, result = ocr_handler.recognize_image(file_path)
        
        if not success:
            self.status_text.value = f"❌ 识别失败: {result}"
            self.status_text.color = ft.colors.RED_500
            self.page.update()
            return
        
        # 显示识别的文本
        self.text_input.value = result
        self.recognized_text = result
        
        # 提取单词
        self.extracted_words = ocr_handler.extract_english_words(result)
        
        if not self.extracted_words:
            self.status_text.value = "⚠️ 图片中未识别到英文单词"
            self.status_text.color = ft.colors.ORANGE_600
            self.page.update()
            return
        
        # 清空选中状态
        self.selected_words.clear()
        
        # 显示单词列表
        self._display_words()
        
        self.status_text.value = f"✓ 识别成功，提取了 {len(self.extracted_words)} 个单词"
        self.status_text.color = ft.colors.GREEN_600
        self.page.update()
    
    def _display_words(self):
        """显示单词列表，每个单词可点击选择"""
        self.word_container.controls.clear()
        
        # 使用Wrap布局，让单词自动换行
        word_chips = []
        
        for word in self.extracted_words:
            # 创建可点击的单词chip
            chip = ft.Chip(
                label=ft.Text(word, size=12),
                bgcolor=ft.colors.BLUE_50,
                selected_color=ft.colors.BLUE_300,
                on_click=lambda e, w=word: self._on_word_click(e, w),
                show_checkmark=True,
            )
            word_chips.append(chip)
        
        # 使用Wrap让单词自动换行排列
        wrap = ft.Wrap(
            controls=word_chips,
            spacing=8,
            run_spacing=8,
        )
        
        self.word_container.controls.append(wrap)
        self._update_selected_count()
        self.page.update()
    
    def _on_word_click(self, e, word: str):
        """单词点击事件处理"""
        chip = e.control
        
        if word in self.selected_words:
            # 取消选中
            self.selected_words.discard(word)
            chip.selected = False
            chip.bgcolor = ft.colors.BLUE_50
        else:
            # 选中
            self.selected_words.add(word)
            chip.selected = True
            chip.bgcolor = ft.colors.BLUE_300
        
        self._update_selected_count()
        self.page.update()
    
    def _on_select_all(self, e):
        """全选所有单词"""
        self.selected_words = set(self.extracted_words)
        self._refresh_word_display()
    
    def _on_deselect_all(self, e):
        """取消全选"""
        self.selected_words.clear()
        self._refresh_word_display()
    
    def _refresh_word_display(self):
        """刷新单词显示"""
        self.word_container.controls.clear()
        
        word_chips = []
        for word in self.extracted_words:
            is_selected = word in self.selected_words
            chip = ft.Chip(
                label=ft.Text(word, size=12),
                bgcolor=ft.colors.BLUE_300 if is_selected else ft.colors.BLUE_50,
                selected_color=ft.colors.BLUE_300,
                selected=is_selected,
                on_click=lambda e, w=word: self._on_word_click(e, w),
                show_checkmark=True,
            )
            word_chips.append(chip)
        
        wrap = ft.Wrap(
            controls=word_chips,
            spacing=8,
            run_spacing=8,
        )
        
        self.word_container.controls.append(wrap)
        self._update_selected_count()
        self.page.update()
    
    def _update_selected_count(self):
        """更新选中计数显示"""
        count = len(self.selected_words)
        self.selected_count_text.value = f"已选中: {count} 个单词"
    
    def _on_submit(self, e):
        """提交选中的单词"""
        if not self.selected_words:
            self.status_text.value = "⚠️ 请先选择要添加的单词"
            self.status_text.color = ft.colors.ORANGE_600
            self.page.update()
            return
        
        # 批量添加到数据库
        words_list = list(self.selected_words)
        new_count, update_count = db.batch_add_words(words_list)
        
        self.status_text.value = f"✓ 成功添加 {new_count} 个新单词，更新 {update_count} 个已有单词"
        self.status_text.color = ft.colors.GREEN_600
        
        # 清空选中状态
        self.selected_words.clear()
        self._refresh_word_display()
        
        self.page.update()
    
    def _on_clear(self, e):
        """清除所有内容"""
        self.text_input.value = ""
        self.recognized_text = ""
        self.extracted_words = []
        self.selected_words.clear()
        self.word_container.controls.clear()
        self.status_text.value = ""
        self._update_selected_count()
        self.page.update()
