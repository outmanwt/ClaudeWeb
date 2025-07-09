import asyncio
import subprocess
import os
import tempfile
from typing import Optional, Dict, Any
from templates import template_generator

class AIGenerator:
    def __init__(self):
        self.timeout = 300  # 5分钟超时
    
    async def generate_webpage(self, project_name: str, user_prompt: str, project_id: str = None) -> Dict[str, Any]:
        """
        生成网页内容，优先使用Claude Code，失败时使用模板
        """
        try:
            print("Start")
            # 优先尝试Claude Code
            content = await self._try_claude_code_generation(project_name, user_prompt, project_id)
            return {
                "content": content,
                "generated_with": "claude-code",
                "success": True
            }
        except Exception as claude_error:
            print(f"Claude Code generation failed: {claude_error}")
            
            # 后备到高质量模板
            try:
                content = template_generator.generate_template(project_name, user_prompt)
                return {
                    "content": content,
                    "generated_with": "quality-template",
                    "success": True,
                    "fallback_reason": str(claude_error)
                }
            except Exception as template_error:
                print(f"Template generation failed: {template_error}")
                
                # 最后的后备方案
                content = self._generate_simple_fallback(project_name, user_prompt)
                return {
                    "content": content,
                    "generated_with": "simple-fallback",
                    "success": True,
                    "fallback_reason": f"Claude: {claude_error}, Template: {template_error}"
                }
    
    async def _try_claude_code_generation(self, project_name: str, user_prompt: str, project_id: str = None) -> str:
        """
        尝试使用Claude Code生成内容
        """
        # 构建增强提示词
        enhanced_prompt = self._build_enhanced_prompt(project_name, user_prompt)
        from claude_code_sdk import (
            ClaudeSDKError,      # Base error
            CLINotFoundError,    # Claude Code not installed
            CLIConnectionError,  # Connection issues
            ProcessError,        # Process failed
            CLIJSONDecodeError,  # JSON parsing issues
        )
        # 方法2: 尝试使用claude-code Python包 (如果已安装)
        try:
            return await self._call_claude_python_sdk(enhanced_prompt, project_id)
        except CLINotFoundError:
            print("Please install Claude Code")
        except ProcessError as e:
            print(f"Process failed with exit code: {e.exit_code}")
        except CLIJSONDecodeError as e:
            print(f"Failed to parse response: {e}")
        except Exception as e:
            print(f"Claude Python SDK failed: {e}")
            raise Exception("All Claude Code methods failed")
            

    
    async def _call_claude_cli(self, prompt: str, project_id: str = None) -> str:
        """
        通过CLI调用Claude Code
        """        
        try:
            # 构建命令 - 直接传递提示词到stdin
            cmd = ['claude', '--allowedTools=[\"Bash\", \"Edit\", \"Read\", \"Write\", \"LS\"]']
            
            # 如果有WebSocket连接，添加进度推送
            if project_id:
                from main import manager
                await manager.broadcast_progress(project_id, "🤖 调用Claude Code CLI...", "progress")
            
            # 执行命令，通过stdin传递提示词
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=prompt.encode('utf-8')),
                timeout=self.timeout
            )
            
            if process.returncode == 0:
                result = stdout.decode('utf-8').strip()
                if result and len(result) > 100:  # 基本的内容验证
                    return result
                else:
                    raise Exception("Claude CLI returned empty or invalid content")
            else:
                error_msg = stderr.decode('utf-8')
                raise Exception(f"Claude CLI failed with code {process.returncode}: {error_msg}")
                
        except asyncio.TimeoutError:
            raise Exception("Claude CLI timeout (5 minutes)")
        except FileNotFoundError:
            raise Exception("Claude CLI not found. Please install claude-code CLI.")
    
    async def _call_claude_python_sdk(self, prompt: str, project_id: str = None) -> str:
        """
        通过Python SDK调用Claude Code
        """
        try:
            # 尝试导入claude-code SDK
            try:
                from claude_code_sdk import query, ClaudeCodeOptions, AssistantMessage, TextBlock
            except ImportError:
                raise Exception("claude-code-sdk not installed. Run: pip install claude-code-sdk")
            
            if project_id:
                from main import manager
                await manager.broadcast_progress(project_id, "🤖 调用Claude Code SDK...", "progress")
            
            full_response = ""
            options = ClaudeCodeOptions(
                allowed_tools=["Read", "Write", "Bash"],
                permission_mode='acceptEdits'  # auto-accept file edits
            )
            # 使用异步方式调用SDK
            async for message in query(prompt=prompt,options=options):
                if hasattr(message, 'content'):
                    if isinstance(message.content, list):
                        for content_block in message.content:
                            if hasattr(content_block, 'text'):
                                full_response += content_block.text
                    else:
                        full_response += str(message.content)
                    
                    # 实时推送进度
                    if project_id and len(full_response) % 500 == 0:  # 每500字符推送一次
                        from main import manager
                        await manager.broadcast_progress(
                            project_id, 
                            f"📝 已生成 {len(full_response)} 字符...", 
                            "progress"
                        )
            
            if full_response and len(full_response) > 100:
                return full_response
            else:
                raise Exception("Claude SDK returned empty or invalid content")
                
        except Exception as e:
            raise Exception(f"Claude SDK error: {str(e)}")
    
    def _build_enhanced_prompt(self, project_name: str, user_prompt: str) -> str:
        """
        构建增强的提示词
        """
        return f"""
重要约束：
- 只返回完整的HTML代码，从<!DOCTYPE html>开始到</html>结束。
- 不要输出除HTML代码之外的任何内容，不要有任何解释、说明、注释、提示或额外文本。
- 输出内容必须可以直接保存为html文件并运行。        
        
用户需求: {user_prompt}
项目名称: {project_name}

请生成一个完整的功能性网站，要求：

1. 技术要求:
   - 使用现代HTML5 + CSS3 + JavaScript
   - 响应式设计，适配移动端和桌面端
   - 所有功能完整可用，避免使用占位符
   - 代码内联，无外部依赖
   - 使用语义化HTML标签

2. 设计要求:
   - 美观的UI设计和用户体验
   - 现代化的视觉风格
   - 合适的颜色搭配和排版
   - 流畅的动画效果
   - 清晰的信息层次

3. 功能要求:
   - 根据用户的具体需求实现相应功能
   - 交互式元素和用户反馈
   - 本地存储支持（如适用）
   - 键盘和鼠标事件支持
   - 错误处理和用户提示

4. 代码质量:
   - 清晰的代码结构和注释
   - 良好的性能优化
   - 跨浏览器兼容性
   - 安全的代码实践

请生成完整的index.html文件，html文件包含所有必要的CSS样式和JavaScript功能。文件应该是自包含的，可以直接在浏览器中打开使用。

"""
    
    def _generate_simple_fallback(self, project_name: str, user_prompt: str) -> str:
        """
        简单的后备模板
        """
        from datetime import datetime
        
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            text-align: center;
            background: rgba(255,255,255,0.1);
            padding: 40px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }}
        h1 {{
            font-size: 3rem;
            margin-bottom: 20px;
        }}
        .prompt {{
            font-size: 1.5rem;
            background: rgba(255,255,255,0.2);
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .info {{
            margin-top: 30px;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>⚠️ {project_name}</h1>
        <div class="prompt">用户需求: {user_prompt}</div>
        <div class="info">
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>生成方式: 简单后备模板</p>
            <p>说明: AI生成和高质量模板均不可用，使用简单后备方案</p>
        </div>
    </div>
</body>
</html>"""

# 全局AI生成器实例
ai_generator = AIGenerator()