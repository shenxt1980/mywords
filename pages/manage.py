# -*- coding: utf-8 -*-
"""
单词管理页面 - 简化版
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
        title = ft.Text("单词管理", size=24, weight=ft.FontWeight.W_BOLD)
        
        self.sort_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("alphabetical", "字典序"),
                ft.dropdown.Option("selection_desc", "高频词优先"),
                ft.dropdown.Option("print_asc", "未打印优先"),
            ],
            value="alphabetical",
            on_change=self.on_sort_change,
            width=150,
        )
        
        refresh_btn = ft.ElevatedButton("刷新", on_click=self.on_refresh)
        export_btn = ft.ElevatedButton("导出PDF", on_click=self.on_export, bgcolor="red", color="white")
        
        self.stats_text = ft.Text("", color="grey")
        self.word_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        self.status_text = ft.Text("")
        
        self.load_words()
        
        return ft.Column([
            title,
            ft.Divider(),
            ft.Row([self.sort_dropdown, refresh_btn, export_btn]),
            self.stats_text,
            ft.Divider(),
            self.word_list,
            self.status_text,
        ], scroll=ft.ScrollMode.AUTO, expand=True)
    
    def load_words(self):
        self.words = db.get_all_words(self.sort_by)
        self.display_words()
        stats = db.get_statistics()
        self.stats_text.value = f"共 {stats['total_words']} 个单词"
    
    def display_words(self):
        self.word_list.controls.clear()
        
        if not self.words:
            self.word_list.controls.append(ft.Text("暂无单词，请先添加", color="grey"))
            return
        
        for w in self.words:
            card = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(w['word'], size=16, weight=ft.FontWeight.W_BOLD, color="blue"),
                        ft.Text(w.get('phonetic') or '', color="grey", size=12),
                    ]),
                    ft.Text(w.get('meaning') or '（待补充）', size=12),
                    ft.Row([
                        ft.Text(f"被选:{w.get('selection_count', 0)}", size=10, color="blue"),
                        ft.Text(f"打印:{w.get('print_count', 0)}", size=10, color="green"),
                        ft.Text(f"背诵:{w.get('recitation_count', 0)}", size=10, color="purple"),
                    ]),
                    ft.Row([
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
    
    def on_refresh(self, e):
        self.load_words()
        self.status_text.value = "已刷新"
        self.status_text.color = "green"
        self.page.update()
    
    def on_export(self, e):
        if not self.words:
            self.status_text.value = "没有单词可导出"
            self.status_text.color = "red"
            self.page.update()
            return
        
        try:
            from pdf_generator import pdf_generator
            
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "vocabulary.pdf")
            
            success, msg = pdf_generator.generate_vocabulary_pdf(self.words, output_path)
            
            if success:
                word_ids = [w['id'] for w in self.words]
                db.increment_print_count(word_ids)
                self.status_text.value = f"PDF已保存到: {output_path}"
                self.status_text.color = "green"
                self.load_words()
            else:
                self.status_text.value = msg
                self.status_text.color = "red"
        except Exception as ex:
            self.status_text.value = f"导出失败: {ex}"
            self.status_text.color = "red"
        
        self.page.update()
    
    def delete_word(self, word_id):
        db.delete_word(word_id)
        self.load_words()
        self.status_text.value = "已删除"
        self.status_text.color = "green"
        self.page.update()
