#!/bin/bash
# 后端启动脚本

echo "岗责驱动的周工作计划管理系统 - 后端服务"
echo "=========================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    exit 1
fi

# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ]; then
    echo "警告: 建议在虚拟环境中运行"
    echo "创建虚拟环境: python3 -m venv venv"
    echo "激活虚拟环境: source venv/bin/activate"
    echo ""
fi

# 检查依赖
if [ ! -f "requirements.txt" ]; then
    echo "错误: 未找到requirements.txt"
    exit 1
fi

echo "检查依赖包..."
pip install -r requirements.txt --quiet

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "警告: 未找到.env文件，使用.env.example"
    cp .env.example .env
    echo "请编辑.env文件并设置SECRET_KEY"
fi

# 初始化数据库（如果需要）
if [ "$1" == "init" ]; then
    echo "初始化数据库..."
    python3 init_db.py
    echo ""
fi

# 启动服务
echo "启动FastAPI服务..."
echo "API文档: http://localhost:8000/docs"
echo "=========================================="
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
