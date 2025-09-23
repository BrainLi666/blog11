from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Length, EqualTo
from datetime import datetime
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db = SQLAlchemy(app)

# 初始化登录管理器
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 数据库模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('posts', lazy=True))
    slug = db.Column(db.String(200), unique=True, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    tags = db.Column(db.String(200), nullable=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))
    author = db.Column(db.String(100), nullable=False)

# 表单定义
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    category = StringField('Category', validators=[Length(max=100)])
    tags = StringField('Tags (comma separated)')
    submit = SubmitField('Save')

class CommentForm(FlaskForm):
    author = StringField('Your Name', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Comment', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Submit Comment')

# 登录管理器回调
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 创建数据库表
with app.app_context():
    db.create_all()
    # 创建默认管理员用户（首次运行时）
    if not User.query.filter_by(username='admin').first():
        from werkzeug.security import generate_password_hash
        admin_user = User(username='admin', password=generate_password_hash('admin123'))
        db.session.add(admin_user)
        db.session.commit()

# 路由定义
@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    # 获取所有分类（去重并排除空分类）
    categories = db.session.query(Post.category).filter(Post.category.isnot(None)).distinct().all()
    categories = [category[0] for category in categories]
    return render_template('index.html', posts=posts, categories=categories)

@app.route('/post/<slug>')
def post_detail(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, author=form.author.data, post_id=post.id)
        db.session.add(comment)
        db.session.commit()
        flash('Comment added successfully!', 'success')
        return redirect(url_for('post_detail', slug=slug))
    
    # 获取相关文章（基于相同分类）
    related_posts = []
    if post.category:
        related_posts = Post.query.filter(
            Post.category == post.category, 
            Post.id != post.id
        ).order_by(Post.created_at.desc()).limit(3).all()
    
    return render_template('post_detail.html', post=post, form=form, related_posts=related_posts)

@app.route('/category/<category>')
def category_posts(category):
    posts = Post.query.filter_by(category=category).order_by(Post.created_at.desc()).all()
    # 获取所有分类（去重并排除空分类）
    all_categories = db.session.query(Post.category).filter(Post.category.isnot(None)).distinct().all()
    all_categories = [cat[0] for cat in all_categories]
    return render_template('category.html', posts=posts, category=category, categories=all_categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        from werkzeug.security import check_password_hash
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('admin/login.html', form=form)

@app.route('/admin/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('admin/dashboard.html', posts=posts)

@app.route('/admin/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        # 生成slug
        from slugify import slugify
        slug = slugify(form.title.data)
        # 检查slug是否已存在
        if Post.query.filter_by(slug=slug).first():
            slug = f"{slug}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        post = Post(
            title=form.title.data,
            content=form.content.data,
            author_id=current_user.id,
            slug=slug,
            category=form.category.data or None,
            tags=form.tags.data or None
        )
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/edit_post.html', form=form, title='New Post')

@app.route('/admin/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author_id != current_user.id:
        flash('You are not authorized to edit this post', 'danger')
        return redirect(url_for('admin_dashboard'))
    form = PostForm(obj=post)
    if form.validate_on_submit():
        form.populate_obj(post)
        post.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/edit_post.html', form=form, title='Edit Post', post=post)

@app.route('/admin/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author_id != current_user.id:
        flash('You are not authorized to delete this post', 'danger')
        return redirect(url_for('admin_dashboard'))
    # 删除相关评论
    Comment.query.filter_by(post_id=post_id).delete()
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)