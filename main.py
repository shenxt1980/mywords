# -*- coding: utf-8 -*-
"""
陌生单词收集与背诵软件 - 主程序入口
"""

import os
import sys
import argparse
import socket

# 添加项目目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import flet as ft
from flet import AppView

# 导入页面模块
from pages.input import InputPage
from pages.manage import ManagePage
from pages.review import ReviewPage
from pages.game import GamePage

from database import db


class VocabularyApp:
    """单词应用主类"""
    
    def __init__(self):
        self.page = None
        self.current_page = None
        self.nav_rail = None
        self.content_area = None
        self.input_page = None
        self.manage_page = None
        self.review_page = None
        self.game_page = None
    
    def main(self, page: ft.Page):
        self.page = page
        self._setup_page()
        self._create_navigation()
        self._create_content_area()
        self._setup_layout()
        self._navigate_to("home")
    
    def _setup_page(self):
        self.page.title = "陌生单词收集与背诵"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window.width = 900
        self.page.window.height = 700
        self.page.window.min_width = 400
        self.page.window.min_height = 500
        
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE,
        )
    
    def _create_navigation(self):
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.HOME_OUTLINED,
                    selected_icon=ft.Icons.HOME,
                    label="首页",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.ADD_BOX_OUTLINED,
                    selected_icon=ft.Icons.ADD_BOX,
                    label="采集",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.LIST_ALT_OUTLINED,
                    selected_icon=ft.Icons.LIST_ALT,
                    label="管理",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SCHOOL_OUTLINED,
                    selected_icon=ft.Icons.SCHOOL,
                    label="背诵",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.GAMES_OUTLINED,
                    selected_icon=ft.Icons.GAMES,
                    label="游戏",
                ),
            ],
            on_change=self._on_nav_change,
            bgcolor=ft.Colors.BLUE_50,
        )
    
    def _create_content_area(self):
        self.content_area = ft.Container(
            content=ft.Column(
                controls=[],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=20,
            expand=True,
        )
    
    def _setup_layout(self):
        main_row = ft.Row(
            controls=[
                self.nav_rail,
                ft.VerticalDivider(width=1),
                self.content_area,
            ],
            expand=True,
        )
        self.page.add(main_row)
    
    def _on_nav_change(self, e):
        index = e.control.selected_index
        pages = ["home", "input", "manage", "review", "game"]
        self._navigate_to(pages[index])
    
    def _navigate_to(self, page_name: str):
        self.content_area.content.controls.clear()
        
        if page_name == "home":
            content = self._build_home_page()
        elif page_name == "input":
            if self.input_page is None:
                self.input_page = InputPage(self.page)
            content = self.input_page.build()
        elif page_name == "manage":
            if self.manage_page is None:
                self.manage_page = ManagePage(self.page)
            content = self.manage_page.build()
        elif page_name == "review":
            if self.review_page is None:
                self.review_page = ReviewPage(self.page)
            content = self.review_page.build()
        elif page_name == "game":
            if self.game_page is None:
                self.game_page = GamePage(self.page)
            content = self.game_page.build()
        else:
            content = ft.Text("页面未找到")
        
        self.content_area.content.controls.append(content)
        self.current_page = page_name
        self.page.update()
    
    def _build_home_page(self) -> ft.Control:
        stats = db.get_statistics()
        
        title = ft.Text(
            "陌生单词收集与背诵软件",
            size=28,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700,
            text_align=ft.TextAlign.CENTER,
        )
        
        subtitle = ft.Text(
            "Vocabulary Collector & Learner",
            size=14,
            color=ft.Colors.GREY_600,
            text_align=ft.TextAlign.CENTER,
            italic=True,
        )
        
        stats_cards = ft.Row(
            controls=[
                self._create_stat_card("单词总数", str(stats['total_words']), ft.Colors.BLUE_600),
                self._create_stat_card("选择次数", str(stats['total_selections']), ft.Colors.GREEN_600),
                self._create_stat_card("打印次数", str(stats['total_prints']), ft.Colors.ORANGE_600),
                self._create_stat_card("背诵次数", str(stats['total_recitations']), ft.Colors.PURPLE_600),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15,
            wrap=True,
        )
        
        features = ft.Column(
            controls=[
                ft.Text("功能介绍", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                ft.Container(height=10),
                self._create_feature_item(ft.Icons.ADD_BOX, "单词采集", "支持粘贴文本或上传图片", ft.Colors.GREEN_600),
                self._create_feature_item(ft.Icons.LIST_ALT, "单词管理", "查看、编辑、导出PDF", ft.Colors.BLUE_600),
                self._create_feature_item(ft.Icons.SCHOOL, "背诵复习", "浏览模式和默写模式", ft.Colors.PURPLE_600),
                self._create_feature_item(ft.Icons.GAMES, "连连看游戏", "趣味单词匹配", ft.Colors.PINK_600),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        quick_start = ft.Row(
            controls=[
                ft.ElevatedButton(
                    "开始采集",
                    icon=ft.Icons.ADD,
                    on_click=lambda e: self._navigate_to("input"),
                    bgcolor=ft.Colors.GREEN_600,
                    color=ft.Colors.WHITE,
                    width=150,
                    height=45,
                ),
                ft.ElevatedButton(
                    "开始背诵",
                    icon=ft.Icons.SCHOOL,
                    on_click=lambda e: self._navigate_to("review"),
                    bgcolor=ft.Colors.PURPLE_600,
                    color=ft.Colors.WHITE,
                    width=150,
                    height=45,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )
        
        return ft.Column(
            controls=[
                ft.Container(height=20),
                title,
                ft.Container(height=5),
                subtitle,
                ft.Container(height=25),
                stats_cards,
                ft.Container(height=25),
                ft.Divider(),
                ft.Container(height=15),
                features,
                ft.Container(height=25),
                quick_start,
            ],
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )
    
    def _create_stat_card(self, label: str, value: str, color: str) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(label, size=11, color=ft.Colors.GREY_600),
                    ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=color),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.WHITE,
            padding=12,
            border_radius=8,
            width=120,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
    
    def _create_feature_item(self, icon: str, title: str, description: str, color: str) -> ft.Control:
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, color=color, size=26),
                    ft.Column(
                        controls=[
                            ft.Text(title, size=13, weight=ft.FontWeight.BOLD, color=color),
                            ft.Text(description, size=11, color=ft.Colors.GREY_600),
                        ],
                        spacing=2,
                    ),
                ],
                spacing=12,
            ),
            padding=8,
            width=350,
        )


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


def run_app():
    app = VocabularyApp()
    ft.app(target=app.main)


if __name__ == "__main__":
    print("=" * 50)
    print(">> 单词背诵软件启动中...")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--web":
        local_ip = get_local_ip()
        port = 8555
        if len(sys.argv) > 2:
            try:
                port = int(sys.argv[2])
            except:
                pass
        
        print(f"[电脑] http://localhost:{port}")
        print(f"[手机] http://{local_ip}:{port}")
        print("=" * 50)
        print("[提示] 请确保手机和电脑在同一WiFi网络下")
        print("=" * 50)
        
        os.environ["FLET_SERVER_PORT"] = str(port)
        
        app = VocabularyApp()
        ft.app(
            target=app.main,
            view=AppView.WEB_BROWSER,
            port=port,
        )
    else:
        print("[桌面模式] 启动中...")
        print("=" * 50)
        run_app()
