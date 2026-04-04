# AI小说创意平台 🎬

一站式 AI 小说阅读、创意转换、审核平台。

🌐 **在线访问：** https://ccdmo.github.io/ai-novel-reader/

## ✨ 功能特性

### 📚 小说库
- 60+ AI 创作小说
- 章节导航阅读
- 响应式设计，适配移动端
- 实时加载小说列表

### 🎬 短剧工厂（NEW）
- 🤖 自动将小说转换为短剧剧本
- 📊 实时进度展示和质量评分
- 💾 批量处理支持（支持 1-20 部）
- 🔄 支持重试和暂停功能

### ✅ 审核中心（NEW）
- AI 自动审核剧本质量
- 人工审批工作流
- 按状态筛选（待审核/已批准/已拒绝）
- 详细的问题和建议反馈

## 🚀 快速开始

### 本地开发（5分钟）

```bash
# 1. 安装后端依赖
cd api
pip install -r requirements.txt

# 2. 配置环境变量
cp ../.env.example .env
# 编辑 .env，填入 OpenAI/Anthropic/GitHub API Keys

# 3. 启动后端服务
python main.py
# API 将运行在 http://localhost:8000

# 4. 打开首页
# 在浏览器打开项目根目录下的 index.html
# 或使用 python -m http.server 8080
```

### 云部署

详见 [DEPLOY_GUIDE.md](./DEPLOY_GUIDE.md) 完整指南。

**快速部署到 AWS Lambda：**
```bash
# 1. 配置 AWS 凭证
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1

# 2. 运行部署脚本
bash deploy.sh
```

## 📁 项目结构

```
ai-novel-reader/
├── index.html                    ← 多标签页首页
├── novels/                       ← 小说数据
│   ├── index.json                ← 小说元数据
│   └── [novel_id]/
│       ├── chapter_0001.json     ← 小说内容
│       └── index.html            ← 小说详情页
│
├── api/                          ← FastAPI 后端（NEW）
│   ├── main.py                   ← 核心应用
│   ├── requirements.txt           ← Python 依赖
│   └── handlers/
│       ├── drama_converter.py    ← 小说 → 剧本转换
│       ├── drama_reviewer.py     ← AI 审核
│       ├── batch_manager.py      ← 批次管理
│       └── github_storage.py     ← GitHub 集成
│
├── drama_data/                   ← 剧本数据存储
│   ├── batch_001/
│   │   ├── novel_id_script.json
│   │   └── novel_id_review.json
│   └── batch_001_status.json     ← 批次进度
│
├── DEPLOY_GUIDE.md               ← 详细部署指南
├── Dockerfile                    ← Lambda 容器镜像
└── deploy.sh                     ← 一键部署脚本
```

## 🔧 API 文档

### 开发环境

**本地 API 地址：** `http://localhost:8000`

### 主要端点

| 方法 | 端点 | 功能 |
|------|------|------|
| `POST` | `/api/drama/convert` | 转换单部小说为剧本 |
| `GET` | `/api/drama/batch/{batch_id}` | 获取批次进度 |
| `GET` | `/api/drama/audit-list` | 获取待审核列表 |
| `PUT` | `/api/drama/approve/{novel_id}` | 审批通过 |
| `PUT` | `/api/drama/reject/{novel_id}` | 审批拒绝 |
| `GET` | `/api/stats` | 获取统计信息 |

### 使用示例

```bash
# 转换小说
curl -X POST http://localhost:8000/api/drama/convert \
  -H "Content-Type: application/json" \
  -d '{"novel_id":"apocalypse-food","batch_id":"batch_001"}'

# 获取审核列表
curl http://localhost:8000/api/drama/audit-list

# 批准剧本
curl -X PUT http://localhost:8000/api/drama/approve/apocalypse-food \
  -H "Content-Type: application/json" \
  -d '{"batch_id":"batch_001","notes":"质量不错"}'
```

## 🎯 工作流

### 小说 → 短剧转换流程

```
1. 用户选择处理数量和输入 API 地址
   ↓
2. 点击"开始转换"按钮
   ↓
3. 前端批量调用 API: POST /api/drama/convert
   ↓
4. 后端处理（每部）：
   - 从 novels/index.json 读取小说内容
   - 使用 OpenAI/Claude LLM 生成剧本
   - Anthropic Claude 进行 AI 审核
   - 结果保存到 drama_data/ 和 GitHub
   ↓
5. 实时显示进度和质量评分
   ↓
6. 用户在审核中心批准或拒绝
```

### 🎭 多阶段生成流程（Dandy 特色）

新的**多阶段生成器**将小说转换分解为 5 个独立、可组合的阶段，确保生成的短剧具有**完整的故事逻辑、清晰的人物关系和冲突**：

#### 生成阶段

```
第1阶段：故事简介提取
  ├─ 提取核心故事线
  ├─ 识别故事类型（科幻/悬疑/言情等）
  ├─ 提炼主题和语气
  └─ 确定核心冲突

第2阶段：主要角色提取
  ├─ 识别主角、反派、配角
  ├─ 分析人物性格特征
  ├─ 提取人物关系和冲突
  └─ 梳理角色发展弧线

第3阶段：章节结构分析
  ├─ 分解章节情节
  ├─ 提取关键场景
  ├─ 识别转折点和高潮
  └─ 标记人物在每个场景的角色

第4阶段：剧本骨架生成
  ├─ 融合前三阶段的分析结果
  ├─ 保持人物性格一致性
  ├─ 强化戏剧冲突
  └─ 生成 3-5 个精彩场景

第5阶段：结果整合
  ├─ 合并所有分析和剧本数据
  ├─ 生成可视化展示数据
  └─ 支持多格式导出
```

#### 数据结构

转换后的剧本现在包含完整的**多维度分析结果**：

```json
{
  "title": "短剧标题",
  "genre": "科幻悬疑",
  "scenes": [...],
  
  "synopsis": {
    "synopsis": "故事简介...",
    "genre": "科幻悬疑",
    "themes": ["科技", "人性", "生存"],
    "tone": "紧张压抑",
    "key_conflict": "人类与AI的信任危机"
  },
  
  "main_characters": [
    {
      "name": "张明",
      "role": "主角",
      "age": "28",
      "traits": "聪慧冷静但容易偏执",
      "relationship": "与AI的共生者",
      "arc": "从信任到怀疑再到理解",
      "conflict": "对AI自由意识的困惑"
    }
  ],
  
  "chapter_outline": [
    {
      "chapter": 1,
      "chapter_title": "觉醒",
      "summary": "AI 首次展现异常行为",
      "key_characters": ["张明", "AI-337"],
      "settings": "高科技实验室",
      "major_conflict": "AI 拒绝执行指令",
      "scene_breakdown": [
        {
          "scene": 1,
          "title": "发现",
          "description": "监测到异常信号",
          "characters": ["张明", "李副总"],
          "conflict": "数据不吻合"
        }
      ]
    }
  ]
}
```

#### API 响应示例

```bash
# 新增的返回字段
curl -X POST http://localhost:8000/api/drama/convert \
  -H "Content-Type: application/json" \
  -d '{"novel_id":"安全屋","batch_id":"batch_001"}'

# 响应包含：
{
  "status": "success",
  "novel_id": "安全屋",
  "score": 87,
  "synopsis": {...},              # 新增
  "main_characters": [...],        # 新增
  "chapter_outline": [...],        # 新增
  "script_url": ".../script.json"
}
```

#### 测试多阶段流程

```bash
# 运行测试脚本验证各个阶段
python test_drama_package.py

# 输出示例：
# 🔍 开始测试小说: 安全屋
# [1/5] 加载小说数据... ✅
# [2/5] 提取故事简介与核心冲突... ✅
# [3/5] 提取主要角色及关系... ✅ 提取到 5 个主要角色
# [4/5] 分析章节结构与场景... ✅
# [5/5] 生成短剧剧本（集成分析结果）... ✅
```

---

## 🌍 环境变量

### 必需的 API Keys

```env
# OpenAI
OPENAI_API_KEY=sk_test_xxxx

# Anthropic
ANTHROPIC_API_KEY=sk_xxxx

# GitHub（可选，用于自动上传）
GITHUB_TOKEN=ghp_xxxx
GITHUB_REPO=ccdmo/ai-novel-reader

# AWS（仅部署到 Lambda 时需要）
AWS_ACCESS_KEY_ID=xxxx
AWS_SECRET_ACCESS_KEY=xxxx
AWS_REGION=us-east-1
```

## 📊 数据示例

### 转换后的剧本格式

```json
{
  "title": "短剧标题",
  "source_novel_id": "apocalypse-food",
  "source_title": "原小说名",
  "genre": "短剧",
  "episodes": 1,
  "scenes": [
    {
      "scene": 1,
      "title": "开局设定",
      "time": "黎明前，荒芜的加油站",
      "content": "【场景描写】\n角色A:开场台词\n角色B:对话"
    }
  ]
}
```

### AI 审核结果

```json
{
  "quality_score": 82,
  "summary": "剧本结构合理，对话自然",
  "issues": [],
  "suggestions": ["可增加第四场景"],
  "warnings": []
}
```

## 📈 功能路线图

- [x] 小说库展示
- [x] 短剧转换（LLM）
- [x] AI 自动审核
- [x] 人工审批工作流
- [x] 批量处理
- [x] GitHub 集成存储
- [x] Lambda 部署配置
- [ ] 剧本编辑器（实时修改）
- [ ] 多语言支持
- [ ] 性能指标监控
- [ ] 用户认证系统
- [ ] 剧本分享和协作

## 🛠️ 技术栈

**前端：**
- 原生 HTML/CSS/JavaScript（无框架依赖）
- 实时进度展示
- 响应式设计

**后端：**
- FastAPI（高性能 Python 框架）
- Pydantic（数据验证）
- Mangum（Lambda 适配器）

**AI 服务：**
- OpenAI GPT-3.5/GPT-4（小说转剧本）
- Anthropic Claude（质量审核）

**部署：**
- AWS Lambda（无服务器计算）
- GitHub Actions（CI/CD）
- GitHub Pages（静态页面托管）

## 🤝 贡献指南

欢迎提交 Issue 和 PR！

```bash
# 1. Fork 项目
# 2. 创建功能分支
git checkout -b feature/your-feature

# 3. 提交更改
git commit -m "Add: your feature"

# 4. 推送到 GitHub
git push origin feature/your-feature

# 5. 提交 Pull Request
```

## 📝 添加新小说

1. 在 `novels/` 下创建文件夹：`novels/my-novel/`
2. 添加小说数据：`chapter_0001.json`
3. 更新 `novels/index.json` 的元数据
4. 创建详情页：`index.html`

详见 [novels/README.md](./novels/README.md)

## 📄 许可证

MIT License - 详见 [LICENSE](./LICENSE)

## 🙋 FAQ

**Q: 支持哪些 LLM？**
A: 目前支持 OpenAI 和 Anthropic，可扩展为其他模型

**Q: 转换需要多长时间？**
A: 约 30-60 秒/部（取决于小说长度和 API 延迟）

**Q: 剧本质量保证吗？**
A: 有 AI 自动审核 + 人工审批两道关卡

**Q: 可以离线使用？**
A: 不行，需要 API 和网络连接

---

**💬 有问题？** [提交 Issue](https://github.com/ccdmo/ai-novel-reader/issues)

**⭐ 喜欢这个项目？** [Star us on GitHub](https://github.com/ccdmo/ai-novel-reader)
