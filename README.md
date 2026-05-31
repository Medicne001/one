# 📝 Todo 应用

一个现代化的待办事项管理应用，使用 Flask + SQLite 构建，支持本地存储、优先级管理和任务筛选。

## ✨ 功能特性

- ✅ **任务管理**：创建、编辑、删除任务
- ✅ **任务完成状态**：标记任务为已完成或待处理
- ✅ **优先级设置**：支持低、中、高三个优先级
- ✅ **任务描述**：为每个任务添加详细描述
- ✅ **任务筛选**：按完成状态筛选任务
- ✅ **任务排序**：按创建时间或优先级排序
- ✅ **实时统计**：显示总任务数、已完成数、待处理数
- ✅ **本地存储**：使用 SQLite 数据库本地存储
- ✅ **现代 UI**：响应式设计，支持深色/浅色主题
- ✅ **REST API**：完整的 API 接口支持

## 🚀 快速开始

### 前置要求

- Python 3.8 或更高版本
- pip（Python 包管理器）

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/Medicne001/one.git
cd one
```

2. **创建虚拟环境**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **运行应用**
```bash
python app.py
```

5. **访问应用**
在浏览器中打开：`http://localhost:5000`

## 📁 项目结构

```
one/
├── app.py                 # Flask 应用主文件（数据模型 + 路由）
├── config.py              # 配置文件
├── requirements.txt       # Python 依赖
├── README.md              # 项目文档
├── templates/
│   ├── base.html          # 基础模板
│   └── index.html         # 主页面
├── static/
│   ├── css/
│   │   └── style.css      # 样式表
│   └── js/
│       └── script.js      # 前端逻辑
└── .gitignore             # Git 忽略配置
```

## 🔌 API 文档

### 获取所有任务
```http
GET /api/todos
```

**响应示例：**
```json
[
  {
    "id": 1,
    "title": "完成项目报告",
    "description": "完成Q1季度项目报告",
    "completed": false,
    "created_at": "2024-01-15 10:30:00",
    "updated_at": "2024-01-15 10:30:00",
    "priority": "high"
  }
]
```

### 创建任务
```http
POST /api/todos
Content-Type: application/json

{
  "title": "新任务",
  "description": "任务描述（可选）",
  "priority": "medium"
}
```

### 获取单个任务
```http
GET /api/todos/{id}
```

### 更新任务
```http
PUT /api/todos/{id}
Content-Type: application/json

{
  "title": "更新后的标题",
  "description": "更新后的描述",
  "completed": true,
  "priority": "high"
}
```

### 删除任务
```http
DELETE /api/todos/{id}
```

### 切换任务完成状态
```http
PUT /api/todos/{id}/toggle
```

### 获取统计信息
```http
GET /api/stats
```

**响应示例：**
```json
{
  "total": 10,
  "completed": 7,
  "pending": 3
}
```

## 🎨 UI 特性

- **响应式设计**：完美适配桌面、平板和手机设备
- **现代 UI**：使用渐变背景和卡片设计
- **动画效果**：流畅的过渡和淡入淡出效果
- **优先级色标**：用不同颜色区分优先级
- **实时反馈**：操作后立即显示结果

## 🛠️ 技术栈

### 后端
- **Flask**：轻量级 Web 框架
- **Flask-SQLAlchemy**：ORM 框架
- **SQLite**：本地数据库

### 前端
- **HTML5**：页面结构
- **CSS3**：样式和动画
- **JavaScript (ES6+)**：交互逻辑
- **Fetch API**：与后端通信

## 📝 数据模型

### Todo 模型
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键，自增长 |
| title | String(200) | 任务标题，必填 |
| description | Text | 任务描述 |
| completed | Boolean | 完成状态，默认为 False |
| priority | String(10) | 优先级：low/medium/high |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 最后更新时间 |

## 🔒 安全特性

- ✅ 输入验证
- ✅ HTML 转义（防止 XSS）
- ✅ 错误处理
- ✅ CORS 支持（可选）

## 🚀 部署建议

### 生产环境

1. **使用生产级 WSGI 服务器**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

2. **使用数据库**
对于多用户场景，考虑迁移到 PostgreSQL：
```bash
pip install psycopg2-binary
# 修改 config.py 中的 DATABASE_URI
```

3. **启用 HTTPS**
使用 nginx 反向代理或 Let's Encrypt

4. **环境变量**
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secure-key
```

## 📦 依赖版本

- Flask 2.3.0
- Flask-SQLAlchemy 3.0.0
- Werkzeug 2.3.0
- Python 3.8+

## 📖 学习资源

- [Flask 官方文档](https://flask.palletsprojects.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [MDN Web Docs](https://developer.mozilla.org/)

## 📄 许可证

本项目采用 MIT 许可证。

## 🤝 贡献

欢迎提交 Pull Request 和 Issue！

## 👨‍💻 作者

Created by Medicne001

## 🐛 报告问题

如遇到问题，请在 Issues 中提交。

---

**⭐ 如果觉得有帮助，请给个 Star！**
