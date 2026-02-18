# -*- coding: utf-8 -*-
"""
单词管理页面 - 查看、编辑、删除单词，以及导出PDF
"""

import os
import flet as ft
from typing import List, Dict, Callable

# 导入其他模块
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from pdf_generator import pdf_generator
from utils.dictionary import dictionary_api


class ManagePage:
    """单词管理页面"""
    
    def __init__(self, page: ft.Page, on_navigate: Callable = None):
        """
        初始化单词管理页面
        
        参数:
            page: Flet页面对象
            on_navigate: 导航回调函数
        """
        self.page = page
        self.on_navigate = on_navigate
        
        # 状态变量
        self.current_sort = "alphabetical"  # 当前排序方式
        self.all_words: List[Dict] = []  # 所有单词
        self.selected_ids: set = set()  # 选中的单词ID
        
        # UI组件
        self.word_list = None
        self.status_text = None
        self.search_input = None
        self.edit_dialog = None
    
    def build(self) -> ft.Control:
        """构建页面UI"""
        
        # 标题
        title = ft.Text(
            "单词管理",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.BLUE_700
        )
        
        # 搜索框
        self.search_input = ft.TextField(
            label="搜索单词",
            hint_text="输入单词或含义...",
            prefix_icon=ft.icons.SEARCH,
            on_submit=self._on_search,
            border_color=ft.colors.BLUE_400,
            expand=True,
        )
        
        search_button = ft.IconButton(
            icon=ft.icons.SEARCH,
            on_click=self._on_search,
            bgcolor=ft.colors.BLUE_100,
        )
        
        # 排序选择
        sort_dropdown = ft.Dropdown(
            label="排序方式",
            options=[
                ft.dropdown.Option("alphabetical", "字典序 A-Z"),
                ft.dropdown.Option("selection_desc", "高频词优先"),
                ft.dropdown.Option("print_asc", "未打印优先"),
            ],
            value=self.current_sort,
            on_change=self._on_sort_change,
            width=180,
        )
        
        # 按钮行
        buttons_row = ft.Row(
            controls=[
                ft.ElevatedButton(
                    "刷新",
                    icon=ft.icons.REFRESH,
                    on_click=self._on_refresh,
                    bgcolor=ft.colors.BLUE_600,
                    color=ft.colors.WHITE,
                ),
                ft.ElevatedButton(
                    "全选",
                    icon=ft.icons.SELECT_ALL,
                    on_click=self._on_select_all,
                    bgcolor=ft.colors.GREEN_600,
                    color=ft.colors.WHITE,
                ),
                ft.ElevatedButton(
                    "取消",
                    icon=ft.icons.DESELECT,
                    on_click=self._on_deselect_all,
                    bgcolor=ft.colors.GREY_400,
                    color=ft.colors.WHITE,
                ),
                ft.ElevatedButton(
                    "导出PDF",
                    icon=ft.icons.PICTURE_AS_PDF,
                    on_click=self._on_export_pdf,
                    bgcolor=ft.colors.RED_600,
                    color=ft.colors.WHITE,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )
        
        # 统计信息
        self.stats_text = ft.Text("", size=14, color=ft.colors.GREY_700)
        
        # 单词列表
        self.word_list = ft.Column(
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        # 状态文本
        self.status_text = ft.Text("", size=14)
        
        # 加载单词
        self._load_words()
        
        # 主布局
        return ft.Column(
            controls=[
                title,
                ft.Container(height=10),
                ft.Row(controls=[self.search_input, search_button]),
                ft.Container(height=10),
                ft.Row(
                    controls=[sort_dropdown, buttons_row],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(height=10),
                self.stats_text,
                ft.Container(height=10),
                ft.Divider(),
                self.word_list,
                ft.Container(height=10),
                self.status_text,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
    
    def _load_words(self, search_keyword: str = ""):
        """加载单词列表"""
        if search_keyword:
            self.all_words = db.search_words(search_keyword)
        else:
            self.all_words = db.get_all_words(self.current_sort)
        
        self._display_words()
        self._update_stats()
    
    def _display_words(self):
        """显示单词列表"""
        self.word_list.controls.clear()
        
        if not self.all_words:
            self.word_list.controls.append(
                ft.Container(
                    content=ft.Text(
                        "暂无单词，请先添加单词",
                        size=16,
                        color=ft.colors.GREY_500,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.alignment.center,
                    padding=50,
                )
            )
            self.page.update()
            return
        
        for word_info in self.all_words:
            word_id = word_info['id']
            is_selected = word_id in self.selected_ids
            
            # 创建单词卡片
            card = self._create_word_card(word_info, is_selected)
            self.word_list.controls.append(card)
        
        self.page.update()
    
    def _create_word_card(self, word_info: Dict, is_selected: bool) -> ft.Control:
        """创建单个单词卡片"""
        word_id = word_info['id']
        word = word_info.get('word', '')
        meaning = word_info.get('meaning', '') or '（待补充含义）'
        phonetic = word_info.get('phonetic', '')
        part_of_speech = word_info.get('part_of_speech', '')
        
        selection_count = word_info.get('selection_count', 0)
        print_count = word_info.get('print_count', 0)
        recitation_count = word_info.get('recitation_count', 0)
        
        # 单词和音标行
        word_row = ft.Row(
            controls=[
                ft.Checkbox(
                    value=is_selected,
                    on_change=lambda e, wid=word_id: self._on_checkbox_change(e, wid),
                ),
                ft.Text(
                    word,
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLUE_800,
                ),
                ft.Text(
                    phonetic,
                    size=14,
                    color=ft.colors.GREY_600,
                    italic=True,
                ) if phonetic else ft.Container(),
                ft.Text(
                    part_of_speech,
                    size=12,
                    color=ft.colors.GREEN_700,
                    bgcolor=ft.colors.GREEN_50,
                ) if part_of_speech else ft.Container(),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        # 含义行
        meaning_row = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(
                        meaning,
                        size=14,
                        color=ft.colors.BLACK87,
                    ),
                    padding=ft.padding.only(left=40),
                    expand=True,
                )
            ]
        )
        
        # 统计信息行
        stats_row = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(
                        f"被选: {selection_count}次",
                        size=11,
                        color=ft.colors.BLUE_600,
                    ),
                    padding=ft.padding.only(left=40),
                ),
                ft.Text(
                    f"打印: {print_count}次",
                    size=11,
                    color=ft.colors.GREEN_600,
                ),
                ft.Text(
                    f"背诵: {recitation_count}次",
                    size=11,
                    color=ft.colors.PURPLE_600,
                ),
            ]
        )
        
        # 操作按钮行
        action_row = ft.Row(
            controls=[
                ft.TextButton(
                    "编辑",
                    icon=ft.icons.EDIT,
                    on_click=lambda e, wi=word_info: self._on_edit_word(wi),
                ),
                ft.TextButton(
                    "查词典",
                    icon=ft.icons.DICTIONARY,
                    on_click=lambda e, wi=word_info: self._on_lookup_word(wi),
                ),
                ft.TextButton(
                    "删除",
                    icon=ft.icons.DELETE,
                    on_click=lambda e, wid=word_id: self._on_delete_word(wid),
                ),
            ],
            alignment=ft.MainAxisAlignment.END,
        )
        
        # 整合卡片
        card = ft.Container(
            content=ft.Column(
                controls=[
                    word_row,
                    meaning_row,
                    stats_row,
                    ft.Divider(height=1),
                    action_row,
                ]
            ),
            bgcolor=ft.colors.BLUE_50 if is_selected else ft.colors.WHITE,
            border=ft.border.all(1, ft.colors.BLUE_200 if is_selected else ft.colors.GREY_300),
            border_radius=8,
            padding=10,
            margin=ft.margin.only(bottom=5),
            on_click=lambda e, wid=word_id: self._on_card_click(wid),
        )
        
        return card
    
    def _on_card_click(self, word_id: int):
        """卡片点击事件"""
        if word_id in self.selected_ids:
            self.selected_ids.discard(word_id)
        else:
            self.selected_ids.add(word_id)
        self._display_words()
    
    def _on_checkbox_change(self, e, word_id: int):
        """复选框变化事件"""
        if e.control.value:
            self.selected_ids.add(word_id)
        else:
            self.selected_ids.discard(word_id)
    
    def _on_sort_change(self, e):
        """排序方式改变"""
        self.current_sort = e.control.value
        self._load_words(self.search_input.value or "")
    
    def _on_search(self, e):
        """搜索单词"""
        keyword = self.search_input.value.strip()
        self._load_words(keyword if keyword else "")
    
    def _on_refresh(self, e):
        """刷新列表"""
        self.search_input.value = ""
        self.selected_ids.clear()
        self._load_words()
        self.status_text.value = "✓ 已刷新"
        self.status_text.color = ft.colors.GREEN_600
        self.page.update()
    
    def _on_select_all(self, e):
        """全选"""
        self.selected_ids = {w['id'] for w in self.all_words}
        self._display_words()
        self.status_text.value = f"✓ 已选中 {len(self.selected_ids)} 个单词"
        self.status_text.color = ft.colors.BLUE_600
        self.page.update()
    
    def _on_deselect_all(self, e):
        """取消全选"""
        self.selected_ids.clear()
        self._display_words()
        self.status_text.value = "✓ 已取消选择"
        self.status_text.color = ft.colors.GREY_600
        self.page.update()
    
    def _on_export_pdf(self, e):
        """导出选中单词为PDF"""
        # 获取要导出的单词
        if self.selected_ids:
            words_to_export = [w for w in self.all_words if w['id'] in self.selected_ids]
        else:
            words_to_export = self.all_words
        
        if not words_to_export:
            self.status_text.value = "⚠️ 没有可导出的单词"
            self.status_text.color = ft.colors.ORANGE_600
            self.page.update()
            return
        
        # 生成PDF
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"vocabulary_{len(words_to_export)}_words.pdf")
        
        success, message = pdf_generator.generate_vocabulary_pdf(words_to_export, output_path)
        
        if success:
            # 更新打印次数
            word_ids = [w['id'] for w in words_to_export]
            db.increment_print_count(word_ids)
            
            self.status_text.value = f"✓ {message}"
            self.status_text.color = ft.colors.GREEN_600
            
            # 刷新列表
            self._load_words(self.search_input.value or "")
        else:
            self.status_text.value = f"❌ {message}"
            self.status_text.color = ft.colors.RED_500
        
        self.page.update()
    
    def _on_edit_word(self, word_info: Dict):
        """编辑单词"""
        word_id = word_info['id']
        
        # 创建输入字段
        word_input = ft.TextField(label="单词", value=word_info.get('word', ''))
        meaning_input = ft.TextField(label="中文含义", value=word_info.get('meaning', '') or '', multiline=True, min_lines=2, max_lines=4)
        phonetic_input = ft.TextField(label="音标", value=word_info.get('phonetic', '') or '')
        pos_input = ft.TextField(label="词性", value=word_info.get('part_of_speech', '') or '')
        example_input = ft.TextField(label="例句", value=word_info.get('example_sentence', '') or '', multiline=True, min_lines=2, max_lines=4)
        
        def on_save(e):
            # 保存修改
            db.update_word(
                word_id,
                word=word_input.value,
                meaning=meaning_input.value,
                phonetic=phonetic_input.value,
                part_of_speech=pos_input.value,
                example_sentence=example_input.value,
            )
            self.edit_dialog.open = False
            self.page.update()
            self._load_words(self.search_input.value or "")
            self.status_text.value = "✓ 已保存修改"
            self.status_text.color = ft.colors.GREEN_600
            self.page.update()
        
        def on_cancel(e):
            self.edit_dialog.open = False
            self.page.update()
        
        # 创建对话框
        self.edit_dialog = ft.AlertDialog(
            title=ft.Text("编辑单词"),
            content=ft.Column(
                controls=[
                    word_input,
                    meaning_input,
                    phonetic_input,
                    pos_input,
                    example_input,
                ],
                scroll=ft.ScrollMode.AUTO,
                width=400,
                height=350,
            ),
            actions=[
                ft.TextButton("取消", on_click=on_cancel),
                ft.ElevatedButton("保存", on_click=on_save, bgcolor=ft.colors.BLUE_600, color=ft.colors.WHITE),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = self.edit_dialog
        self.edit_dialog.open = True
        self.page.update()
    
    def _on_lookup_word(self, word_info: Dict):
        """查词典获取含义"""
        word = word_info.get('word', '')
        
        self.status_text.value = f"⏳ 正在查询 '{word}' 的释义..."
        self.status_text.color = ft.colors.BLUE_600
        self.page.update()
        
        # 调用词典API
        result = dictionary_api.lookup_word(word)
        
        if result:
            # 更新数据库
            db.update_word(
                word_info['id'],
                meaning=result.get('meaning', ''),
                phonetic=result.get('phonetic', ''),
                part_of_speech=result.get('part_of_speech', ''),
                example_sentence=result.get('example', ''),
            )
            self._load_words(self.search_input.value or "")
            self.status_text.value = f"✓ 已更新 '{word}' 的释义"
            self.status_text.color = ft.colors.GREEN_600
        else:
            self.status_text.value = f"⚠️ 未能找到 '{word}' 的释义"
            self.status_text.color = ft.colors.ORANGE_600
        
        self.page.update()
    
    def _on_delete_word(self, word_id: int):
        """删除单词"""
        word_info = db.get_word_by_id(word_id)
        word = word_info.get('word', '') if word_info else ''
        
        def on_confirm(e):
            db.delete_word(word_id)
            self.selected_ids.discard(word_id)
            self.confirm_dialog.open = False
            self._load_words(self.search_input.value or "")
            self.status_text.value = f"✓ 已删除 '{word}'"
            self.status_text.color = ft.colors.GREEN_600
            self.page.update()
        
        def on_cancel(e):
            self.confirm_dialog.open = False
            self.page.update()
        
        # 创建确认对话框
        self.confirm_dialog = ft.AlertDialog(
            title=ft.Text("确认删除"),
            content=ft.Text(f"确定要删除单词 '{word}' 吗？此操作不可恢复。"),
            actions=[
                ft.TextButton("取消", on_click=on_cancel),
                ft.ElevatedButton(
                    "删除",
                    on_click=on_confirm,
                    bgcolor=ft.colors.RED_600,
                    color=ft.colors.WHITE,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = self.confirm_dialog
        self.confirm_dialog.open = True
        self.page.update()
    
    def _update_stats(self):
        """更新统计信息"""
        stats = db.get_statistics()
        self.stats_text.value = (
            f"共 {stats['total_words']} 个单词 | "
            f"总选择 {stats['total_selections']} 次 | "
            f"总打印 {stats['total_prints']} 次 | "
            f"总背诵 {stats['total_recitations']} 次"
        )
