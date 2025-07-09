from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from contextlib import asynccontextmanager
import aiosqlite
import os
import asyncio
import json
import uuid
from datetime import datetime
from typing import Optional, List
import subprocess
import shutil
from templates import template_generator
from ai_generator import ai_generator
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    await init_database()
    yield
    # 关闭时执行（如果需要清理资源）

app = FastAPI(title="AI项目管理系统", lifespan=lifespan)

# 配置常量
DATABASE_PATH = os.getenv("DATABASE_PATH", "projects.db")
PROJECTS_DIR = os.getenv("PROJECTS_DIR", "projects")
PORT = int(os.getenv("PORT", "3000"))

# 确保项目目录存在
os.makedirs(PROJECTS_DIR, exist_ok=True)

# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
    
    async def connect(self, websocket: WebSocket, project_id: str = None):
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = {
            'websocket': websocket,
            'project_id': project_id
        }
        return connection_id
    
    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
    
    async def broadcast_progress(self, project_id: str, message: str, msg_type: str = "progress"):
        progress_data = {
            "type": msg_type,
            "projectId": project_id,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        # 广播给订阅该项目的所有连接
        for conn_id, conn_data in self.active_connections.items():
            if conn_data['project_id'] == project_id:
                try:
                    await conn_data['websocket'].send_text(json.dumps(progress_data))
                except:
                    # 连接已断开，移除
                    self.disconnect(conn_id)

manager = ConnectionManager()

# 数据模型
class ProjectCreate(BaseModel):
    name: str
    keyword: str

class ProjectUpdate(BaseModel):
    keyword: str

class PageCreate(BaseModel):
    prompt: Optional[str] = None

# 数据库初始化
async def init_database():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                keyword TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                url_id TEXT NOT NULL,
                version_hash TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        """)
        await db.commit()

# Git辅助函数
async def exec_git_command(command: str, cwd: str) -> str:
    """执行Git命令"""
    try:
        result = subprocess.run(
            command.split(),
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise Exception(f"Git command failed: {e.stderr}")

async def init_git_repo(project_path: str):
    """初始化Git仓库"""
    await exec_git_command("git init", project_path)
    await exec_git_command("git config user.name 'Project Generator'", project_path)
    await exec_git_command("git config user.email 'noreply@project.local'", project_path)

async def commit_to_git(project_path: str, message: str):
    """提交到Git"""
    await exec_git_command("git add .", project_path)
    await exec_git_command(f"git commit -m '{message}'", project_path)

async def get_git_versions(project_path: str) -> List[dict]:
    """获取Git版本历史"""
    try:
        output = await exec_git_command("git log --oneline --reverse", project_path)
        versions = []
        for index, line in enumerate(output.strip().split('\n')):
            if line:
                parts = line.split(' ', 1)
                hash_val = parts[0]
                message = parts[1] if len(parts) > 1 else ""
                versions.append({
                    "hash": hash_val,
                    "message": message,
                    "version": index + 1,
                    "isCurrent": False
                })
        
        # 标记当前版本
        if versions:
            versions[-1]["isCurrent"] = True
        
        return versions
    except:
        return []

# 静态文件服务（如果目录存在）
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# WebSocket端点
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    connection_id = await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                if message.get("type") == "subscribe":
                    project_id = message.get("projectId")
                    if connection_id in manager.active_connections:
                        manager.active_connections[connection_id]['project_id'] = project_id
                        # 发送订阅确认
                        await websocket.send_text(json.dumps({
                            "type": "subscribed",
                            "projectId": project_id,
                            "message": f"已订阅项目 {project_id} 的进度推送"
                        }))
                        
            except json.JSONDecodeError:
                # 忽略非JSON消息
                pass
            except Exception as e:
                print(f"WebSocket message handling error: {e}")
                
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        print(f"WebSocket connection error: {e}")
        manager.disconnect(connection_id)

# API端点
@app.get("/api/projects")
async def get_projects():
    """获取项目列表"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT * FROM projects ORDER BY created_at DESC") as cursor:
            projects = await cursor.fetchall()
            return [
                {
                    "id": p[0],
                    "name": p[1],
                    "keyword": p[2],
                    "created_at": p[3]
                }
                for p in projects
            ]

@app.post("/api/projects")
async def create_project(project: ProjectCreate):
    """创建项目"""
    if not project.name or not project.keyword:
        raise HTTPException(status_code=400, detail="Project name and keyword are required")
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO projects (name, keyword) VALUES (?, ?)",
            (project.name, project.keyword)
        )
        project_id = cursor.lastrowid
        await db.commit()
        
        # 创建项目目录
        project_path = os.path.join(PROJECTS_DIR, project.name)
        os.makedirs(project_path, exist_ok=True)
        
        # 初始化Git仓库
        try:
            await init_git_repo(project_path)
        except Exception as e:
            print(f"Git initialization failed: {e}")
        
        return {
            "id": project_id,
            "name": project.name,
            "keyword": project.keyword,
            "defaultPage": f"http://localhost:{PORT}/page/index"
        }

@app.put("/api/projects/{project_id}")
async def update_project(project_id: int, project: ProjectUpdate):
    """更新项目"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # 检查项目是否存在
        async with db.execute("SELECT * FROM projects WHERE id = ?", (project_id,)) as cursor:
            existing_project = await cursor.fetchone()
            if not existing_project:
                raise HTTPException(status_code=404, detail="Project not found")
        
        # 更新项目
        await db.execute(
            "UPDATE projects SET keyword = ? WHERE id = ?",
            (project.keyword, project_id)
        )
        await db.commit()
        
        return {
            "id": project_id,
            "name": existing_project[1],
            "keyword": project.keyword,
            "created_at": existing_project[3]
        }

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: int):
    """删除项目"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # 检查项目是否存在
        async with db.execute("SELECT name FROM projects WHERE id = ?", (project_id,)) as cursor:
            project = await cursor.fetchone()
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
        
        # 删除数据库记录
        await db.execute("DELETE FROM pages WHERE project_id = ?", (project_id,))
        await db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        await db.commit()
        
        # 删除项目目录
        project_path = os.path.join(PROJECTS_DIR, project[0])
        if os.path.exists(project_path):
            shutil.rmtree(project_path)
        
        return {"message": "Project deleted successfully"}

@app.get("/api/projects/{project_id}/pages")
async def get_project_pages(project_id: int):
    """获取项目页面列表"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # 检查项目是否存在
        async with db.execute("SELECT name FROM projects WHERE id = ?", (project_id,)) as cursor:
            project = await cursor.fetchone()
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
        
        # 获取Git版本历史
        project_path = os.path.join(PROJECTS_DIR, project[0])
        versions = await get_git_versions(project_path)
        
        # 获取页面记录
        async with db.execute(
            "SELECT * FROM pages WHERE project_id = ? ORDER BY created_at DESC",
            (project_id,)
        ) as cursor:
            pages = await cursor.fetchall()
            
            # 合并版本信息
            result = []
            for page in pages:
                page_data = {
                    "id": page[0],
                    "project_id": page[1],
                    "url_id": page[2],
                    "version_hash": page[3],
                    "created_at": page[4]
                }
                
                # 查找对应的版本信息
                for version in versions:
                    if version["hash"] == page[3]:
                        page_data.update({
                            "version": version["version"],
                            "message": version["message"]
                        })
                        break
                
                result.append(page_data)
            
            return result

@app.post("/api/projects/{project_id}/pages")
async def create_page(project_id: int, page: PageCreate):
    """生成新页面"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # 检查项目是否存在
        async with db.execute("SELECT name, keyword FROM projects WHERE id = ?", (project_id,)) as cursor:
            project = await cursor.fetchone()
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
        
        project_name = project[0]
        project_keyword = project[1]
        project_path = os.path.join(PROJECTS_DIR, project_name)
        
        # 使用用户提示词或项目关键字
        user_prompt = page.prompt if page.prompt else project_keyword
        
        # 广播进度开始
        await manager.broadcast_progress(str(project_id), "🚀 开始生成页面...", "progress")
        
        try:
            # 使用AI生成器生成网页内容
            await manager.broadcast_progress(str(project_id), "🚀 开始AI生成...", "progress")
            generation_result = await ai_generator.generate_webpage(
                project_name, 
                user_prompt, 
                str(project_id)
            )
            
            html_content = generation_result["content"]
            generated_with = generation_result["generated_with"]
            
            await manager.broadcast_progress(
                str(project_id), 
                f"✅ 生成完成 (方式: {generated_with})", 
                "success"
            )
            
            #保存HTML文件
            index_path = os.path.join(project_path, "index.html")
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            await manager.broadcast_progress(str(project_id), f"💾 {str(html_content)}", "progress")
            
            # Git提交
            try:
                commit_message = f"生成页面: {project_name} - {user_prompt}"
                await commit_to_git(project_path, commit_message)
                await manager.broadcast_progress(str(project_id), "📝 Git提交完成", "progress")
            except Exception as e:
                await manager.broadcast_progress(str(project_id), f"⚠️ Git提交失败: {str(e)}", "warning")
            
            # 获取最新的Git哈希
            try:
                hash_output = await exec_git_command("git rev-parse --short HEAD", project_path)
                version_hash = hash_output.strip()
            except:
                version_hash = "unknown"
            
            # 保存页面记录
            cursor = await db.execute(
                "INSERT INTO pages (project_id, url_id, version_hash) VALUES (?, ?, ?)",
                (project_id, "index", version_hash)
            )
            page_id = cursor.lastrowid
            await db.commit()
            
            await manager.broadcast_progress(str(project_id), "✅ 页面生成完成!", "success")
            
            return {
                "id": page_id,
                "url_id": "index",
                "url": f"http://localhost:{PORT}/page/index",
                "version": 1,
                "hash": version_hash,
                "generated_with": generated_with,
                "prompt": user_prompt,
                "action": "created"
            }
            
        except Exception as e:
            await manager.broadcast_progress(str(project_id), f"❌ 生成失败: {str(e)}", "error")
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_id}/versions")
async def get_project_versions(project_id: int):
    """获取版本历史"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT name FROM projects WHERE id = ?", (project_id,)) as cursor:
            project = await cursor.fetchone()
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
        
        project_path = os.path.join(PROJECTS_DIR, project[0])
        versions = await get_git_versions(project_path)
        return versions

@app.get("/page/{url_id}")
async def get_page(url_id: str):
    """访问生成的页面"""
    if url_id == "index":
        # 查找最新的项目
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("SELECT name FROM projects ORDER BY created_at DESC LIMIT 1") as cursor:
                project = await cursor.fetchone()
                if not project:
                    raise HTTPException(status_code=404, detail="No projects found")
                
                project_path = os.path.join(PROJECTS_DIR, project[0], "index.html")
                if os.path.exists(project_path):
                    return FileResponse(project_path, media_type="text/html")
    
    raise HTTPException(status_code=404, detail="Page not found")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """主页"""
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI项目管理系统</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .project-form { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .projects-list { background: white; padding: 20px; border-radius: 8px; }
            .project-item { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .btn { padding: 8px 16px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; }
            .btn-primary { background: #007bff; color: white; }
            .btn-success { background: #28a745; color: white; }
            .btn-small { padding: 4px 8px; font-size: 0.8rem; margin: 2px; }
            .keyword-section { margin: 10px 0; }
            .keyword-display { display: flex; align-items: center; gap: 10px; }
            .keyword-edit { display: flex; align-items: center; gap: 10px; }
            .keyword-input { flex: 1; padding: 5px; border: 1px solid #ddd; border-radius: 3px; }
            .keyword-text { font-weight: bold; color: #007bff; }
            .project-actions { margin-top: 10px; }
            .project-actions .btn { margin-right: 5px; }
            .hidden { display: none; }
            .keyword-suggestions { margin-top: 10px; }
            .suggestion-tag { 
                display: inline-block; 
                background: #e9ecef; 
                color: #495057; 
                padding: 3px 8px; 
                margin: 2px; 
                border-radius: 15px; 
                font-size: 0.8rem; 
                cursor: pointer; 
                transition: background 0.2s;
            }
            .suggestion-tag:hover { 
                background: #007bff; 
                color: white; 
            }
            .form-group { margin-bottom: 15px; }
            .form-group label { display: block; margin-bottom: 5px; }
            .form-group input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            .progress { margin: 10px 0; }
            .progress-item { padding: 5px; margin: 2px 0; border-radius: 3px; }
            .progress-item.success { background: #d4edda; color: #155724; }
            .progress-item.error { background: #f8d7da; color: #721c24; }
            .progress-item.warning { background: #fff3cd; color: #856404; }
            .progress-item.progress { background: #d1ecf1; color: #0c5460; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 AI项目管理系统</h1>
                <p>智能网页生成 + 版本控制 + 实时反馈</p>
            </div>
            
            <div class="project-form">
                <h3>创建新项目</h3>
                <form id="projectForm">
                    <div class="form-group">
                        <label>项目名称:</label>
                        <input type="text" id="projectName" required>
                    </div>
                    <div class="form-group">
                        <label>关键字/提示词:</label>
                        <input type="text" id="projectKeyword" required>
                        <div class="keyword-suggestions">
                            <small>推荐关键字：</small>
                            <span class="suggestion-tag" onclick="selectSuggestion('刷题')">刷题</span>
                            <span class="suggestion-tag" onclick="selectSuggestion('考试')">考试</span>
                            <span class="suggestion-tag" onclick="selectSuggestion('计算器')">计算器</span>
                            <span class="suggestion-tag" onclick="selectSuggestion('工具')">工具</span>
                            <span class="suggestion-tag" onclick="selectSuggestion('hello')">hello</span>
                            <span class="suggestion-tag" onclick="selectSuggestion('博客')">博客</span>
                            <span class="suggestion-tag" onclick="selectSuggestion('商城')">商城</span>
                            <span class="suggestion-tag" onclick="selectSuggestion('游戏')">游戏</span>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary">创建项目</button>
                </form>
            </div>
            
            <div class="projects-list">
                <h3>项目列表</h3>
                <div id="projectsList"></div>
            </div>
            
            <div id="progress" class="progress" style="display: none;">
                <h4>生成进度:</h4>
                <div id="progressLog"></div>
            </div>
        </div>
        
        <script>
            let ws;
            
            function connectWebSocket() {
                ws = new WebSocket(`ws://${window.location.host}/ws`);
                
                ws.onmessage = function(event) {
                    try {
                        const data = JSON.parse(event.data);
                        if (data.type === 'subscribed') {
                            console.log('已订阅项目进度推送:', data.message);
                        } else {
                            showProgress(data.message, data.type);
                        }
                    } catch (e) {
                        console.error('WebSocket消息解析错误:', e);
                    }
                };
                
                ws.onopen = function() {
                    console.log('WebSocket连接已建立');
                };
                
                ws.onclose = function(event) {
                    console.log('WebSocket连接已关闭, 代码:', event.code, '原因:', event.reason);
                    setTimeout(connectWebSocket, 3000);
                };
                
                ws.onerror = function(error) {
                    console.error('WebSocket连接错误:', error);
                };
            }
            
            function showProgress(message, type) {
                const progressDiv = document.getElementById('progress');
                const logDiv = document.getElementById('progressLog');
                
                progressDiv.style.display = 'block';
                
                const item = document.createElement('div');
                item.className = `progress-item ${type}`;
                item.textContent = message;
                logDiv.appendChild(item);
                
                logDiv.scrollTop = logDiv.scrollHeight;
                
                if (type === 'success' || type === 'error') {
                    setTimeout(() => {
                        progressDiv.style.display = 'none';
                        logDiv.innerHTML = '';
                        loadProjects();
                    }, 2000);
                }
            }
            
            async function loadProjects() {
                try {
                    const response = await fetch('/api/projects');
                    const projects = await response.json();
                    
                    const listDiv = document.getElementById('projectsList');
                    listDiv.innerHTML = '';
                    
                    projects.forEach(project => {
                        const projectDiv = document.createElement('div');
                        projectDiv.className = 'project-item';
                        projectDiv.innerHTML = `
                            <h4>${project.name}</h4>
                            <div class="keyword-section">
                                <div class="keyword-display" id="keyword-display-${project.id}">
                                    <p>关键字: <span class="keyword-text">${project.keyword}</span></p>
                                    <button class="btn btn-secondary btn-small" onclick="editKeyword(${project.id})">编辑</button>
                                </div>
                                <div class="keyword-edit hidden" id="keyword-edit-${project.id}">
                                    <input type="text" class="keyword-input" id="keyword-input-${project.id}" value="${project.keyword}">
                                    <button class="btn btn-primary btn-small" onclick="saveKeyword(${project.id})">保存</button>
                                    <button class="btn btn-secondary btn-small" onclick="cancelEditKeyword(${project.id})">取消</button>
                                </div>
                            </div>
                            <p>创建时间: ${new Date(project.created_at).toLocaleString()}</p>
                            <div class="project-actions">
                                <button class="btn btn-primary" onclick="generatePage(${project.id})">生成页面</button>
                                <button class="btn btn-success" onclick="regenerateWithKeyword(${project.id})">重新生成</button>
                                <button class="btn btn-primary" onclick="viewPage(${project.id})">查看页面</button>
                                <button class="btn btn-danger" onclick="deleteProject(${project.id})">删除</button>
                            </div>
                        `;
                        listDiv.appendChild(projectDiv);
                    });
                } catch (error) {
                    console.error('加载项目失败:', error);
                }
            }
            
            async function generatePage(projectId) {
                if (ws) {
                    ws.send(JSON.stringify({
                        type: 'subscribe',
                        projectId: projectId.toString()
                    }));
                }
                
                try {
                    const response = await fetch(`/api/projects/${projectId}/pages`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({})
                    });
                    
                    if (!response.ok) {
                        throw new Error('生成失败');
                    }
                    
                } catch (error) {
                    showProgress(`生成失败: ${error.message}`, 'error');
                }
            }
            
            function selectSuggestion(keyword) {
                document.getElementById('projectKeyword').value = keyword;
            }
            
            function editKeyword(projectId) {
                document.getElementById(`keyword-display-${projectId}`).classList.add('hidden');
                document.getElementById(`keyword-edit-${projectId}`).classList.remove('hidden');
                document.getElementById(`keyword-input-${projectId}`).focus();
            }
            
            function cancelEditKeyword(projectId) {
                document.getElementById(`keyword-display-${projectId}`).classList.remove('hidden');
                document.getElementById(`keyword-edit-${projectId}`).classList.add('hidden');
            }
            
            async function saveKeyword(projectId) {
                const newKeyword = document.getElementById(`keyword-input-${projectId}`).value;
                
                if (!newKeyword.trim()) {
                    alert('关键字不能为空');
                    return;
                }
                
                try {
                    const response = await fetch(`/api/projects/${projectId}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ keyword: newKeyword })
                    });
                    
                    if (response.ok) {
                        // 更新显示的关键字
                        document.querySelector(`#keyword-display-${projectId} .keyword-text`).textContent = newKeyword;
                        document.getElementById(`keyword-display-${projectId}`).classList.remove('hidden');
                        document.getElementById(`keyword-edit-${projectId}`).classList.add('hidden');
                        showProgress(`✅ 关键字已更新为: ${newKeyword}`, 'success');
                    } else {
                        throw new Error('更新失败');
                    }
                } catch (error) {
                    console.error('更新关键字失败:', error);
                    showProgress(`❌ 更新失败: ${error.message}`, 'error');
                }
            }
            
            async function regenerateWithKeyword(projectId) {
                // 首先检查关键字是否在编辑状态，如果是则先保存
                const editSection = document.getElementById(`keyword-edit-${projectId}`);
                if (!editSection.classList.contains('hidden')) {
                    await saveKeyword(projectId);
                }
                
                // 显示确认对话框
                if (confirm('确定要基于当前关键字重新生成页面吗？这将创建一个新的版本。')) {
                    // 订阅WebSocket进度
                    if (ws) {
                        ws.send(JSON.stringify({
                            type: 'subscribe',
                            projectId: projectId.toString()
                        }));
                    }
                    
                    // 生成页面
                    try {
                        const response = await fetch(`/api/projects/${projectId}/pages`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({})
                        });
                        
                        if (!response.ok) {
                            throw new Error('重新生成失败');
                        }
                        
                    } catch (error) {
                        showProgress(`重新生成失败: ${error.message}`, 'error');
                    }
                }
            }
            
            function viewPage(projectId) {
                window.open('/page/index', '_blank');
            }
            
            async function deleteProject(projectId) {
                if (confirm('确定要删除这个项目吗？')) {
                    try {
                        const response = await fetch(`/api/projects/${projectId}`, {
                            method: 'DELETE'
                        });
                        
                        if (response.ok) {
                            loadProjects();
                        }
                    } catch (error) {
                        console.error('删除失败:', error);
                    }
                }
            }
            
            document.getElementById('projectForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const name = document.getElementById('projectName').value;
                const keyword = document.getElementById('projectKeyword').value;
                
                try {
                    const response = await fetch('/api/projects', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ name, keyword })
                    });
                    
                    if (response.ok) {
                        document.getElementById('projectForm').reset();
                        loadProjects();
                    }
                } catch (error) {
                    console.error('创建项目失败:', error);
                }
            });
            
            // 初始化
            connectWebSocket();
            loadProjects();
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)