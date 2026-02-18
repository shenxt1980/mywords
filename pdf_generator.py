# -*- coding: utf-8 -*-
"""
PDF生成模块 - 生成单词表的PDF文件
使用 reportlab 库生成A4尺寸的PDF文件
"""

import os
from datetime import datetime
from typing import List, Dict

# PDF库导入检查
PDF_AVAILABLE = False
PDF_ERROR_MSG = ""

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    PDF_AVAILABLE = True
except ImportError as e:
    PDF_ERROR_MSG = f"reportlab未安装，请运行: pip install reportlab。错误: {e}"


class PDFGenerator:
    """PDF生成器"""
    
    def __init__(self):
        """初始化PDF生成器"""
        self.chinese_font_registered = False
        self._register_chinese_font()
    
    def _register_chinese_font(self):
        """注册中文字体"""
        if self.chinese_font_registered:
            return
        
        # 尝试注册常见的中文字体
        font_paths = [
            # Windows字体路径
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simkai.ttf",
            # Linux字体路径
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            # macOS字体路径
            "/System/Library/Fonts/PingFang.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                    self.chinese_font_registered = True
                    print(f"成功注册中文字体: {font_path}")
                    return
                except Exception as e:
                    print(f"注册字体失败 {font_path}: {e}")
                    continue
        
        print("警告: 未找到中文字体，PDF中的中文可能无法正常显示")
    
    def is_available(self) -> tuple:
        """
        检查PDF生成功能是否可用
        
        返回:
            tuple: (是否可用, 错误信息)
        """
        if not PDF_AVAILABLE:
            return False, PDF_ERROR_MSG
        return True, ""
    
    def generate_vocabulary_pdf(self, words: List[Dict], output_path: str,
                                  title: str = "陌生单词表") -> tuple:
        """
        生成单词表PDF
        
        参数:
            words: 单词列表，每个单词是包含word, meaning, phonetic等字段的字典
            output_path: 输出文件路径
            title: PDF标题
        
        返回:
            tuple: (成功标志, 错误信息或成功信息)
        """
        if not PDF_AVAILABLE:
            return False, PDF_ERROR_MSG
        
        if not words:
            return False, "没有单词可以导出"
        
        try:
            # 创建PDF文档
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=20*mm,
                bottomMargin=20*mm
            )
            
            # 获取样式
            styles = getSampleStyleSheet()
            
            # 创建自定义样式
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                alignment=TA_CENTER,
                spaceAfter=20,
                fontName='ChineseFont' if self.chinese_font_registered else 'Helvetica'
            )
            
            header_style = ParagraphStyle(
                'CustomHeader',
                parent=styles['Heading2'],
                fontSize=12,
                fontName='ChineseFont' if self.chinese_font_registered else 'Helvetica',
                spaceAfter=10
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10.5,  # 五号字约10.5pt
                fontName='ChineseFont' if self.chinese_font_registered else 'Helvetica',
                leading=14
            )
            
            # 构建文档内容
            story = []
            
            # 添加标题
            story.append(Paragraph(title, title_style))
            
            # 添加生成日期
            date_str = datetime.now().strftime("%Y年%m月%d日 %H:%M")
            story.append(Paragraph(f"生成时间: {date_str}", normal_style))
            story.append(Paragraph(f"共 {len(words)} 个单词", normal_style))
            story.append(Spacer(1, 10*mm))
            
            # 创建表格数据
            table_data = [['序号', '单词', '音标', '词性', '中文含义']]
            
            for idx, word_info in enumerate(words, 1):
                word = word_info.get('word', '')
                phonetic = word_info.get('phonetic', '') or ''
                part_of_speech = word_info.get('part_of_speech', '') or ''
                meaning = word_info.get('meaning', '') or '（待补充）'
                
                # 处理含义过长的情况
                if len(meaning) > 50:
                    meaning = meaning[:47] + "..."
                
                table_data.append([
                    str(idx),
                    word,
                    phonetic,
                    part_of_speech,
                    meaning
                ])
            
            # 创建表格
            # 列宽: 序号(15mm), 单词(35mm), 音标(35mm), 词性(20mm), 含义(剩余)
            col_widths = [15*mm, 35*mm, 35*mm, 20*mm, 70*mm]
            
            table = Table(table_data, colWidths=col_widths)
            
            # 设置表格样式
            table_style = TableStyle([
                # 整体字体
                ('FONTNAME', (0, 0), (-1, -1), 
                 'ChineseFont' if self.chinese_font_registered else 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),  # 表头字号
                ('FONTSIZE', (0, 1), (-1, -1), 10.5),  # 数据字号（五号）
                # 表头样式
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 
                 'ChineseFont' if self.chinese_font_registered else 'Helvetica-Bold'),
                # 数据行样式
                ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # 序号居中
                ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # 单词左对齐
                ('ALIGN', (2, 1), (-1, -1), 'LEFT'),   # 其他左对齐
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                # 边框
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                # 行间距
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                # 隔行变色
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)]),
            ])
            
            table.setStyle(table_style)
            
            # 分页处理：每页最多30个单词
            words_per_page = 30
            total_pages = (len(words) + words_per_page - 1) // words_per_page
            
            if total_pages > 1:
                # 需要分页
                for page_num in range(total_pages):
                    if page_num > 0:
                        story.append(PageBreak())
                        story.append(Paragraph(f"{title} (第{page_num+1}页)", header_style))
                        story.append(Spacer(1, 5*mm))
                    
                    start_idx = page_num * words_per_page
                    end_idx = min(start_idx + words_per_page + 1, len(table_data))
                    
                    page_table_data = table_data[start_idx:end_idx]
                    if page_num > 0:
                        # 非首页需要调整序号
                        page_table_data = [['序号', '单词', '音标', '词性', '中文含义']]
                        for idx, word_info in enumerate(words[start_idx:end_idx], start_idx + 1):
                            word = word_info.get('word', '')
                            phonetic = word_info.get('phonetic', '') or ''
                            part_of_speech = word_info.get('part_of_speech', '') or ''
                            meaning = word_info.get('meaning', '') or '（待补充）'
                            if len(meaning) > 50:
                                meaning = meaning[:47] + "..."
                            page_table_data.append([str(idx), word, phonetic, part_of_speech, meaning])
                    
                    page_table = Table(page_table_data, colWidths=col_widths)
                    page_table.setStyle(table_style)
                    story.append(page_table)
            else:
                story.append(table)
            
            # 生成PDF
            doc.build(story)
            
            return True, f"PDF已生成: {output_path}"
            
        except Exception as e:
            error_msg = f"PDF生成失败: {e}"
            print(error_msg)
            return False, error_msg
    
    def generate_flashcard_pdf(self, words: List[Dict], output_path: str) -> tuple:
        """
        生成单词卡片PDF（用于打印裁剪）
        
        参数:
            words: 单词列表
            output_path: 输出文件路径
        
        返回:
            tuple: (成功标志, 错误信息或成功信息)
        """
        if not PDF_AVAILABLE:
            return False, PDF_ERROR_MSG
        
        if not words:
            return False, "没有单词可以导出"
        
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=10*mm,
                leftMargin=10*mm,
                topMargin=10*mm,
                bottomMargin=10*mm
            )
            
            styles = getSampleStyleSheet()
            
            card_style = ParagraphStyle(
                'CardStyle',
                parent=styles['Normal'],
                fontSize=14,
                fontName='ChineseFont' if self.chinese_font_registered else 'Helvetica',
                alignment=TA_CENTER,
                leading=18
            )
            
            story = []
            
            # 创建卡片表格：每行2个卡片
            card_data = []
            row = []
            
            for word_info in words:
                word = word_info.get('word', '')
                meaning = word_info.get('meaning', '') or ''
                phonetic = word_info.get('phonetic', '') or ''
                
                card_content = f"<b>{word}</b><br/>{phonetic}<br/>{meaning}"
                row.append(Paragraph(card_content, card_style))
                
                if len(row) == 2:
                    card_data.append(row)
                    row = []
            
            # 处理最后一行
            if row:
                row.append('')  # 补空
                card_data.append(row)
            
            # 创建表格
            table = Table(card_data, colWidths=[90*mm, 90*mm], rowHeights=[60*mm])
            
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1),
                 'ChineseFont' if self.chinese_font_registered else 'Helvetica'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ]))
            
            story.append(table)
            doc.build(story)
            
            return True, f"单词卡片PDF已生成: {output_path}"
            
        except Exception as e:
            return False, f"PDF生成失败: {e}"


# 创建全局PDF生成器实例
pdf_generator = PDFGenerator()
