# -*- coding: utf-8 -*-
"""
单词采集页面 - 选词模式
电脑端：选中文本后输入/粘贴到单词框
图片端：OCR识别后点击单词选择
"""

import os
import re
import flet as ft

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db


class InputPage:
    """单词采集页面"""
    
    def __init__(self, page: ft.Page, on_navigate=None):
        self.page = page
        self.selected_words = []
        self.ocr_text = ""
        self.ocr_words = []
        self.ocr_selected = set()
    
    def build(self):
        title = ft.Text("单词采集", size=24, weight=ft.FontWeight.BOLD)
        desc = ft.Text("方式1: 选中文本中的单词 → 粘贴到输入框 → 添加 | 方式2: 上传图片 → 点击选择单词", 
                       size=12, color="grey")
        
        # === 文本模式 ===
        text_title = ft.Text("文本选词", size=16, weight=ft.FontWeight.BOLD, color="blue")
        
        self.text_input = ft.TextField(
            label="粘贴阅读文章（供参考）",
            multiline=True,
            min_lines=4,
            max_lines=8,
            hint_text="在此粘贴阅读文章，然后选中想要的单词，复制到下方输入框...",
        )
        
        # 单词输入框
        self.word_input = ft.TextField(
            label="输入或粘贴要收集的单词",
            hint_text="选中文本中的单词，复制粘贴到这里...",
            width=250,
        )
        
        add_word_btn = ft.ElevatedButton(
            "添加单词",
            on_click=self.on_add_word,
            bgcolor="blue",
            color="white",
        )
        
        # === 图片模式 ===
        img_title = ft.Text("图片选词 (OCR)", size=16, weight=ft.FontWeight.BOLD, color="orange")
        
        upload_btn = ft.ElevatedButton(
            "上传图片识别",
            on_click=self.on_upload_image,
            bgcolor="orange",
            color="white",
        )
        
        self.ocr_status = ft.Text("", size=12)
        
        # OCR识别结果 - 显示原文和可选单词
        self.ocr_text_display = ft.Container(
            content=ft.Column([
                ft.Text("识别到的文本:", size=12, weight=ft.FontWeight.BOLD),
                ft.Text("", size=11),  # 原文显示
            ]),
            padding=10,
            bgcolor="#f0f0f0",
            border_radius=8,
            visible=False,
        )
        self.ocr_original_text = self.ocr_text_display.content.controls[1]
        
        # OCR单词选择区
        self.ocr_words_area = ft.Container(
            content=ft.Column([
                ft.Text("点击选择单词:", size=12),
                ft.Wrap([], spacing=5, run_spacing=5),  # 单词chips
            ]),
            padding=10,
            visible=False,
        )
        self.ocr_chips = self.ocr_words_area.content.controls[1]
        
        # === 待提交单词列表 ===
        list_title = ft.Text("待提交单词列表", size=16, weight=ft.FontWeight.BOLD, color="purple")
        
        self.word_list_display = ft.Column(scroll=ft.ScrollMode.AUTO, height=120)
        
        # 例句输入
        example_label = ft.Text("例句（可选，保存单词所在的原文句子）:", size=12)
        self.example_input = ft.TextField(
            hint_text="粘贴包含单词的原句，帮助记忆...",
            multiline=True,
            min_lines=2,
            max_lines=3,
        )
        
        # 按钮
        clear_btn = ft.OutlinedButton("清空", on_click=self.on_clear)
        submit_btn = ft.ElevatedButton("提交单词", on_click=self.on_submit, bgcolor="purple", color="white")
        
        # 状态
        self.status_text = ft.Text("", size=14)
        self.count_text = ft.Text("已选: 0 个", color="purple")
        
        return ft.Column([
            title,
            desc,
            ft.Divider(),
            
            # 文本模式
            text_title,
            self.text_input,
            ft.Row([self.word_input, add_word_btn]),
            ft.Text("提示: 在上方文本中选中单词 → 复制 → 粘贴到输入框 → 点击添加", size=10, color="grey"),
            
            ft.Divider(),
            
            # 图片模式
            ft.Row([img_title, upload_btn]),
            self.ocr_status,
            self.ocr_text_display,
            self.ocr_words_area,
            
            ft.Divider(),
            
            # 待提交列表
            ft.Row([list_title, self.count_text]),
            self.word_list_display,
            example_label,
            self.example_input,
            ft.Row([clear_btn, submit_btn]),
            self.status_text,
        ], scroll=ft.ScrollMode.AUTO, expand=True)
    
    def on_add_word(self, e):
        """添加单词到列表"""
        text = self.word_input.value.strip()
        if not text:
            self.status_text.value = "请输入单词"
            self.status_text.color = "red"
            self.page.update()
            return
        
        # 提取英文单词
        words = re.findall(r"[a-zA-Z]+(?:[-'][a-zA-Z]+)*", text)
        if not words:
            self.status_text.value = "未识别到英文单词"
            self.status_text.color = "orange"
            self.page.update()
            return
        
        added = 0
        for w in words:
            w = w.lower()
            if w not in self.selected_words and len(w) > 1:
                self.selected_words.append(w)
                added += 1
        
        self.word_input.value = ""
        
        if added > 0:
            self.update_word_list()
            self.status_text.value = f"已添加 {added} 个单词"
            self.status_text.color = "green"
        else:
            self.status_text.value = "单词已在列表中"
            self.status_text.color = "orange"
        
        self.page.update()
    
    def on_upload_image(self, e):
        """上传图片"""
        file_picker = ft.FilePicker(on_result=self.on_file_result)
        self.page.overlay.append(file_picker)
        self.page.update()
        file_picker.pick_files(
            allowed_extensions=["png", "jpg", "jpeg", "bmp"],
            allow_multiple=False
        )
    
    def on_file_result(self, e):
        """处理图片"""
        if not e.files:
            return
        
        self.ocr_status.value = "正在识别图片..."
        self.ocr_status.color = "blue"
        self.page.update()
        
        try:
            from ocr_handler import ocr_handler
            available, error = ocr_handler.is_available()
            
            if not available:
                self.ocr_status.value = f"OCR不可用: {error}"
                self.ocr_status.color = "red"
                self.page.update()
                return
            
            success, result = ocr_handler.recognize_image(e.files[0].path)
            
            if success:
                self.ocr_text = result
                
                # 显示原文
                self.ocr_original_text.value = result[:500] + ("..." if len(result) > 500 else "")
                self.ocr_text_display.visible = True
                
                # 提取单词并显示
                self.ocr_words = self.extract_words(result)
                self.ocr_selected.clear()
                self.display_ocr_words()
                
                self.ocr_words_area.visible = True
                self.ocr_status.value = f"识别成功，共 {len(self.ocr_words)} 个单词，点击选择"
                self.ocr_status.color = "green"
            else:
                self.ocr_status.value = f"识别失败: {result}"
                self.ocr_status.color = "red"
                
        except Exception as ex:
            self.ocr_status.value = f"错误: {ex}"
            self.ocr_status.color = "red"
        
        self.page.update()
    
    def extract_words(self, text):
        """提取单词，保持原文顺序"""
        pattern = r"[a-zA-Z]+(?:[-'][a-zA-Z]+)*"
        words = re.findall(pattern, text)
        seen = set()
        result = []
        for w in words:
            w = w.lower()
            if w not in seen and len(w) > 1:
                seen.add(w)
                result.append(w)
        return result
    
    def display_ocr_words(self):
        """显示OCR单词chips"""
        self.ocr_chips.controls.clear()
        
        for word in self.ocr_words:
            is_selected = word in self.ocr_selected
            chip = ft.Chip(
                label=ft.Text(word),
                bgcolor="purple" if is_selected else "grey",
                selected=is_selected,
                on_click=lambda e, w=word: self.on_ocr_word_click(w),
            )
            self.ocr_chips.controls.append(chip)
        
        self.page.update()
    
    def on_ocr_word_click(self, word):
        """点击OCR单词"""
        if word in self.ocr_selected:
            # 取消选择
            self.ocr_selected.remove(word)
            if word in self.selected_words:
                self.selected_words.remove(word)
        else:
            # 选择
            self.ocr_selected.add(word)
            if word not in self.selected_words:
                self.selected_words.append(word)
        
        self.display_ocr_words()
        self.update_word_list()
    
    def update_word_list(self):
        """更新单词列表显示"""
        self.word_list_display.controls.clear()
        
        for word in self.selected_words:
            row = ft.Row([
                ft.Text(word, size=14, expand=True),
                ft.IconButton(
                    icon=ft.icons.CLOSE,
                    on_click=lambda e, w=word: self.remove_word(w),
                    icon_size=16,
                ),
            ])
            self.word_list_display.controls.append(row)
        
        self.count_text.value = f"已选: {len(self.selected_words)} 个"
        self.page.update()
    
    def remove_word(self, word):
        """移除单词"""
        if word in self.selected_words:
            self.selected_words.remove(word)
        if word in self.ocr_selected:
            self.ocr_selected.remove(word)
        
        self.update_word_list()
        self.display_ocr_words()
    
    def on_clear(self, e):
        """清空"""
        self.selected_words.clear()
        self.ocr_selected.clear()
        self.word_input.value = ""
        self.example_input.value = ""
        self.update_word_list()
        self.display_ocr_words()
        self.status_text.value = "已清空"
        self.status_text.color = "grey"
        self.page.update()
    
    def on_submit(self, e):
        """提交单词"""
        if not self.selected_words:
            self.status_text.value = "请先添加单词"
            self.status_text.color = "red"
            self.page.update()
            return
        
        example = self.example_input.value.strip()
        
        # 批量添加
        new_count, update_count = db.batch_add_words(self.selected_words)
        
        # 如果有例句，更新每个单词
        if example:
            for word in self.selected_words:
                word_info = db.get_word_by_text(word)
                if word_info:
                    db.update_word(word_info['id'], example_sentence=example)
        
        self.status_text.value = f"成功! 新增 {new_count} 个，更新 {update_count} 个单词"
        self.status_text.color = "green"
        
        # 清空
        self.selected_words.clear()
        self.ocr_selected.clear()
        self.example_input.value = ""
        self.update_word_list()
        self.display_ocr_words()
        
        self.page.update()
