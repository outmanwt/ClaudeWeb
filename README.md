# AI 项目管理系统

一个支持**AI智能网页生成**的项目管理系统，集成Claude Code AI能力，支持版本控制、实时进度追踪和高质量模板后备方案。
![20250709104741](https://github.com/user-attachments/assets/668598bc-a262-41f3-960b-7d8202e277bc)
![20250709104742](https://github.com/user-attachments/assets/d591d23c-b128-438d-b4f6-6e1ca61da82c)

## ✨ 核心功能

- 🤖 **AI智能生成**: 优先使用Claude Code生成个性化网页
- 🎨 **高质量模板**: AI不可用时自动切换到精美模板
- 📝 **项目管理**: 完整的项目CRUD操作
- 📦 **Git版本控制**: 每次生成都创建Git提交，支持版本回退
- 🔄 **实时反馈**: WebSocket实时推送生成进度
- 🌐 **响应式设计**: 支持移动端和桌面端访问

## 🛠️ 技术栈

- **后端**: Python + FastAPI + SQLite + Git + WebSocket
- **AI集成**: Claude Code CLI/SDK
- **前端**: HTML5 + CSS3 + JavaScript (无框架依赖)
- **数据库**: SQLite3 (轻量级，无需配置)

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Git
- 现代浏览器

### 安装运行

1. **克隆或下载项目**:
   ```bash
   # 如果是Git仓库
   git clone <repository-url>
   cd aiweb
   ```

2. **一键启动**:
   ```bash
   ./start.sh
   ```
   
   或手动启动：
   ```bash
   # 创建虚拟环境
   python3 -m venv venv
   source venv/bin/activate
   
   # 安装依赖
   pip install -r requirements.txt
   
   # 启动服务器
   python main.py
   ```

3. **访问系统**:
   - 打开浏览器访问: http://localhost:3000
   - 创建项目并开始生成网页！

## 📋 使用指南

### 创建项目

1. 在首页填写项目名称和关键字
2. 点击"创建项目"
3. 系统会自动初始化Git仓库

### 生成网页

1. 点击项目的"生成页面"按钮
2. 系统会实时显示生成进度：
   - 🤖 尝试Claude Code AI生成
   - 🎨 失败时自动使用高质量模板
   - 📝 保存文件并提交Git
3. 生成完成后点击"查看页面"

### 查看版本历史

- 每次生成都会创建Git提交
- 支持查看完整的版本历史
- 可以回退到任意历史版本

## 🎨 模板系统

系统内置三种高质量模板：

### 1. 刷题系统模板
- **触发关键字**: 刷题、考试、题目
- **功能**: 完整的证券从业题库系统
- **特点**: 交互式选择题、实时评分、进度追踪

### 2. 计算器模板  
- **触发关键字**: 计算器、工具、calculator
- **功能**: 完整的科学计算器
- **特点**: 键盘支持、历史记录、本地存储

### 3. Hello World模板
- **触发关键字**: hello、测试，或其他关键字
- **功能**: 美观的展示页面
- **特点**: 动态背景、实时时钟、交互动画

## 🔧 配置说明

### Claude Code集成

系统支持两种Claude Code集成方式：

1. **Claude Code CLI**:
   ```bash
   # 安装Claude Code CLI
   npm install -g @anthropic-ai/claude-code
   
   # 或者使用最新版本
   npm install -g claude-code
   ```

2. **Claude Code Python SDK** (推荐):
   ```bash
   # 已包含在requirements.txt中
   pip install claude-code-sdk
   ```

### API密钥配置

1. 复制环境变量模板：
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，添加你的API密钥：
   ```bash
   ANTHROPIC_API_KEY=your_api_key_here
   ```

3. 从 [Anthropic Console](https://console.anthropic.com/) 获取API密钥

**注意**: 如果没有配置API密钥，系统会自动使用高质量模板生成，不影响基本功能。

### 环境变量

可以通过环境变量配置系统：

```bash
export ANTHROPIC_API_KEY="your-api-key"      # Claude Code API密钥
export DATABASE_PATH="./projects.db"         # 数据库路径
export PROJECTS_DIR="./projects"             # 项目存储目录
export PORT="3000"                           # 服务器端口
```

## 📡 API 文档

### 项目管理

- `GET /api/projects` - 获取项目列表
- `POST /api/projects` - 创建项目
- `PUT /api/projects/{id}` - 更新项目
- `DELETE /api/projects/{id}` - 删除项目

### 页面生成

- `POST /api/projects/{id}/pages` - 生成新页面
- `GET /api/projects/{id}/pages` - 获取页面列表
- `GET /page/{url_id}` - 访问生成的页面

### 版本管理

- `GET /api/projects/{id}/versions` - 获取版本历史
- `POST /api/projects/{id}/checkout/{hash}` - 切换版本

### WebSocket

- `ws://localhost:3000/ws` - 实时进度推送

详细API文档请参考代码注释或启动服务后访问 /docs

## 🧪 测试

运行自动化测试：

```bash
./test.sh
```

测试包括：
- 项目CRUD操作
- 页面生成功能
- API端点验证
- 页面访问测试

## 📁 项目结构

```
aiweb/
├── main.py              # FastAPI主服务器
├── templates.py         # 高质量模板生成器
├── ai_generator.py      # AI生成系统
├── requirements.txt     # Python依赖
├── start.sh            # 启动脚本
├── test.sh             # 测试脚本
├── projects.db         # SQLite数据库
├── projects/           # 项目存储目录
│   ├── 项目A/
│   │   ├── .git/      # Git仓库
│   │   └── index.html # 生成的网页
│   └── 项目B/
└── venv/              # Python虚拟环境
```

## 🔍 故障排除

### 常见问题

1. **Claude Code不可用**:
   - 检查API密钥配置
   - 确认网络连接
   - 系统会自动使用模板后备

2. **Git提交失败**:
   - 检查Git配置
   - 确认项目目录权限
   - 不影响页面生成

3. **端口被占用**:
   ```bash
   # 查找占用端口的进程
   lsof -i :3000
   
   # 或修改端口
   export PORT=8000
   python main.py
   ```

### 日志查看

- 服务器日志会实时显示在终端
- Git操作日志保存在项目目录
- WebSocket连接状态在浏览器控制台

## 🎯 功能特点

### 智能生成策略

1. **优先级1**: Claude Code AI生成 (个性化内容)
2. **优先级2**: 高质量模板生成 (专业功能)
3. **优先级3**: 简单后备模板 (基础展示)

### 版本控制

- 每次生成自动Git提交
- 完整的版本历史追踪
- 支持一键回退到任意版本
- Git信息与页面记录关联

### 实时反馈

- WebSocket实时推送生成进度
- 清晰的状态提示 (进行中/成功/错误/警告)
- 用户友好的错误处理

## 🚧 开发计划

### 近期计划

- [ ] 增加更多模板类型
- [ ] 支持自定义模板
- [ ] 多项目并发生成
- [ ] 用户权限管理

### 长期规划

- [ ] 微服务架构重构
- [ ] 多AI模型支持 (GPT, Gemini)
- [ ] 云端部署方案
- [ ] 移动端应用

## 📄 许可证

MIT License - 详见项目根目录的LICENSE文件

## 🤝 贡献

欢迎提交Issue和Pull Request！请遵循以下贡献指南：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

**享受AI驱动的智能网页生成体验！** 🎉
