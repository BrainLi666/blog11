from app import app, db

with app.app_context():
    # 使用纯SQL来检查和添加字段，避免使用SQLAlchemy模型
    conn = db.engine.connect()
    trans = conn.begin()
    
    try:
        # 检查is_admin字段是否存在
        has_is_admin = False
        try:
            # 查询表结构
            result = conn.execute("PRAGMA table_info('user')")
            columns = [row[1] for row in result]
            has_is_admin = 'is_admin' in columns
            print(f"is_admin字段存在状态: {has_is_admin}")
        except Exception as e:
            print(f"检查字段失败: {e}")
        
        # 如果字段不存在，则添加
        if not has_is_admin:
            try:
                # 添加is_admin字段
                conn.execute('ALTER TABLE "user" ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE')
                trans.commit()
                print("成功添加is_admin字段")
                
                # 开始新的事务
                trans = conn.begin()
                # 设置admin用户为管理员
                conn.execute('UPDATE "user" SET is_admin = TRUE WHERE username = ?', ('admin',))
                trans.commit()
                print("已将admin用户设置为管理员")
            except Exception as e:
                trans.rollback()
                print(f"添加字段或更新管理员失败: {e}")
        else:
            # 字段已存在，确保admin用户是管理员
            try:
                trans = conn.begin()
                conn.execute('UPDATE "user" SET is_admin = TRUE WHERE username = ?', ('admin',))
                trans.commit()
                print("确保admin用户是管理员")
            except Exception as e:
                trans.rollback()
                print(f"更新管理员状态失败: {e}")
        
        print("数据库迁移完成")
    finally:
        conn.close()