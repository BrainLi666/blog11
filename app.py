from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Length, EqualTo
from datetime import datetime
import os
from dotenv import load_dotenv
import functools

# 加载环境变量
load_dotenv()

# 初始化Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 2678400  # 31天

# 初始化数据库
db = SQLAlchemy(app)

# 初始化登录管理器
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 添加模板上下文处理器，使now()函数在模板中可用
@app.context_processor
def utility_processor():
    def now():
        return datetime.now()
    return dict(now=now)

# 数据库模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

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

class PageView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(100), nullable=False)
    user_agent = db.Column(db.String(500), nullable=True)
    url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(200), nullable=True)

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

# 访问统计中间件
def track_page_view(app):
    @app.before_request
    def before_request():
        # 忽略静态文件和管理后台的请求
        if request.path.startswith('/static/') or request.path.startswith('/admin/') or request.path == '/login':
            return
        
        # 生成或获取会话ID
        if 'session_id' not in session:
            from uuid import uuid4
            session['session_id'] = str(uuid4())
            session.permanent = True
        
        # 创建页面访问记录
        with app.app_context():
            page_view = PageView(
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string[:500],  # 限制长度
                url=request.path,
                session_id=session['session_id']
            )
            db.session.add(page_view)
            db.session.commit()

# 登录管理器回调
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 创建admin_required装饰器
def admin_required(func):
    @login_required
    @functools.wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin:
            flash('You need to be an administrator to access this page', 'danger')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return decorated_view

# 创建数据库表和默认管理员用户
with app.app_context():
    db.create_all()
    
    # 创建默认管理员用户（首次运行时）
    if not User.query.filter_by(username='admin').first():
        from werkzeug.security import generate_password_hash
        admin_user = User(username='admin', password=generate_password_hash('admin123'), is_admin=True)
        db.session.add(admin_user)
        db.session.commit()
    else:
        # 确保现有admin用户有管理员权限
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user.is_admin:
            admin_user.is_admin = True
            db.session.commit()

# 启用访问统计
if app.config.get('TRACK_PAGE_VIEWS', True):
    track_page_view(app)

# 路由定义
# 前台路由（带后缀）
@app.route('/blog/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    # 获取所有分类（去重并排除空分类）
    categories = db.session.query(Post.category).filter(Post.category.isnot(None)).distinct().all()
    categories = [category[0] for category in categories]
    return render_template('index.html', posts=posts, categories=categories)

@app.route('/blog/post/<slug>')
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

@app.route('/blog/category/<category>')
def category_posts(category):
    posts = Post.query.filter_by(category=category).order_by(Post.created_at.desc()).all()
    # 获取所有分类（去重并排除空分类）
    all_categories = db.session.query(Post.category).filter(Post.category.isnot(None)).distinct().all()
    all_categories = [cat[0] for cat in all_categories]
    return render_template('category.html', posts=posts, category=category, categories=all_categories)

# 首页重定向到前台路由
@app.route('/')
def home():
    return redirect(url_for('index'))

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
@admin_required
def admin_dashboard():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    # 获取统计数据
    total_posts = Post.query.count()
    
    # 计算本月发布的文章数量
    from datetime import datetime
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year
    posts_this_month = Post.query.filter(
        db.extract('month', Post.created_at) == current_month,
        db.extract('year', Post.created_at) == current_year
    ).count()
    
    total_comments = Comment.query.count()
    total_categories = db.session.query(Post.category).filter(Post.category.isnot(None)).distinct().count()
    
    # 获取PV和UV统计数据
    total_pv = PageView.query.count()
    total_uv = db.session.query(PageView.session_id).distinct().count()
    
    # 获取最近7天的PV和UV数据
    from datetime import datetime, timedelta
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    # 准备日期列表
    date_list = []
    pv_data = []
    uv_data = []
    
    for i in range(7):
        current_date = seven_days_ago + timedelta(days=i)
        date_str = current_date.strftime('%Y-%m-%d')
        date_list.append(date_str)
        
        # 获取当天的PV
        start_date = datetime.strptime(date_str, '%Y-%m-%d')
        end_date = start_date + timedelta(days=1)
        
        day_pv = PageView.query.filter(
            PageView.created_at >= start_date,
            PageView.created_at < end_date
        ).count()
        pv_data.append(day_pv)
        
        # 获取当天的UV
        day_uv = db.session.query(PageView.session_id).filter(
            PageView.created_at >= start_date,
            PageView.created_at < end_date
        ).distinct().count()
        uv_data.append(day_uv)
    
    return render_template('admin/dashboard.html', 
                          posts=posts, 
                          total_posts=total_posts,
                          posts_this_month=posts_this_month,
                          total_comments=total_comments, 
                          total_categories=total_categories,
                          total_pv=total_pv,
                          total_uv=total_uv,
                          date_list=date_list,
                          pv_data=pv_data,
                          uv_data=uv_data)

@app.route('/admin/post/new', methods=['GET', 'POST'])
@admin_required
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
@admin_required
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
@admin_required
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