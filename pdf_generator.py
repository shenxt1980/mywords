# -*- coding: utf-8 -*-
"""
PDF生成模块 - 生成单词表的PDF文件
"""

import os
import hashlib
from datetime import datetime
from typing import List, Dict

# 修复 Python 3.8 + reportlab 4.x 的 hashlib 兼容性问题
_original_md5 = hashlib.md5
def _fixed_md5(*args, **kwargs):
    # 移除不兼容的参数
    kwargs.pop('usedforsecurity', None)
    return _original_md5(*args, **kwargs)
hashlib.md5 = _fixed_md5

_original_sha1 = hashlib.sha1
def _fixed_sha1(*args, **kwargs):
    kwargs.pop('usedforsecurity', None)
    return _original_sha1(*args, **kwargs)
hashlib.sha1 = _fixed_sha1

PDF_AVAILABLE = False
PDF_ERROR_MSG = ""

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    PDF_AVAILABLE = True
except ImportError as e:
    PDF_ERROR_MSG = f"reportlab未安装: {e}"
except Exception as e:
    PDF_ERROR_MSG = f"reportlab加载失败: {e}"


class PDFGenerator:
    """PDF生成器"""
    
    def __init__(self):
        self.chinese_font_registered = False
        self.font_name = 'Helvetica'
        self._register_chinese_font()
    
    def _register_chinese_font(self):
        """注册中文字体"""
        if self.chinese_font_registered:
            return
        
        font_paths = [
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simsun.ttc",
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                    self.chinese_font_registered = True
                    self.font_name = 'ChineseFont'
                    print(f"成功注册中文字体: {font_path}")
                    return
                except Exception as e:
                    print(f"字体注册失败: {e}")
                    continue
        
        print("警告: 未找到中文字体，使用默认字体")
    
    def is_available(self) -> tuple:
        if not PDF_AVAILABLE:
            return False, PDF_ERROR_MSG
        return True, ""
    
    def generate_vocabulary_pdf(self, words: List[Dict], output_path: str,
                                  title: str = "陌生单词表") -> tuple:
        if not PDF_AVAILABLE:
            return False, PDF_ERROR_MSG
        
        if not words:
            return False, "没有单词"
        
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=20*mm,
                bottomMargin=20*mm
            )
            
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=18,
                alignment=TA_CENTER,
                spaceAfter=20,
                fontName=self.font_name
            )
            
            normal_style = ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontSize=10,
                fontName=self.font_name,
                leading=14
            )
            
            story = []
            story.append(Paragraph(title, title_style))
            
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            story.append(Paragraph(f"生成时间: {date_str}  共 {len(words)} 个单词", normal_style))
            story.append(Spacer(1, 10*mm))
            
            # 表格数据
            table_data = [['序号', '单词', '音标', '词性', '含义']]
            
            for idx, w in enumerate(words, 1):
                meaning = w.get('meaning') or ''
                if len(meaning) > 35:
                    meaning = meaning[:32] + "..."
                table_data.append([
                    str(idx),
                    w.get('word', ''),
                    w.get('phonetic') or '',
                    w.get('part_of_speech') or '',
                    meaning
                ])
            
            col_widths = [15*mm, 35*mm, 30*mm, 15*mm, 85*mm]
            table = Table(table_data, colWidths=col_widths)
            
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('ALIGN', (0, 1), (0, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)]),
            ]))
            
            # 分页
            per_page = 30
            if len(words) > per_page:
                for i in range(0, len(table_data), per_page):
                    if i > 0:
                        story.append(PageBreak())
                    page_data = table_data[i:i+per_page]
                    if i > 0:
                        page_data = [['序号', '单词', '音标', '词性', '含义']] + page_data[1:]
                    pt = Table(page_data, colWidths=col_widths)
                    pt.setStyle(table.getStyle())
                    story.append(pt)
            else:
                story.append(table)
            
            doc.build(story)
            
            return True, f"PDF已保存: {output_path}"
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"PDF生成失败: {e}"


pdf_generator = PDFGenerator()
