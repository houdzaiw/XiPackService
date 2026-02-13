#!/bin/bash

# XiPackService 启动脚本

echo "🚀 启动 XiPackService..."
echo "📍 工作目录: $(pwd)"
echo ""

# 检查依赖是否已安装
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  依赖未安装，正在安装..."
    pip3 install -r requirements.txt
fi

# 启动服务器
echo "✅ 启动服务器..."
echo "📝 API 地址: http://127.0.0.1:8000"
echo "🛒 付费页面: http://127.0.0.1:8000/static/purchase.html"
echo "📖 API 文档: http://127.0.0.1:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

# 使用 python3 -m uvicorn 启动
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
