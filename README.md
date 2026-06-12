# 测试用例生成工具

一个基于 Python Flask 的测试用例生成系统，支持自动从需求文档和接口文档生成测试用例，并提供多种测试工具。

## 功能特性

### 📝 测试用例生成
- 上传需求文档（支持 .docx, .pdf, .md, .txt）
- 上传接口文档，自动识别 API
- 自动生成功能测试用例
- 支持导出 Excel、XMind、Apifox、Postman 格式

### 📊 数据生成工具
- 批量生成姓名、手机号、邮箱、身份证号、地址
- 生成 IP 地址、URL、日期
- 支持自定义数量

### 🎭 Mock 数据生成
- 根据接口文档自动生成 Mock 响应
- 提供常用 Mock 数据模板（用户、登录、商品、订单等）

### 🔍 日志智能分析
- 拖拽上传日志文件
- 智能识别错误类型
- 支持导出分析结果到 Excel

### 🎨 格式化工具
- JSON 格式化/压缩/验证
- XML 格式化
- SQL 语句格式化

### 🔄 转换工具
- 时间戳转换
- JWT Token 解码
- 颜色格式转换

### 🧪 测试工具
- 正则表达式测试
- UUID 生成
- 哈希生成（MD5、SHA1、SHA256、SHA512）

### 📱 APK 文件解析
- 解析 APK 基本信息（包名、版本、SDK 版本等）
- 解析权限列表

## 技术栈

- **后端**: Python 3.x + Flask
- **前端**: HTML5 + JavaScript + CSS3
- **文档解析**: python-docx, PyPDF2, markdown
- **Excel 导出**: openpyxl
- **接口格式**: RESTful API

## 快速开始

### 环境要求
- Python 3.8+
- 支持 Windows / macOS / Linux

### 安装依赖

```bash
cd testcase_generator
pip install -r requirements.txt
```

### 启动服务

```bash
python run.py
```

启动后访问: `http://127.0.0.1:5000`

## 项目结构

```
testcase_generator/
├── app/
│   ├── modules/
│   │   ├── document_parser/   # 文档解析模块
│   │   ├── testcase_generator/  # 测试用例生成模块
│   │   ├── exporters/         # 导出器模块
│   │   ├── data_generator/    # 数据生成模块
│   │   ├── mock_generator/    # Mock 数据模块
│   │   └── web/               # Web 路由模块
│   ├── uploads/               # 上传文件目录
│   ├── outputs/               # 导出文件目录
│   └── __init__.py
├── templates/                 # 前端模板
│   └── index.html
├── requirements.txt           # 依赖文件
└── run.py                     # 启动文件
```

## 使用说明

1. **测试用例生成**
   - 上传需求文档或接口文档
   - 系统自动解析并生成测试用例
   - 导出为需要的格式

2. **数据生成**
   - 选择需要生成的数据类型
   - 设置生成数量
   - 点击生成按钮

3. **日志分析**
   - 拖拽上传日志文件
   - 查看分析结果
   - 可导出 Excel

4. **APK 解析**
   - 拖拽上传 APK 文件
   - 查看包信息和权限列表

## License

MIT License
