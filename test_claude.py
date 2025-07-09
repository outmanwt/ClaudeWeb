#!/usr/bin/env python3

import asyncio
import os
from ai_generator import ai_generator

async def test_claude_code():
    print("🧪 测试Claude Code集成...")
    
    # 检查环境变量
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  未设置ANTHROPIC_API_KEY环境变量")
        print("💡 系统将使用高质量模板作为后备")
    else:
        print("✅ 发现API密钥")
    
    print("\n🚀 开始生成测试...")
    
    try:
        result = await ai_generator.generate_webpage(
            "测试项目", 
            "制作一个简单的Hello World页面"
        )
        
        print(f"✅ 生成成功!")
        print(f"📝 生成方式: {result['generated_with']}")
        print(f"📄 内容长度: {len(result['content'])} 字符")
        
        # 预览内容前100字符
        preview = result['content'][:100].replace('\n', ' ')
        print(f"📋 内容预览: {preview}...")
        
    except Exception as e:
        print(f"❌ 生成失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_claude_code())