# -*- coding: utf-8 -*-
"""
陌生单词收集与背诵软件 - 主程序
"""

import os
import sys
import socket

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import flet as ft

from database import db
from pages.input import InputPage
from pages.manage import ManagePage
from pages.review import ReviewPage
from pages.game import GamePage


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


class App:
    def __init__(self):
        self.page = None
        self.input_page = None
        self.manage_page = None
        self.review_page = None
        self.game_page = None
    
    def main(self, page: ft.Page):
        self.page = page
        
        # 页面设置
        page.title = "陌生单词收集与背诵"
        page.window.width = 900
        page.window.height = 700
        
        # 导航
        def on_nav(e):
            index = e.control.selected_index
            pages = ["home", "input", "manage", "review", "game"]
            self.show_page(pages[index])
        
        self.nav = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=[
                ft.NavigationRailDestination(icon=ft.icons.HOME, label="首页"),
                ft.NavigationRailDestination(icon=ft.icons.ADD_BOX, label="采集"),
                ft.NavigationRailDestination(icon=ft.icons.LIST, label="管理"),
                ft.NavigationRailDestination(icon=ft.icons.SCHOOL, label="背诵"),
                ft.NavigationRailDestination(icon=ft.icons.GAMES, label="游戏"),
            ],
            on_change=on_nav,
        )
        
        self.content = ft.Container(
            content=ft.Column([ft.Text("加载中...")], scroll=ft.ScrollMode.AUTO, expand=True),
            padding=20,
            expand=True,
        )
        
        page.add(
            ft.Row([
                self.nav,
                ft.VerticalDivider(width=1),
                self.content,
            ], expand=True)
        )
        
        self.show_page("home")
    
    def show_page(self, name):
        if name == "home":
            self.content.content = self.build_home()
        elif name == "input":
            if not self.input_page:
                self.input_page = InputPage(self.page)
            self.content.content = self.input_page.build()
        elif name == "manage":
            if not self.manage_page:
                self.manage_page = ManagePage(self.page)
            self.content.content = self.manage_page.build()
        elif name == "review":
            if not self.review_page:
                self.review_page = ReviewPage(self.page)
            self.content.content = self.review_page.build()
        elif name == "game":
            if not self.game_page:
                self.game_page = GamePage(self.page)
            self.content.content = self.game_page.build()
        
        self.page.update()
    
    def build_home(self):
        stats = db.get_statistics()
        
        return ft.Column([
            ft.Container(height=30),
            ft.Text("陌生单词收集与背诵", size=28, weight=ft.FontWeight.BOLD, color="blue"),
            ft.Container(height=20),
            ft.Row([
                self.stat_card("单词总数", stats['total_words'], "blue"),
                self.stat_card("选择次数", stats['total_selections'], "green"),
                self.stat_card("打印次数", stats['total_prints'], "orange"),
                self.stat_card("背诵次数", stats['total_recitations'], "purple"),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=30),
            ft.Divider(),
            ft.Container(height=20),
            ft.ElevatedButton("开始采集单词", on_click=lambda e: self.go_to("input"), width=200, height=50),
            ft.Container(height=10),
            ft.ElevatedButton("开始背诵", on_click=lambda e: self.go_to("review"), width=200, height=50),
            ft.Container(height=20),
            ft.Text("提示: 点击左侧导航切换功能", color="grey"),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def stat_card(self, label, value, color):
        return ft.Container(
            content=ft.Column([
                ft.Text(label, size=12, color="grey"),
                ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD, color=color),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=15,
            border=ft.border.all(1, "grey"),
            border_radius=10,
        )
    
    def go_to(self, name):
        index = {"home": 0, "input": 1, "manage": 2, "review": 3, "game": 4}
        self.nav.selected_index = index.get(name, 0)
        self.show_page(name)


if __name__ == "__main__":
    print("=" * 50)
    print("  陌生单词收集与背诵软件")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--web":
        port = 8555
        if len(sys.argv) > 2:
            try:
                port = int(sys.argv[2])
            except:
                pass
        
        ip = get_local_ip()
        print(f"  电脑访问: http://localhost:{port}")
        print(f"  手机访问: http://{ip}:{port}")
        print("=" * 50)
        print("  提示: 确保手机和电脑在同一WiFi")
        print("=" * 50)
        
        # 设置环境变量让Flet监听所有网络接口
        os.environ["FLET_SERVER_IP"] = "0.0.0.0"
        
        ft.app(target=App().main, view=ft.AppView.WEB_BROWSER, port=port, host="0.0.0.0")
    else:
        print("  启动桌面模式...")
        print("=" * 50)
        ft.app(target=App().main)
