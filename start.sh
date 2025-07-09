#!/bin/bash

echo "🚀 启动 AI 项目管理系统..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "检查并安装依赖..."
pip install -r requirements.txt

# 确保项目目录存在
mkdir -p projects

# 启动服务器
echo ""
echo "🎉 系统配置完成！"
echo ""
echo "📋 系统功能："
echo "  🤖 AI智能网页生成 (Claude Code)"
echo "  🎨 高质量模板后备系统"
echo "  📦 Git版本控制"
echo "  🔄 实时进度反馈"
echo "  📝 项目管理"
echo ""
echo "🌐 访问地址: http://localhost:3000"
echo "💾 数据存储: ./projects/ 目录"
echo "🔧 API文档: http://localhost:3000/docs"
echo ""
echo "💡 使用提示："
echo "  - 创建项目时填写关键字（如：刷题、计算器、hello）"
echo "  - 系统会根据关键字选择合适的模板"
echo "  - 生成过程会实时显示进度"
echo "  - 每次生成都会自动创建Git提交"
echo ""
echo "🛑 按 Ctrl+C 停止服务器"
echo "================================"
echo ""

python main.py