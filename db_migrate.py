import sqlite3
import os

# 直接连接SQLite数据库
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'blog.db')

# 检查数据库文件是否存在
if not os.path.exists(os.path.dirname(db_path)):
    os.makedirs(os.path.dirname(db_path))

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查user表是否存在
table_exists = False
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
    if cursor.fetchone():
        table_exists = True
    print(f"users表存在状态: {table_exists}")
except Exception as e:
    print(f"检查表存在失败: {e}")

if table_exists:
    # 检查is_admin字段是否存在
    has_is_admin = False
    try:
        cursor.execute("PRAGMA table_info('user')")
        columns = [row[1] for row in cursor.fetchall()]
        has_is_admin = 'is_admin' in columns
        print(f"is_admin字段存在状态: {has_is_admin}")
    except Exception as e:
        print(f"检查字段失败: {e}")
    
    # 如果字段不存在，则添加
    if not has_is_admin:
        try:
            # 添加is_admin字段
            cursor.execute('ALTER TABLE "user" ADD COLUMN is_admin INTEGER NOT NULL DEFAULT 0')
            conn.commit()
            print("成功添加is_admin字段")
            
            # 设置admin用户为管理员
            cursor.execute('UPDATE "user" SET is_admin = 1 WHERE username = ?', ('admin',))
            conn.commit()
            print("已将admin用户设置为管理员")
        except Exception as e:
            conn.rollback()
            print(f"添加字段或更新管理员失败: {e}")
    else:
        # 字段已存在，确保admin用户是管理员
        try:
            cursor.execute('UPDATE "user" SET is_admin = 1 WHERE username = ?', ('admin',))
            conn.commit()
            print("确保admin用户是管理员")
        except Exception as e:
            conn.rollback()
            print(f"更新管理员状态失败: {e}")
else:
    print("users表不存在，跳过迁移")

# 关闭连接
conn.close()
print("数据库迁移完成")