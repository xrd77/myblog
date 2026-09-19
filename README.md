# 乐安博客

一个用 Flask + MySQL 从零搭建的个人博客网站，支持文章发布、用户注册登录和作者权限管理。

## 功能

- 文章：发布、列表展示、详情查看、编辑、删除
- 首页只展示最新 3 篇文章，全部文章在「文章」页
- 用户系统：注册（密码哈希存储）、登录（session 保持登录状态）、退出
- 权限控制：未登录不能发文；只有作者本人能编辑/删除自己的文章
- 数据存储：MySQL 8.0，文章通过 author_id 关联到用户
- 界面：手写 CSS 的青春校园风格，响应式布局，含网站图标

## 技术栈

- Python 3.12
- Flask（路由、模板渲染、session）
- PyMySQL（MySQL 驱动 + DictCursor）
- MySQL 8.0
- Jinja2 模板引擎
- HTML + CSS（手写，无前端框架）

## 项目结构

```
myblog/
├── app.py                 # 后端：路由 + 数据库操作 + 权限校验
├── requirements.txt       # 依赖清单
├── templates/             # 页面模板（首页/文章/详情/写文章/编辑/登录/注册/关于）
└── static/                # 样式与图标（style.css、favicon.svg）
```

## 本地运行

1. 在 MySQL 中建库建账号：

```sql
CREATE DATABASE blog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'bloguser'@'localhost' IDENTIFIED BY '你的密码';
GRANT ALL PRIVILEGES ON blog.* TO 'bloguser'@'localhost';
FLUSH PRIVILEGES;
```

2. 建表：

```sql
CREATE TABLE posts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  content TEXT NOT NULL,
  date DATE NOT NULL,
  author_id INT NULL
) DEFAULT CHARSET=utf8mb4;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at DATE NOT NULL
) DEFAULT CHARSET=utf8mb4;
```

3. 安装依赖并启动：

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python app.py
```

4. 浏览器打开 http://127.0.0.1:5000

## 后续计划

- [ ] 评论功能
- [ ] 文章分页与搜索
- [ ] 修改密码、个人主页
- [ ] 部署上线（Gunicorn + Nginx）