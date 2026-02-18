# -*- coding: utf-8 -*-
"""
连连看游戏页面 - 匹配英文和中文
"""

import os
import random
import flet as ft
from typing import List, Dict, Callable, Optional

# 导入其他模块
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db


class GamePage:
    """连连看游戏页面"""
    
    def __init__(self, page: ft.Page, on_navigate: Callable = None):
        """
        初始化游戏页面
        
        参数:
            page: Flet页面对象
            on_navigate: 导航回调函数
        """
        self.page = page
        self.on_navigate = on_navigate
        
        # 游戏状态
        self.game_words: List[Dict] = []  # 游戏单词列表
        self.game_blocks: List[Dict] = []  # 游戏方块列表
        self.selected_block: Optional[Dict] = None  # 当前选中的方块
        self.matched_pairs: int = 0  # 已匹配的配对数
        self.total_pairs: int = 0  # 总配对数
        self.score: int = 0  # 得分
        self.game_active: bool = False  # 游戏是否进行中
        
        # UI组件
        self.game_grid = None
        self.status_text = None
        self.score_text = None
    
    def build(self) -> ft.Control:
        """构建页面UI"""
        
        # 标题
        title = ft.Text(
            "单词连连看",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.PINK_700
        )
        
        # 说明
        description = ft.Text(
            "点击英文和对应的中文进行匹配，匹配正确则消除",
            size=14,
            color=ft.colors.GREY_600,
            text_align=ft.TextAlign.CENTER,
        )
        
        # 游戏设置
        settings_row = ft.Row(
            controls=[
                ft.Text("单词数量:", size=14),
                ft.Dropdown(
                    options=[
                        ft.dropdown.Option("4"),
                        ft.dropdown.Option("6"),
                        ft.dropdown.Option("8"),
                        ft.dropdown.Option("10"),
                    ],
                    value="6",
                    width=80,
                ),
                ft.ElevatedButton(
                    "开始游戏",
                    icon=ft.icons.PLAY_ARROW,
                    on_click=self._on_start_game,
                    bgcolor=ft.colors.GREEN_600,
                    color=ft.colors.WHITE,
                ),
                ft.ElevatedButton(
                    "重新开始",
                    icon=ft.icons.REFRESH,
                    on_click=self._on_restart_game,
                    bgcolor=ft.colors.BLUE_600,
                    color=ft.colors.WHITE,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15,
        )
        
        self.count_dropdown = settings_row.controls[1]
        
        # 得分显示
        self.score_text = ft.Text(
            "得分: 0",
            size=18,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.PURPLE_700,
        )
        
        # 进度显示
        self.progress_text = ft.Text(
            "配对: 0 / 0",
            size=14,
            color=ft.colors.GREY_600,
        )
        
        # 游戏网格
        self.game_grid = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text(
                        "点击「开始游戏」开始",
                        size=18,
                        color=ft.colors.GREY_500,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.alignment.center,
                    height=300,
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        # 状态文本
        self.status_text = ft.Text("", size=14)
        
        # 主布局
        return ft.Column(
            controls=[
                title,
                ft.Container(height=10),
                description,
                ft.Container(height=20),
                settings_row,
                ft.Container(height=15),
                ft.Row(
                    controls=[self.score_text, self.progress_text],
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                ),
                ft.Container(height=15),
                ft.Divider(),
                ft.Container(height=10),
                self.game_grid,
                ft.Container(height=10),
                self.status_text,
            ],
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )
    
    def _on_start_game(self, e):
        """开始游戏"""
        count = int(self.count_dropdown.value)
        
        # 获取单词（需要有含义的单词）
        all_words = db.get_all_words("random")
        words_with_meaning = [w for w in all_words if w.get('meaning')]
        
        if len(words_with_meaning) < count:
            self.status_text.value = f"⚠️ 有含义的单词不足 {count} 个，请先添加单词和含义"
            self.status_text.color = ft.colors.ORANGE_600
            self.page.update()
            return
        
        # 随机选择单词
        self.game_words = random.sample(words_with_meaning, count)
        self.total_pairs = count
        self.matched_pairs = 0
        self.score = 0
        self.selected_block = None
        self.game_active = True
        
        # 创建游戏方块
        self._create_game_blocks()
        
        self._update_display()
        
        self.status_text.value = "✓ 游戏开始！点击方块进行匹配"
        self.status_text.color = ft.colors.GREEN_600
        self.page.update()
    
    def _on_restart_game(self, e):
        """重新开始游戏"""
        if self.game_words:
            self._on_start_game(e)
        else:
            self.status_text.value = "⚠️ 请先点击「开始游戏」"
            self.status_text.color = ft.colors.ORANGE_600
            self.page.update()
    
    def _create_game_blocks(self):
        """创建游戏方块"""
        self.game_blocks = []
        
        # 创建英文和中文方块
        for word_info in self.game_words:
            # 英文方块
            self.game_blocks.append({
                'id': f"en_{word_info['id']}",
                'text': word_info['word'],
                'type': 'english',
                'pair_id': word_info['id'],
                'matched': False,
                'selected': False,
            })
            # 中文方块
            self.game_blocks.append({
                'id': f"cn_{word_info['id']}",
                'text': word_info.get('meaning', '')[:15],  # 限制长度
                'type': 'chinese',
                'pair_id': word_info['id'],
                'matched': False,
                'selected': False,
            })
        
        # 随机打乱
        random.shuffle(self.game_blocks)
        
        # 显示游戏网格
        self._display_game_grid()
    
    def _display_game_grid(self):
        """显示游戏网格"""
        self.game_grid.controls.clear()
        
        # 计算列数（根据方块数量调整）
        total_blocks = len(self.game_blocks)
        cols = 4 if total_blocks <= 12 else 5
        
        # 按行分组
        rows = []
        current_row_controls = []
        
        for i, block in enumerate(self.game_blocks):
            # 创建方块按钮
            btn = ft.Container(
                content=ft.Text(
                    block['text'],
                    size=12,
                    text_align=ft.TextAlign.CENTER,
                    color=ft.colors.WHITE if block['type'] == 'english' else ft.colors.BLACK87,
                    no_wrap=True,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                bgcolor=self._get_block_color(block),
                border=ft.border.all(2, ft.colors.BLUE_300 if block['selected'] else ft.colors.TRANSPARENT),
                border_radius=8,
                padding=10,
                width=120,
                height=60,
                alignment=ft.alignment.center,
                on_click=lambda e, bid=block['id']: self._on_block_click(bid),
                visible=not block['matched'],
            )
            
            block['button'] = btn
            current_row_controls.append(btn)
            
            if len(current_row_controls) >= cols:
                rows.append(ft.Row(
                    controls=current_row_controls,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ))
                current_row_controls = []
        
        # 添加最后一行
        if current_row_controls:
            # 补齐空位
            while len(current_row_controls) < cols:
                current_row_controls.append(ft.Container(width=120, height=60))
            rows.append(ft.Row(
                controls=current_row_controls,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ))
        
        # 添加所有行
        for row in rows:
            self.game_grid.controls.append(row)
        
        self.page.update()
    
    def _get_block_color(self, block: Dict) -> str:
        """获取方块颜色"""
        if block['matched']:
            return ft.colors.GREY_400
        if block['selected']:
            return ft.colors.AMBER_400
        if block['type'] == 'english':
            return ft.colors.BLUE_500
        else:
            return ft.colors.GREEN_300
    
    def _on_block_click(self, block_id: str):
        """方块点击事件"""
        if not self.game_active:
            return
        
        # 找到被点击的方块
        clicked_block = None
        for block in self.game_blocks:
            if block['id'] == block_id:
                clicked_block = block
                break
        
        if not clicked_block or clicked_block['matched']:
            return
        
        # 如果没有选中的方块，选中当前方块
        if self.selected_block is None:
            clicked_block['selected'] = True
            self.selected_block = clicked_block
            self._update_block_style(clicked_block)
            return
        
        # 如果点击的是已选中的方块，取消选中
        if clicked_block['id'] == self.selected_block['id']:
            clicked_block['selected'] = False
            self.selected_block = None
            self._update_block_style(clicked_block)
            return
        
        # 检查是否匹配
        if self._check_match(self.selected_block, clicked_block):
            # 匹配成功
            self.selected_block['matched'] = True
            clicked_block['matched'] = True
            self.selected_block['selected'] = False
            clicked_block['selected'] = False
            self.matched_pairs += 1
            self.score += 10
            
            self.status_text.value = "✓ 匹配正确！+10分"
            self.status_text.color = ft.colors.GREEN_600
            
            # 检查游戏是否结束
            if self.matched_pairs >= self.total_pairs:
                self.game_active = False
                self.status_text.value = f"🎉 恭喜完成！最终得分: {self.score}"
                self.status_text.color = ft.colors.PURPLE_600
        else:
            # 匹配失败
            self.selected_block['selected'] = False
            self.score = max(0, self.score - 2)
            
            self.status_text.value = "✗ 匹配失败，-2分"
            self.status_text.color = ft.colors.RED_500
        
        self.selected_block = None
        
        # 更新显示
        self._display_game_grid()
        self._update_display()
    
    def _check_match(self, block1: Dict, block2: Dict) -> bool:
        """检查两个方块是否匹配"""
        # 必须是不同类型（一个英文一个中文）
        if block1['type'] == block2['type']:
            return False
        # 配对ID必须相同
        return block1['pair_id'] == block2['pair_id']
    
    def _update_block_style(self, block: Dict):
        """更新方块样式"""
        if 'button' in block:
            btn = block['button']
            btn.bgcolor = self._get_block_color(block)
            btn.border = ft.border.all(2, ft.colors.BLUE_300 if block['selected'] else ft.colors.TRANSPARENT)
            self.page.update()
    
    def _update_display(self):
        """更新显示"""
        self.score_text.value = f"得分: {self.score}"
        self.progress_text.value = f"配对: {self.matched_pairs} / {self.total_pairs}"
        self.page.update()
