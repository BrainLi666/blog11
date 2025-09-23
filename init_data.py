from app import app, db, User, Post, Comment
from werkzeug.security import generate_password_hash
from datetime import datetime
import random

# 创建应用上下文
with app.app_context():
    # 确保数据库已创建
    db.create_all()
    
    # 检查是否已有管理员用户
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        # 创建管理员用户
        admin = User(username='admin', password=generate_password_hash('admin123'))
        db.session.add(admin)
        db.session.commit()
        print("管理员用户已创建：用户名=admin，密码=admin123")
    else:
        print("管理员用户已存在")
    
    # 检查是否已有示例文章
    if not Post.query.first():
        # 示例文章数据
        sample_posts = [
            {
                "title": "Flask入门教程：创建你的第一个Web应用",
                "content": "<h2>什么是Flask？</h2><p>Flask是一个轻量级的Python Web框架，它被称为'微框架'，因为它不依赖特定的工具或库。Flask提供了构建Web应用所需的基本功能，但保持了足够的灵活性，让开发者可以根据自己的需求选择合适的扩展。</p><h2>为什么选择Flask？</h2><ul><li><strong>轻量级</strong>：Flask的核心非常小，只包含最基本的功能</li><li><strong>灵活</strong>：你可以选择自己喜欢的数据库、模板引擎等</li><li><strong>易于学习</strong>：对于初学者来说，Flask比其他框架更容易上手</li><li><strong>活跃的社区</strong>：有大量的文档和社区支持</li></ul><h2>开始使用Flask</h2><p>首先，你需要安装Flask：</p><pre><code>pip install flask</code></pre><p>然后，创建一个简单的应用：</p><pre><code>from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'</code></pre>
                ",
                "category": "技术",
                "tags": "Python, Flask, Web开发"
            },
            {
                "title": "Tailwind CSS：实用的原子化CSS框架",
                "content": "<h2>什么是Tailwind CSS？</h2><p>Tailwind CSS是一个功能类优先的CSS框架，它提供了一套完整的构建块，让你可以在不离开HTML的情况下快速构建现代网站。与传统的CSS框架不同，Tailwind不提供预定义的组件，而是提供了低层次的实用工具类，让你可以完全控制元素的外观。</p><h2>Tailwind CSS的特点</h2><ul><li><strong>原子化设计</strong>：每个类都有一个特定的功能</li><li><strong>无命名负担</strong>：不需要为每个元素创建自定义类名</li><li><strong>响应式设计</strong>：内置响应式工具，轻松实现多设备适配</li><li><strong>可定制性强</strong>：可以通过配置文件自定义颜色、字体等</li></ul><h2>为什么选择Tailwind CSS？</h2><p>使用Tailwind CSS可以显著提高前端开发效率，减少CSS文件的体积，同时保持设计的一致性。特别是对于原型设计和快速迭代的项目，Tailwind CSS可以让你在不编写任何自定义CSS的情况下，快速构建出美观的界面。</p>
                ",
                "category": "前端",
                "tags": "CSS, Tailwind, 前端开发"
            },
            {
                "title": "个人博客的意义与价值",
                "content": "<h2>为什么要写博客？</h2><p>在当今这个信息爆炸的时代，写博客似乎已经不是什么新鲜事了。但即使如此，个人博客仍然具有不可替代的价值。无论是记录生活点滴，分享专业知识，还是表达个人观点，博客都是一个很好的平台。</p><h2>博客的价值</h2><ul><li><strong>知识管理</strong>：写作是最好的学习方式，通过写博客可以整理和巩固自己的知识</li><li><strong>个人品牌</strong>：持续输出高质量内容可以建立个人品牌，提升影响力</li><li><strong>交流与反馈</strong>：博客可以促进与读者的交流，获取有价值的反馈</li><li><strong>记录成长</strong>：博客是记录个人成长和变化的最好方式</li></ul><h2>如何开始写博客？</h2><p>开始写博客其实很简单，只需要选择一个平台，确定一个主题，然后开始写作。重要的是坚持，定期更新内容，不断提高写作质量。记住，写博客的首要目的是为了自己，而不是为了取悦他人。</p>
                ",
                "category": "生活",
                "tags": "博客, 成长, 分享"
            }
        ]
        
        # 生成文章的slug
        from slugify import slugify
        
        # 添加示例文章
        for i, post_data in enumerate(sample_posts):
            slug = slugify(post_data['title'])
            # 检查slug是否已存在
            if Post.query.filter_by(slug=slug).first():
                slug = f"{slug}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            post = Post(
                title=post_data['title'],
                content=post_data['content'],
                author_id=admin.id,
                slug=slug,
                category=post_data['category'],
                tags=post_data['tags']
            )
            db.session.add(post)
            db.session.commit()
            
            # 为每篇文章添加一些评论
            sample_comments = [
                {"author": "读者1", "content": "非常感谢分享，学到了很多！"},
                {"author": "读者2", "content": "写得很棒，期待更多内容！"},
                {"author": "读者3", "content": "这个主题很有意思，希望能深入探讨一下。"}
            ]
            
            # 随机添加1-3条评论
            num_comments = random.randint(1, 3)
            for comment_data in sample_comments[:num_comments]:
                comment = Comment(
                    content=comment_data['content'],
                    author=comment_data['author'],
                    post_id=post.id
                )
                db.session.add(comment)
                db.session.commit()
            
        print(f"已添加{len(sample_posts)}篇示例文章和相关评论")
    else:
        print("示例文章已存在")

print("数据初始化完成！")