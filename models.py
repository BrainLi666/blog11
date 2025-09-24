from flask_login import UserMixin
from datetime import datetime

# 注意：db对象将在app.py中导入后使用

class User(UserMixin):
    __tablename__ = 'user'
    id = None
    username = None
    password = None
    created_at = None

class Post:
    __tablename__ = 'post'
    id = None
    title = None
    content = None
    created_at = None
    updated_at = None
    author_id = None
    author = None
    slug = None
    category = None
    tags = None

class Comment:
    __tablename__ = 'comment'
    id = None
    content = None
    created_at = None
    post_id = None
    post = None
    author = None