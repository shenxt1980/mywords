# 陌生单词收集与背诵软件 - 环境搭建指南

## 📋 目录
1. [环境要求](#环境要求)
2. [安装步骤](#安装步骤)
3. [VSCode配置](#vscode配置)
4. [启动程序](#启动程序)
5. [手机访问](#手机访问)
6. [常见问题](#常见问题)

---

## 环境要求

- **操作系统**: Windows 10/11、macOS 10.14+、或 Linux
- **Python**: 3.9 - 3.11（推荐 3.10）
- **内存**: 至少 4GB（OCR功能需要）
- **硬盘**: 至少 2GB 可用空间（OCR模型约1GB）

---

## 安装步骤

### 第一步：安装 Python

#### Windows:
1. 访问 https://www.python.org/downloads/
2. 下载 Python 3.10（推荐版本）
3. 运行安装程序
4. **重要**: 勾选 "Add Python to PATH"
5. 点击 "Install Now"

#### 验证安装:
打开命令提示符（按 Win+R，输入 `cmd`），输入:
```
python --version
```
应该显示类似 `Python 3.10.x`

### 第二步：创建项目文件夹并下载代码

1. 创建文件夹:
```
mkdir vocab_app
cd vocab_app
```

2. 将提供的代码文件放入该文件夹，确保目录结构如下:
```
vocab_app/
├── main.py
├── database.py
├── ocr_handler.py
├── pdf_generator.py
├── requirements.txt
├── pages/
│   ├── __init__.py
│   ├── input.py
│   ├── manage.py
│   ├── review.py
│   └── game.py
├── utils/
│   ├── __init__.py
│   └── dictionary.py
├── uploads/
└── output/
```

### 第三步：创建虚拟环境（推荐）

```
python -m venv venv
```

激活虚拟环境:
- Windows:
```
venv\Scripts\activate
```
- macOS/Linux:
```
source venv/bin/activate
```

### 第四步：安装依赖包

**重要**: 由于 EasyOCR 依赖较多，我们分步安装:

1. 先安装核心框架:
```
pip install flet
```

2. 安装PDF生成库:
```
pip install reportlab Pillow
```

3. 安装OCR库（这一步需要较长时间，约5-15分钟）:
```
pip install easyocr
```

如果 easyocr 安装太慢，可以使用国内镜像:
```
pip install easyocr -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 第五步：验证安装

运行以下命令检查是否安装成功:
```
python -c "import flet; print('Flet:', flet.__version__)"
python -c "import easyocr; print('EasyOCR OK')"
python -c "import reportlab; print('ReportLab OK')"
```

---

## VSCode 配置

### 1. 安装 VSCode
- 下载: https://code.visualstudio.com/
- 安装时勾选 "添加到右键菜单"

### 2. 安装推荐插件

打开 VSCode，按 `Ctrl+Shift+X` 打开扩展面板，搜索并安装:

| 插件名 | 用途 |
|--------|------|
| Python | Python 语言支持（必须） |
| Pylance | 智能提示（推荐） |
| Chinese Language Pack | 中文界面（可选） |
| Code Runner | 快速运行代码（可选） |

### 3. 打开项目

1. 打开 VSCode
2. 文件 → 打开文件夹 → 选择 `vocab_app` 文件夹
3. 如果弹出 "是否信任此文件夹"，选择 "是"

### 4. 选择 Python 解释器

1. 按 `Ctrl+Shift+P`
2. 输入 "Python: Select Interpreter"
3. 选择你创建的虚拟环境中的 Python

---

## 启动程序

### 方法一：命令行启动

打开终端（VSCode 中按 `Ctrl+` `），输入:

**桌面模式**（在独立窗口中运行）:
```
python main.py
```

**Web模式**（浏览器访问，手机可访问）:
```
python main.py --web
```

指定端口:
```
python main.py --web --port 8080
```

### 方法二：VSCode 直接运行

1. 打开 `main.py` 文件
2. 点击右上角的 ▶ 运行按钮
3. 或按 `F5` 调试运行

---

## 手机访问

### 前提条件
- 手机和电脑连接到同一个 WiFi 网络
- 电脑防火墙允许 Python 通过

### 步骤

1. **以Web模式启动程序**:
```
python main.py --web
```

2. **查看控制台输出**，会显示类似:
```
==================================================
🚀 单词背诵软件已启动!
==================================================
📱 电脑访问: http://localhost:8555
📱 手机访问: http://192.168.1.100:8555
==================================================
⚠️ 请确保手机和电脑在同一WiFi网络下
==================================================
```

3. **在手机浏览器中输入**显示的地址（如 `http://192.168.1.100:8555`）

### Windows 防火墙设置

如果手机无法访问，需要允许 Python 通过防火墙:

1. 控制面板 → Windows Defender 防火墙 → 允许应用通过防火墙
2. 点击 "更改设置" → "允许其他应用"
3. 找到 Python 并勾选 "专用" 和 "公用"
4. 或者临时关闭防火墙测试

---

## 常见问题

### Q1: `pip install easyocr` 报错

**原因**: easyocr 依赖 torch（深度学习框架），下载较大

**解决方案**:
1. 使用国内镜像:
```
pip install torch -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install easyocr -i https://pypi.tuna.tsinghua.edu.cn/simple
```

2. 如果还是失败，可以只安装 CPU 版本的 torch:
```
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install easyocr
```

### Q2: OCR 识别很慢

**原因**: EasyOCR 首次使用需要下载模型文件

**解决方案**:
- 第一次使用时耐心等待（约1-3分钟）
- 之后会使用缓存的模型，速度会快很多

### Q3: 程序启动后闪退

**原因**: 可能是端口被占用或依赖未正确安装

**解决方案**:
1. 检查依赖:
```
pip install -r requirements.txt
```

2. 更换端口:
```
python main.py --web --port 9000
```

### Q4: PDF 中文显示为方框

**原因**: 系统缺少中文字体

**解决方案**:
- Windows: 通常已有中文字体，无需额外配置
- Linux: 安装中文字体
```
sudo apt-get install fonts-wqy-microhei
```

### Q5: 手机无法访问

**解决方案**:
1. 确认手机和电脑在同一 WiFi
2. 检查防火墙设置
3. 尝试关闭 Windows 防火墙测试
4. 使用 `ipconfig` 确认电脑IP地址

### Q6: 词典API查询失败

**原因**: 网络问题或API不可用

**解决方案**:
- 程序内置了常用单词词典，可离线使用
- 对于在线查询，检查网络连接
- 可以手动编辑单词含义

---

## 项目文件说明

| 文件 | 说明 |
|------|------|
| main.py | 主程序入口 |
| database.py | 数据库操作（SQLite） |
| ocr_handler.py | OCR文字识别 |
| pdf_generator.py | PDF生成 |
| pages/input.py | 单词采集页面 |
| pages/manage.py | 单词管理页面 |
| pages/review.py | 背诵复习页面 |
| pages/game.py | 连连看游戏页面 |
| utils/dictionary.py | 词典API工具 |

---

## 快速测试

安装完成后，运行以下命令测试:

```bash
# 进入项目目录
cd vocab_app

# 启动程序（桌面模式）
python main.py
```

如果一切正常，会弹出一个窗口显示应用程序界面。

---

## 联系与反馈

如有问题，请检查:
1. Python 版本是否正确（3.9-3.11）
2. 所有依赖是否安装成功
3. 查看终端错误信息

祝使用愉快！
