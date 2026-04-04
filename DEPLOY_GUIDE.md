# 🎬 AI 小说创意平台 - 完整部署指南

## 📋 目录结构

```
ai-novel-reader/
├── index.html              ← 改造的首页（包含短剧工厂和审核中心）
├── api/                    ← FastAPI 后端应用
│   ├── main.py            ← 核心应用入口
│   ├── requirements.txt    ← Python 依赖
│   └── handlers/           ← 业务逻辑模块
│       ├── drama_converter.py      ← 小说转剧本
│       ├── drama_reviewer.py       ← AI 审核
│       ├── batch_manager.py        ← 批次管理
│       └── github_storage.py       ← GitHub 集成
├── drama_data/             ← 剧本数据存储
│   ├── batches.json
│   ├── batch_001/
│   │   ├── novel_id_script.json
│   │   ├── novel_id_review.json
│   │   └── status.json
├── Dockerfile              ← Lambda 容器镜像
├── deploy.sh               ← 部署脚本
└── .env.example            ← 环境变量示例

novels/
├── index.json              ← 小说列表元数据
├── novel_id_001/
│   ├── chapter_0001.json   ← 小说内容
│   └── chapters.json
...
```

## 🚀 快速开始

### 1️⃣ 前置准备

需要的 API Key：
- OpenAI API Key (https://platform.openai.com/api-keys)
- Anthropic Claude API Key (https://console.anthropic.com/)
- GitHub Personal Token (https://github.com/settings/tokens)
- AWS 账号 (用于 Lambda 部署)

### 2️⃣ 本地开发环境配置

```bash
# 1. 进入 API 目录
cd api

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 创建 .env 文件
cp ../.env.example .env
# 编辑 .env，填入你的 API Key
```

### 3️⃣ 本地测试运行

```bash
# 在 api 目录下
python main.py

# 测试 API（新开终端）
curl http://localhost:8000/health

# 测试转换功能
curl -X POST http://localhost:8000/api/drama/convert \
  -H "Content-Type: application/json" \
  -d '{"novel_id":"apocalypse-food","batch_id":"batch_001"}'
```

### 4️⃣ 网站本地测试

```bash
# 在项目根目录启动简单 HTTP 服务器
python -m http.server 8080
```

然后打开 http://localhost:8080 查看网站。

在"短剧工厂"标签页中：
- 输入 API 地址：http://localhost:8000
- 点击"开始转换"按钮测试

## ☁️ 云部署指南

### 方案 1: AWS Lambda + API Gateway（推荐）

#### 1a. 创建 Lambda 函数

```bash
# 使用 AWS 管理控制台或 CLI

# 方式 1：使用 Docker 镜像
aws lambda create-function \
  --function-name ai-novel-drama-converter \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-role \
  --code ImageUri=YOUR_ECR_URI:latest \
  --package-type Image \
  --timeout 300 \
  --memory-size 512 \
  --environment Variables='{
    OPENAI_API_KEY=sk_xxxx,
    ANTHROPIC_API_KEY=sk_xxxx,
    GITHUB_TOKEN=ghp_xxxx
  }' \
  --region us-east-1

# 方式 2：使用 ZIP 包
cd api
mkdir -p build
pip install -r requirements.txt -t build/
cp main.py handlers/ build/
cd build && zip -r ../lambda.zip . && cd ..
aws lambda create-function \
  --function-name ai-novel-drama-converter \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-role \
  --handler main.handler \
  --zip-file fileb://lambda.zip
```

#### 1b. 设置 API Gateway

```bash
# 创建 REST API
aws apigateway create-rest-api \
  --name drama-converter-api \
  --description "AI Novel Drama Converter API"

# 创建资源和方法（通过控制台更便捷）
# 或使用 CLI 脚本自动化
```

#### 1c. 获取 API 公网 URL

在 API Gateway 控制台获取调用 URL：
```
https://xxxxx.execute-api.us-east-1.amazonaws.com/prod
```

#### 1d. 配置 CORS（重要！）

在 API Gateway 中为每个方法启用 CORS：
```
Access-Control-Allow-Origin: https://ccdmo.github.io
Access-Control-Allow-Methods: GET,POST,PUT,DELETE,OPTIONS
Access-Control-Allow-Headers: Content-Type,Authorization
```

### 方案 2: GitHub Actions 自动部署

编辑 `.github/workflows/deploy-lambda.yml`：

```yaml
# 设置 GitHub Secrets
# 1. Settings → Secrets → New repository secret
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
# - AWS_REGION = us-east-1
# - OPENAI_API_KEY = sk_xxxx
# - ANTHROPIC_API_KEY = sk_xxxx
# - GITHUB_TOKEN = ghp_xxxx

# 然后 git push 会自动触发部署
```

### 方案 3: Railway/Render/Fly.io 一键部署

在这些平台中连接 GitHub 仓库，设置环境变量后自动部署。

**环境变量设置：**
```
OPENAI_API_KEY=sk_xxxx
ANTHROPIC_API_KEY=sk_xxxx
GITHUB_TOKEN=ghp_xxxx
GITHUB_REPO=your-username/ai-novel-reader
```

## 🔌 前后端集成

### 前端配置

编辑 `index.html` 中的 API 地址输入框：

```javascript
// drama-factory.html 中会自动使用用户输入的 API 地址
document.getElementById('apiEndpoint').value = 'https://your-api-endpoint.com'
```

### 新增 API 端点

前端支持的所有 API 端点：

```
POST   /api/drama/convert
GET    /api/drama/batch/{batch_id}
GET    /api/drama/audit-list
PUT    /api/drama/approve/{novel_id}
PUT    /api/drama/reject/{novel_id}
GET    /api/drama/{novel_id}
GET    /api/stats
```

## 📊 使用工作流

### 工作流 1: 批量转换小说

```
用户界面 (index.html)
  ↓
[短剧工厂标签页]
  ↓
选择处理数量 (5部)
  ↓
输入 API 地址
  ↓
点击 "🚀 开始转换"
  ↓
前端调用 POST /api/drama/convert (5次)
  ↓
[后端 FastAPI]
  ↓
1. 读取小说内容 (novels/index.json)
  ↓
2. LLM 转换 (OpenAI/Claude)
  ↓
3. AI 审核 (Anthropic)
  ↓
4. 保存到 GitHub (后台)
  ↓
返回结果给前端
  ↓
[用户看到实时进度表]
  ↓
每行显示：小说名、状态、评分、建议
```

### 工作流 2: 审核和批准

```
[审核中心标签页]
  ↓
自动加载待审核列表 (GET /api/drama/audit-list)
  ↓
显示质量评分和 AI 建议
  ↓
用户点击 "✅ 批准" 或 "❌ 拒绝"
  ↓
发送 PUT /api/drama/approve/{novel_id}
  ↓
[后端更新状态]
  ↓
结果保存到本地 drama_data/ 和 GitHub
```

## 📁 数据存储结构

### 本地存储 (drama_data/)

```json
{
  "batch_001_status.json": {
    "batch_id": "batch_001",
    "created_at": "2024-01-01T10:00:00",
    "total_required": 5,
    "completed": 5,
    "novels": {
      "apocalypse-food": {
        "score": 85,
        "status": "pending",
        "completed_at": "2024-01-01T10:05:00",
        "approval_status": "approved"
      }
    }
  },
  "batch_001/apocalypse-food_script.json": {
    "title": "剧本标题",
    "scenes": [...]
  },
  "batch_001/apocalypse-food_review.json": {
    "quality_score": 85,
    "summary": "总体评价",
    "issues": [],
    "suggestions": []
  }
}
```

### GitHub 存储

同步结构自动上传到：
```
drama_data/batch_001/novel_id_script.json
drama_data/batch_001/novel_id_review.json
```

## 🔧 故障排查

### 问题 1: 转换失败 (503 / API Key 错误)

```bash
# 检查环境变量
export OPENAI_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key

# 测试 API 连接
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

### 问题 2: CORS 错误

确保 API Gateway 启用了 CORS：
```bash
aws apigateway put-integration-response \
  --rest-api-id API_ID \
  --resource-id RESOURCE_ID \
  --http-method OPTIONS \
  --status-code 200 \
  --response-parameters '{"method.response.header.Access-Control-Allow-Headers":"'"'"'*'"'"'","method.response.header.Access-Control-Allow-Origin":"'"'"'*'"'"'"}'
```

### 问题 3: 剧本存储失败

检查：
1. GitHub Token 是否正确
2. drama_data 目录是否存在
3. 本地权限是否正确

```bash
ls -la drama_data/
chmod 755 drama_data/
```

## 📈 监控和日志

### CloudWatch 日志（Lambda）

```bash
aws logs tail /aws/lambda/ai-novel-drama-converter --follow
```

### 本地日志

```bash
# 启用详细日志
export LOG_LEVEL=DEBUG
python main.py
```

## 🛡️ 安全建议

1. **API Key 管理**
   - 不要将 key 提交到 Git
   - 使用环境变量或 AWS Secrets Manager
   - 定期轮换 key

2. **CORS 安全**
   ```
   Allow-Origin: https://ccdmo.github.io (严格指定)
   只允许必要的 methods: POST, GET, PUT
   ```

3. **Rate Limiting**
   在 API Gateway 添加速率限制，防止滥用

4. **输入验证**
   所有 novel_id 都应该先验证是否存在

## 📚 下一步

- [ ] 部署到 Lambda
- [ ] 配置 API Gateway
- [ ] 测试前后端集成
- [ ] 设置 GitHub Actions 自动部署
- [ ] 监控运维仪表板
- [ ] 性能优化和缓存

## 💬 常见问题

**Q: 转换一部小说需要多长时间？**
A: 约 30-60 秒（取决于小说长度和 LLM API 响应时间）

**Q: 可以离线使用吗？**
A: 不行，需要 OpenAI/Anthropic API 和网络连接

**Q: 剧本质量如何？**
A: 取决于 LLM 模型，建议使用 GPT-4/Claude 3 以上获得更好质量

**Q: 支持其他 LLM 吗？**
A: 可以，修改 drama_converter.py 中的模型调用即可

---

**需要帮助？** 提交 Issue 或 PR！🚀
