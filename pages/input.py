# -*- coding: utf-8 -*-
"""
单词采集页面 - 支持文本导入、截图粘贴和图片OCR识别
"""

import os
import re
import flet as ft
from typing import List, Dict, Callable

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db


def extract_english_words_from_text(text: str) -> List[str]:
    """
    从文本中提取英文单词（不依赖OCR库）
    
    参数:
        text: 输入文本
    
    返回:
        List[str]: 英文单词列表（去重、排序）
    """
    pattern = r"[a-zA-Z]+(?:[-'][a-zA-Z]+)*"
    words = re.findall(pattern, text)
    unique_words = sorted(set(word.lower() for word in words if len(word) > 1))
    return unique_words


class InputPage:
    """单词采集页面"""
    
    def __init__(self, page: ft.Page, on_navigate: Callable = None):
        self.page = page
        self.on_navigate = on_navigate
        
        self.recognized_text = ""
        self.extracted_words: List[str] = []
        self.selected_words: set = set()
        
        self.text_input = None
        self.word_container = None
        self.status_text = None
        self.selected_count_text = None
        self.ocr_status_text = None
        
        self._init_ocr()
    
    def _init_ocr(self):
        """延迟初始化OCR"""
        self.ocr_handler = None
        self.ocr_available = False
        self.ocr_error = ""
        
        try:
            from ocr_handler import ocr_handler
            self.ocr_handler = ocr_handler
            self.ocr_available, self.ocr_error = ocr_handler.is_available()
        except Exception as e:
            self.ocr_error = str(e)
    
    def build(self) -> ft.Control:
        title = ft.Text(
            "单词采集",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700
        )
        
        description = ft.Text(
            "粘贴文本、粘贴截图或上传图片来采集陌生单词",
            size=14,
            color=ft.Colors.GREY_600
        )
        
        self.text_input = ft.TextField(
            label="粘贴或输入文本（支持Ctrl+V粘贴截图）",
            multiline=True,
            min_lines=5,
            max_lines=10,
            hint_text="在此粘贴阅读理解文章，或直接Ctrl+V粘贴截图...",
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_700,
            on_change=self._on_text_change,
        )
        
        self.status_text = ft.Text("", size=14, color=ft.Colors.GREEN_700)
        
        buttons_row = ft.Row(
            controls=[
                ft.ElevatedButton(
                    "提取单词",
                    icon=ft.Icons.TEXT_FIELDS,
                    on_click=self._on_extract_from_text,
                    bgcolor=ft.Colors.BLUE_600,
                    color=ft.Colors.WHITE,
                ),
                ft.ElevatedButton(
                    "粘贴截图",
                    icon=ft.Icons.CONTENT_PASTE,
                    on_click=self._on_paste_clipboard,
                    bgcolor=ft.Colors.TEAL_600,
                    color=ft.Colors.WHITE,
                ),
                ft.ElevatedButton(
                    "上传图片",
                    icon=ft.Icons.IMAGE,
                    on_click=self._on_upload_image,
                    bgcolor=ft.Colors.GREEN_600,
                    color=ft.Colors.WHITE,
                ),
                ft.ElevatedButton(
                    "清除",
                    icon=ft.Icons.CLEAR,
                    on_click=self._on_clear,
                    bgcolor=ft.Colors.GREY_400,
                    color=ft.Colors.WHITE,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            wrap=True,
        )
        
        self.ocr_status_text = ft.Text(
            "",
            size=12,
        )
        if self.ocr_available:
            self.ocr_status_text.value = "[OK] 图片OCR功能已就绪"
            self.ocr_status_text.color = ft.Colors.GREEN_600
        else:
            self.ocr_status_text.value = "[提示] 图片OCR不可用，文本提取功能正常。如需图片识别请安装: pip install easyocr"
            self.ocr_status_text.color = ft.Colors.GREY_600
        
        self.word_container = ft.Column(
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            height=250,
        )
        
        word_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("提取的单词（点击选择）", size=16, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    self.word_container,
                ]
            ),
            bgcolor=ft.Colors.GREY_50,
            padding=10,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
        
        self.selected_count_text = ft.Text(
            "已选中: 0 个单词",
            size=14,
            color=ft.Colors.BLUE_700,
            weight=ft.FontWeight.BOLD,
        )
        
        submit_button = ft.ElevatedButton(
            "提交选中单词",
            icon=ft.Icons.SAVE,
            on_click=self._on_submit,
            bgcolor=ft.Colors.PURPLE_600,
            color=ft.Colors.WHITE,
            width=180,
            height=45,
        )
        
        select_buttons = ft.Row(
            controls=[
                ft.TextButton(
                    "全选",
                    icon=ft.Icons.SELECT_ALL,
                    on_click=self._on_select_all,
                ),
                ft.TextButton(
                    "取消全选",
                    icon=ft.Icons.DESELECT,
                    on_click=self._on_deselect_all,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
        return ft.Column(
            controls=[
                title,
                ft.Container(height=10),
                description,
                ft.Container(height=15),
                self.text_input,
                ft.Container(height=10),
                buttons_row,
                ft.Container(height=5),
                self.ocr_status_text,
                ft.Container(height=15),
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
    
    def _on_text_change(self, e):
        """文本变化时的事件"""
        pass
    
    def _on_extract_from_text(self, e):
        """从文本中提取单词"""
        try:
            text = self.text_input.value
            if not text or not text.strip():
                self.status_text.value = "[!] 请先输入或粘贴文本"
                self.status_text.color = ft.Colors.RED_500
                self.page.update()
                return
            
            self.extracted_words = extract_english_words_from_text(text)
            
            if not self.extracted_words:
                self.status_text.value = "[!] 未在文本中找到英文单词"
                self.status_text.color = ft.Colors.ORANGE_600
                self.page.update()
                return
            
            self.selected_words.clear()
            self._display_words()
            
            self.status_text.value = f"[OK] 已提取 {len(self.extracted_words)} 个单词"
            self.status_text.color = ft.Colors.GREEN_600
            self.page.update()
            
        except Exception as ex:
            self.status_text.value = f"[错误] {str(ex)}"
            self.status_text.color = ft.Colors.RED_500
            self.page.update()
    
    def _on_paste_clipboard(self, e):
        """粘贴剪贴板内容"""
        self.status_text.value = "[...] 正在读取剪贴板..."
        self.status_text.color = ft.Colors.BLUE_600
        self.page.update()
        
        try:
            import pyperclip
            clipboard_text = pyperclip.paste()
            
            if clipboard_text and clipboard_text.strip():
                self.text_input.value = clipboard_text
                self.status_text.value = "[OK] 已粘贴文本，请点击\"提取单词\""
                self.status_text.color = ft.Colors.GREEN_600
            else:
                self.status_text.value = "[!] 剪贴板中没有文本内容"
                self.status_text.color = ft.Colors.ORANGE_600
            
        except ImportError:
            self.status_text.value = "[提示] 请直接在文本框中按 Ctrl+V 粘贴"
            self.status_text.color = ft.Colors.BLUE_600
        except Exception as ex:
            self.status_text.value = f"[错误] {str(ex)}"
            self.status_text.color = ft.Colors.RED_500
        
        self.page.update()
    
    def _on_upload_image(self, e):
        """上传图片并识别"""
        if not self.ocr_available or not self.ocr_handler:
            self.status_text.value = "[!] 图片OCR功能不可用，请安装 easyocr"
            self.status_text.color = ft.Colors.RED_500
            self.page.update()
            return
        
        file_picker = ft.FilePicker(on_result=self._on_file_picker_result)
        self.page.overlay.append(file_picker)
        self.page.update()
        
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
        
        self.status_text.value = "[...] 正在识别图片，请稍候..."
        self.status_text.color = ft.Colors.BLUE_600
        self.page.update()
        
        success, result = self.ocr_handler.recognize_image(file_path)
        
        if not success:
            self.status_text.value = f"[错误] {result}"
            self.status_text.color = ft.Colors.RED_500
            self.page.update()
            return
        
        self.text_input.value = result
        self.recognized_text = result
        
        self.extracted_words = extract_english_words_from_text(result)
        
        if not self.extracted_words:
            self.status_text.value = "[!] 图片中未识别到英文单词"
            self.status_text.color = ft.Colors.ORANGE_600
            self.page.update()
            return
        
        self.selected_words.clear()
        self._display_words()
        
        self.status_text.value = f"[OK] 识别成功，提取了 {len(self.extracted_words)} 个单词"
        self.status_text.color = ft.Colors.GREEN_600
        self.page.update()
    
    def _display_words(self):
        """显示单词列表"""
        self.word_container.controls.clear()
        
        word_chips = []
        
        for word in self.extracted_words:
            chip = ft.Chip(
                label=ft.Text(word, size=12),
                bgcolor=ft.Colors.BLUE_50,
                selected_color=ft.Colors.BLUE_300,
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
    
    def _on_word_click(self, e, word: str):
        """单词点击事件"""
        chip = e.control
        
        if word in self.selected_words:
            self.selected_words.discard(word)
            chip.selected = False
            chip.bgcolor = ft.Colors.BLUE_50
        else:
            self.selected_words.add(word)
            chip.selected = True
            chip.bgcolor = ft.Colors.BLUE_300
        
        self._update_selected_count()
        self.page.update()
    
    def _on_select_all(self, e):
        """全选"""
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
                bgcolor=ft.Colors.BLUE_300 if is_selected else ft.Colors.BLUE_50,
                selected_color=ft.Colors.BLUE_300,
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
        """更新选中计数"""
        count = len(self.selected_words)
        self.selected_count_text.value = f"已选中: {count} 个单词"
    
    def _on_submit(self, e):
        """提交选中的单词"""
        if not self.selected_words:
            self.status_text.value = "[!] 请先选择要添加的单词"
            self.status_text.color = ft.Colors.ORANGE_600
            self.page.update()
            return
        
        words_list = list(self.selected_words)
        new_count, update_count = db.batch_add_words(words_list)
        
        self.status_text.value = f"[OK] 成功添加 {new_count} 个新单词，更新 {update_count} 个已有单词"
        self.status_text.color = ft.Colors.GREEN_600
        
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
