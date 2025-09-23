# 轻量级个人博客系统

一个基于Flask的轻量级个人博客系统，支持用户端和管理端分离，具有精美的界面设计。

## 特性

- **用户端**：文章列表、文章详情、分类浏览、评论功能
- **管理端**：文章管理（创建、编辑、删除）、评论管理、统计数据查看
- **精美的界面设计**：使用Tailwind CSS和Font Awesome构建响应式设计
- **轻量级架构**：适合2核2G内存、3M带宽的服务器部署
- **安全认证**：基于Flask-Login的用户认证系统
- **数据存储**：使用SQLite数据库，无需额外配置

## 技术栈

- **后端**：Python 3.8+, Flask 3.0
- **数据库**：SQLite
- **前端**：HTML, Tailwind CSS v3, JavaScript
- **富文本编辑器**：TinyMCE

## 安装指南

### 1. 克隆项目

```bash
# 进入博客目录
cd /Users/liyunpeng/Desktop/Python/blog

# 初始化git（如果需要）
git init
```

### 2. 创建虚拟环境

```bash
# 在macOS/Linux上
python3 -m venv venv

# 在Windows上
python -m venv venv
```

### 3. 激活虚拟环境

```bash
# 在macOS/Linux上
source venv/bin/activate

# 在Windows上
venv\Scripts\activate
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 配置环境变量

编辑`.env`文件，设置您的密钥：

```
SECRET_KEY=your-secret-key-here
```

建议使用随机生成的密钥，可以通过以下命令生成：

```bash
python -c "import secrets; print(secrets.token_hex(16))"
```

### 6. 初始化数据库

运行应用程序时，会自动创建数据库表和默认管理员用户：

```bash
flask run
```

默认管理员账号：
- 用户名：admin
- 密码：admin123（建议登录后立即修改）

## 使用说明

### 启动开发服务器

```bash
flask run
```

访问 `http://127.0.0.1:5000` 查看博客前台，访问 `http://127.0.0.1:5000/login` 进入管理后台。

### 生产环境部署

对于生产环境，建议使用Gunicorn作为WSGI服务器，并配置Nginx作为反向代理：

```bash
# 安装Gunicorn
pip install gunicorn

# 使用Gunicorn运行应用
gunicorn -w 2 -b 0.0.0.0:8000 app:app
```

### 功能使用

1. **创建文章**：登录管理后台，点击"新建文章"按钮
2. **编辑文章**：在文章列表中点击"编辑"按钮
3. **删除文章**：在文章列表中点击"删除"按钮
4. **添加分类和标签**：在创建/编辑文章时填写分类和标签信息
5. **查看评论**：在文章详情页可以查看和添加评论

## 项目结构

```
blog/
├── app.py               # 主应用文件
├── requirements.txt     # 项目依赖
├── .env                 # 环境变量配置
├── .gitignore           # Git忽略规则
├── README.md            # 项目说明文档
└── templates/           # 模板文件
    ├── base.html        # 基础模板
    ├── index.html       # 首页
    ├── post_detail.html # 文章详情页
    ├── category.html    # 分类页
    └── admin/           # 管理端模板
        ├── base.html    # 管理端基础模板
        ├── login.html   # 登录页面
        ├── dashboard.html # 仪表盘
        └── edit_post.html # 编辑文章页面
```

## 注意事项

- 首次运行时会自动创建默认管理员用户，请务必修改默认密码
- 生产环境中请确保设置强密钥和关闭调试模式
- 定期备份数据库文件（默认为`blog.db`）

## License

MIT