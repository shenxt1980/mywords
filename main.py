# -*- coding: utf-8 -*-
"""
陌生单词收集与背诵软件 - 主程序入口
使用 Flet 框架实现跨平台Web应用

功能:
1. 单词采集 - 支持文本导入和图片OCR识别
2. 单词管理 - 查看、编辑、删除、导出PDF
3. 背诵复习 - 浏览模式和默写模式
4. 连连看游戏 - 趣味单词匹配

启动方式:
    python main.py
    或
    python main.py --web  # 启动Web服务器模式（手机可访问）
"""

import os
import sys
import argparse
import socket
import flet as ft

# 添加项目目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入页面模块
from pages.input import InputPage
from pages.manage import ManagePage
from pages.review import ReviewPage
from pages.game import GamePage

# 导入其他模块
from database import db


class VocabularyApp:
    """单词应用主类"""
    
    def __init__(self):
        """初始化应用"""
        self.page = None
        self.current_page = None
        self.nav_rail = None
        self.content_area = None
        
        # 页面实例
        self.input_page = None
        self.manage_page = None
        self.review_page = None
        self.game_page = None
    
    def main(self, page: ft.Page):
        """
        主函数 - Flet应用入口
        
        参数:
            page: Flet页面对象
        """
        self.page = page
        
        # 配置页面基本属性
        self._setup_page()
        
        # 创建导航栏
        self._create_navigation()
        
        # 创建内容区域
        self._create_content_area()
        
        # 添加页面布局
        self._setup_layout()
        
        # 默认显示首页
        self._navigate_to("home")
    
    def _setup_page(self):
        """配置页面基本属性"""
        self.page.title = "陌生单词收集与背诵"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window.width = 900
        self.page.window.height = 700
        self.page.window.min_width = 400
        self.page.window.min_height = 500
        
        # 设置主题颜色
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.colors.BLUE,
            use_material3=True,
        )
        
        # 设置字体（支持中文）
        self.page.fonts = {
            "Noto Sans SC": "https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap"
        }
        self.page.theme.font_family = "Noto Sans SC"
    
    def _create_navigation(self):
        """创建导航栏"""
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.HOME_OUTLINED,
                    selected_icon=ft.icons.HOME,
                    label="首页",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.ADD_BOX_OUTLINED,
                    selected_icon=ft.icons.ADD_BOX,
                    label="采集",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.LIST_ALT_OUTLINED,
                    selected_icon=ft.icons.LIST_ALT,
                    label="管理",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SCHOOL_OUTLINED,
                    selected_icon=ft.icons.SCHOOL,
                    label="背诵",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.GAMES_OUTLINED,
                    selected_icon=ft.icons.GAMES,
                    label="游戏",
                ),
            ],
            on_change=self._on_nav_change,
            bgcolor=ft.colors.BLUE_50,
        )
    
    def _create_content_area(self):
        """创建内容区域"""
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
        """设置页面布局"""
        # 主布局行
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
        """导航栏变化事件"""
        index = e.control.selected_index
        pages = ["home", "input", "manage", "review", "game"]
        self._navigate_to(pages[index])
    
    def _navigate_to(self, page_name: str):
        """导航到指定页面"""
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
        """构建首页"""
        # 获取统计信息
        stats = db.get_statistics()
        
        # 标题
        title = ft.Text(
            "陌生单词收集与背诵软件",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.BLUE_700,
            text_align=ft.TextAlign.CENTER,
        )
        
        # 副标题
        subtitle = ft.Text(
            "Vocabulary Collector & Learner",
            size=16,
            color=ft.colors.GREY_600,
            text_align=ft.TextAlign.CENTER,
            italic=True,
        )
        
        # 统计卡片
        stats_cards = ft.Row(
            controls=[
                self._create_stat_card(
                    "📚 单词总数",
                    str(stats['total_words']),
                    ft.colors.BLUE_600
                ),
                self._create_stat_card(
                    "👆 选择次数",
                    str(stats['total_selections']),
                    ft.colors.GREEN_600
                ),
                self._create_stat_card(
                    "🖨️ 打印次数",
                    str(stats['total_prints']),
                    ft.colors.ORANGE_600
                ),
                self._create_stat_card(
                    "📖 背诵次数",
                    str(stats['total_recitations']),
                    ft.colors.PURPLE_600
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
            wrap=True,
        )
        
        # 功能介绍
        features = ft.Column(
            controls=[
                ft.Text("功能介绍", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700),
                ft.Container(height=10),
                self._create_feature_item(
                    ft.icons.ADD_BOX,
                    "单词采集",
                    "支持粘贴文本或上传图片，自动识别英文单词",
                    ft.colors.GREEN_600
                ),
                self._create_feature_item(
                    ft.icons.LIST_ALT,
                    "单词管理",
                    "查看、编辑、删除单词，支持导出PDF打印",
                    ft.colors.BLUE_600
                ),
                self._create_feature_item(
                    ft.icons.SCHOOL,
                    "背诵复习",
                    "浏览模式和默写模式，支持高频词优先",
                    ft.colors.PURPLE_600
                ),
                self._create_feature_item(
                    ft.icons.GAMES,
                    "连连看游戏",
                    "趣味单词匹配游戏，边玩边学",
                    ft.colors.PINK_600
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        # 快速开始按钮
        quick_start = ft.Row(
            controls=[
                ft.ElevatedButton(
                    "开始采集单词",
                    icon=ft.icons.ADD,
                    on_click=lambda e: self._navigate_to("input"),
                    bgcolor=ft.colors.GREEN_600,
                    color=ft.colors.WHITE,
                    width=180,
                    height=50,
                ),
                ft.ElevatedButton(
                    "开始背诵",
                    icon=ft.icons.SCHOOL,
                    on_click=lambda e: self._navigate_to("review"),
                    bgcolor=ft.colors.PURPLE_600,
                    color=ft.colors.WHITE,
                    width=180,
                    height=50,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=30,
        )
        
        # 使用提示
        tips = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("💡 使用提示", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700),
                    ft.Text("1. 在「采集」页面粘贴文本或上传图片，自动提取单词", size=12),
                    ft.Text("2. 在「管理」页面编辑单词含义，或点击「查词典」自动获取", size=12),
                    ft.Text("3. 在「背诵」页面选择模式进行背诵，记录学习进度", size=12),
                    ft.Text("4. 在「游戏」页面通过连连看游戏巩固记忆", size=12),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
            bgcolor=ft.colors.BLUE_50,
            padding=15,
            border_radius=10,
            width=500,
        )
        
        # 整合首页内容
        return ft.Column(
            controls=[
                ft.Container(height=30),
                title,
                ft.Container(height=5),
                subtitle,
                ft.Container(height=30),
                stats_cards,
                ft.Container(height=30),
                ft.Divider(),
                ft.Container(height=20),
                features,
                ft.Container(height=30),
                quick_start,
                ft.Container(height=30),
                ft.Row([tips], alignment=ft.MainAxisAlignment.CENTER),
            ],
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )
    
    def _create_stat_card(self, label: str, value: str, color: str) -> ft.Control:
        """创建统计卡片"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(label, size=12, color=ft.colors.GREY_600),
                    ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color=color),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.colors.WHITE,
            padding=15,
            border_radius=10,
            width=140,
            border=ft.border.all(1, ft.colors.GREY_300),
        )
    
    def _create_feature_item(self, icon: str, title: str, description: str, color: str) -> ft.Control:
        """创建功能介绍项"""
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, color=color, size=30),
                    ft.Column(
                        controls=[
                            ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=color),
                            ft.Text(description, size=12, color=ft.colors.GREY_600),
                        ],
                        spacing=2,
                    ),
                ],
                spacing=15,
            ),
            padding=10,
            width=400,
        )


def get_local_ip():
    """获取本机IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


def run_app(web_mode: bool = False, port: int = 8555):
    """
    运行应用
    
    参数:
        web_mode: 是否以Web模式运行（手机可访问）
        port: Web服务器端口
    """
    app = VocabularyApp()
    
    if web_mode:
        # Web模式 - 手机可通过IP地址访问
        local_ip = get_local_ip()
        print("=" * 50)
        print("🚀 单词背诵软件已启动!")
        print("=" * 50)
        print(f"📱 电脑访问: http://localhost:{port}")
        print(f"📱 手机访问: http://{local_ip}:{port}")
        print("=" * 50)
        print("⚠️ 请确保手机和电脑在同一WiFi网络下")
        print("=" * 50)
        
        ft.app(
            target=app.main,
            view=ft.AppView.WEB_BROWSER,
            port=port,
            host="0.0.0.0",  # 允许外部访问
        )
    else:
        # 桌面模式 - 作为桌面应用运行
        print("=" * 50)
        print("🚀 单词背诵软件已启动!")
        print("=" * 50)
        ft.app(target=app.main)


if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="陌生单词收集与背诵软件")
    parser.add_argument(
        "--web",
        action="store_true",
        help="以Web模式运行，手机可通过浏览器访问"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8555,
        help="Web服务器端口（默认: 8555）"
    )
    
    args = parser.parse_args()
    
    # 运行应用
    run_app(web_mode=args.web, port=args.port)
