# -*- coding: utf-8 -*-
"""
单词管理页面 - 查看编辑单词、导出PDF
"""

import os
import flet as ft

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db


class ManagePage:
    """单词管理页面"""
    
    def __init__(self, page: ft.Page, on_navigate=None):
        self.page = page
        self.words = []
        self.sort_by = "alphabetical"
    
    def build(self):
        title = ft.Text("单词管理", size=24, weight=ft.FontWeight.BOLD)
        
        # 排序和搜索
        self.sort_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("alphabetical", "字典序"),
                ft.dropdown.Option("selection_desc", "高频词"),
                ft.dropdown.Option("print_asc", "未打印"),
            ],
            value="alphabetical",
            on_change=self.on_sort_change,
            width=120,
        )
        
        self.search_input = ft.TextField(
            label="搜索单词",
            on_submit=self.on_search,
            width=150,
        )
        
        refresh_btn = ft.ElevatedButton("刷新", on_click=self.on_refresh)
        
        # 导出PDF按钮（更醒目）
        export_btn = ft.ElevatedButton(
            "导出PDF打印",
            on_click=self.on_export,
            bgcolor="red",
            color="white",
            icon=ft.icons.PICTURE_AS_PDF,
        )
        
        self.stats_text = ft.Text("", color="grey", size=12)
        self.word_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        self.status_text = ft.Text("")
        
        self.load_words()
        
        return ft.Column([
            title,
            ft.Divider(),
            ft.Row([self.sort_dropdown, self.search_input, refresh_btn]),
            ft.Container(height=5),
            ft.Row([export_btn]),  # 单独一行，更醒目
            self.stats_text,
            ft.Divider(),
            self.word_list,
            self.status_text,
        ], scroll=ft.ScrollMode.AUTO, expand=True)
    
    def load_words(self, keyword=""):
        if keyword:
            self.words = db.search_words(keyword)
        else:
            self.words = db.get_all_words(self.sort_by)
        
        self.display_words()
        
        stats = db.get_statistics()
        self.stats_text.value = f"共 {stats['total_words']} 个单词 | 选择{stats['total_selections']}次 | 打印{stats['total_prints']}次"
    
    def display_words(self):
        self.word_list.controls.clear()
        
        if not self.words:
            self.word_list.controls.append(ft.Text("暂无单词，请先到「采集」页面添加", color="grey"))
            self.page.update()
            return
        
        for w in self.words:
            card = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(w['word'], size=16, weight=ft.FontWeight.BOLD, color="blue"),
                        ft.Text(w.get('phonetic') or '', color="grey", size=12, italic=True),
                        ft.Container(
                            content=ft.Text(w.get('part_of_speech') or '', size=10, color="white"),
                            bgcolor="green",
                            border_radius=4,
                            padding=ft.padding.only(left=4, right=4, top=2, bottom=2),
                            visible=bool(w.get('part_of_speech')),
                        ),
                    ]),
                    ft.Text(w.get('meaning') or '（待补充含义）', size=12),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("例句:", size=10, color="grey"),
                            ft.Text(w.get('example_sentence') or '', size=11, italic=True),
                        ], visible=bool(w.get('example_sentence'))),
                        visible=bool(w.get('example_sentence')),
                    ),
                    ft.Row([
                        ft.Text(f"选中:{w.get('selection_count', 0)}", size=10, color="blue"),
                        ft.Text(f"打印:{w.get('print_count', 0)}", size=10, color="green"),
                        ft.Text(f"背诵:{w.get('recitation_count', 0)}", size=10, color="purple"),
                    ]),
                    ft.Row([
                        ft.TextButton("编辑", on_click=lambda e, word=w: self.edit_word(word)),
                        ft.TextButton("查词典", on_click=lambda e, word=w: self.lookup_word(word)),
                        ft.TextButton("删除", on_click=lambda e, wid=w['id']: self.delete_word(wid)),
                    ]),
                ]),
                padding=10,
                border=ft.border.all(1, "grey"),
                border_radius=8,
                margin=ft.margin.only(bottom=5),
            )
            self.word_list.controls.append(card)
        
        self.page.update()
    
    def on_sort_change(self, e):
        self.sort_by = e.control.value
        self.load_words()
    
    def on_search(self, e):
        keyword = self.search_input.value.strip()
        self.load_words(keyword if keyword else "")
    
    def on_refresh(self, e):
        self.search_input.value = ""
        self.load_words()
        self.status_text.value = "已刷新"
        self.status_text.color = "green"
        self.page.update()
    
    def edit_word(self, word_info):
        """编辑单词"""
        word_id = word_info['id']
        
        word_input = ft.TextField(label="单词", value=word_info.get('word', ''), width=200)
        meaning_input = ft.TextField(label="中文含义", value=word_info.get('meaning') or '', multiline=True, min_lines=2, max_lines=4)
        phonetic_input = ft.TextField(label="音标", value=word_info.get('phonetic') or '', width=150)
        pos_input = ft.TextField(label="词性", value=word_info.get('part_of_speech') or '', width=100)
        example_input = ft.TextField(label="例句", value=word_info.get('example_sentence') or '', multiline=True, min_lines=2, max_lines=3)
        
        def on_save(e):
            db.update_word(
                word_id,
                word=word_input.value,
                meaning=meaning_input.value,
                phonetic=phonetic_input.value,
                part_of_speech=pos_input.value,
                example_sentence=example_input.value,
            )
            dialog.open = False
            self.load_words(self.search_input.value.strip())
            self.status_text.value = "已保存"
            self.status_text.color = "green"
            self.page.update()
        
        def on_cancel(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("编辑单词"),
            content=ft.Column([
                word_input,
                ft.Row([phonetic_input, pos_input]),
                meaning_input,
                example_input,
            ], scroll=ft.ScrollMode.AUTO, width=350, height=350),
            actions=[
                ft.TextButton("取消", on_click=on_cancel),
                ft.ElevatedButton("保存", on_click=on_save, bgcolor="blue", color="white"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def lookup_word(self, word_info):
        """查词典"""
        word = word_info.get('word', '')
        
        self.status_text.value = f"正在查询 {word}..."
        self.status_text.color = "blue"
        self.page.update()
        
        try:
            from utils.dictionary import dictionary_api
            result = dictionary_api.lookup_word(word)
            
            if result and result.get('meaning'):
                db.update_word(
                    word_info['id'],
                    meaning=result.get('meaning', ''),
                    phonetic=result.get('phonetic', ''),
                    part_of_speech=result.get('part_of_speech', ''),
                    example_sentence=result.get('example', ''),
                )
                self.load_words(self.search_input.value.strip())
                self.status_text.value = f"已更新 {word} 的信息"
                self.status_text.color = "green"
            else:
                self.status_text.value = f"未找到 {word} 的释义，请手动编辑"
                self.status_text.color = "orange"
                
        except Exception as ex:
            self.status_text.value = f"查询失败: {ex}"
            self.status_text.color = "red"
        
        self.page.update()
    
    def delete_word(self, word_id):
        """删除单词"""
        def on_confirm(e):
            db.delete_word(word_id)
            dialog.open = False
            self.load_words(self.search_input.value.strip())
            self.status_text.value = "已删除"
            self.status_text.color = "green"
            self.page.update()
        
        def on_cancel(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("确认删除"),
            content=ft.Text("确定要删除这个单词吗？"),
            actions=[
                ft.TextButton("取消", on_click=on_cancel),
                ft.ElevatedButton("删除", on_click=on_confirm, bgcolor="red", color="white"),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def on_export(self, e):
        """导出PDF"""
        if not self.words:
            self.status_text.value = "没有单词可导出"
            self.status_text.color = "red"
            self.page.update()
            return
        
        self.status_text.value = "正在生成PDF..."
        self.status_text.color = "blue"
        self.page.update()
        
        try:
            from pdf_generator import pdf_generator
            
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "vocabulary.pdf")
            
            success, msg = pdf_generator.generate_vocabulary_pdf(self.words, output_path)
            
            if success:
                word_ids = [w['id'] for w in self.words]
                db.increment_print_count(word_ids)
                self.status_text.value = f"PDF已保存: {output_path}"
                self.status_text.color = "green"
                self.load_words(self.search_input.value.strip())
            else:
                self.status_text.value = msg
                self.status_text.color = "red"
        except Exception as ex:
            self.status_text.value = f"导出失败: {ex}"
            self.status_text.color = "red"
        
        self.page.update()
