"""
数据库初始化脚本
运行此脚本初始化数据库并导入基础数据
"""
import sys
import os

# 添加app目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.base import SessionLocal, Base, engine
from app.utils.init_data import initialize_database


def main():
    """主函数"""
    # 创建所有表
    print("创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✓ 数据库表创建完成\n")

    # 获取数据库会话
    db = SessionLocal()
    try:
        # 初始化数据
        initialize_database(db)
    except Exception as e:
        print(f"\n✗ 初始化失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
