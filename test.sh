#!/bin/bash

echo "🧪 开始测试 AI 项目管理系统..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先创建虚拟环境"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖
echo "📦 检查依赖..."
pip list | grep -E "(fastapi|uvicorn|aiosqlite|websockets)" > /dev/null
if [ $? -ne 0 ]; then
    echo "❌ 缺少必要依赖，请运行: pip install -r requirements.txt"
    exit 1
fi

# 清理旧数据
echo "🧹 清理测试数据..."
rm -f projects.db
rm -rf projects/

# 启动服务器（后台运行）
echo "🚀 启动服务器..."
python main.py &
SERVER_PID=$!

# 等待服务器启动
sleep 5

# 检查服务器是否启动成功
curl -s http://localhost:3000/ > /dev/null
if [ $? -ne 0 ]; then
    echo "❌ 服务器启动失败"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

echo "✅ 服务器启动成功"

# 测试API端点
echo "🔍 测试API端点..."

# 测试1: 创建项目
echo "测试1: 创建项目"
response=$(curl -s -X POST http://localhost:3000/api/projects \
    -H "Content-Type: application/json" \
    -d '{"name":"测试项目","keyword":"计算器"}')

if echo "$response" | grep -q '"id"'; then
    echo "✅ 项目创建成功"
    project_id=$(echo "$response" | grep -o '"id":[0-9]*' | cut -d':' -f2)
    echo "项目ID: $project_id"
else
    echo "❌ 项目创建失败: $response"
fi

# 测试2: 获取项目列表
echo "测试2: 获取项目列表"
response=$(curl -s http://localhost:3000/api/projects)
if echo "$response" | grep -q "测试项目"; then
    echo "✅ 项目列表获取成功"
else
    echo "❌ 项目列表获取失败: $response"
fi

# 测试3: 生成页面
echo "测试3: 生成页面"
if [ ! -z "$project_id" ]; then
    response=$(curl -s -X POST http://localhost:3000/api/projects/$project_id/pages \
        -H "Content-Type: application/json" \
        -d '{"prompt":"制作一个简单的计算器"}')
    
    if echo "$response" | grep -q '"generated_with"'; then
        echo "✅ 页面生成成功"
        generated_with=$(echo "$response" | grep -o '"generated_with":"[^"]*"' | cut -d':' -f2 | tr -d '"')
        echo "生成方式: $generated_with"
    else
        echo "❌ 页面生成失败: $response"
    fi
fi

# 测试4: 访问页面
echo "测试4: 访问生成的页面"
response=$(curl -s http://localhost:3000/page/index)
if echo "$response" | grep -q "<!DOCTYPE html>"; then
    echo "✅ 页面访问成功"
else
    echo "❌ 页面访问失败"
fi

# 测试5: WebSocket连接（简单测试）
echo "测试5: WebSocket连接测试"
# 这里可以添加更复杂的WebSocket测试，目前跳过
echo "⏭️ WebSocket测试跳过（需要专门的WebSocket客户端）"

# 清理
echo "🧹 清理测试环境..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null

echo "🎉 测试完成！"