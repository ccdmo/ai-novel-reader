# 🚀 快速上手指南（5分钟）

## ⚡ 最快方式：本地测试

### 第 1 步：获取 API Keys（2分钟）

1. **OpenAI Key**
   - 访问 https://platform.openai.com/api-keys
   - 创建新 key
   - 复制保存

2. **Anthropic(Claude) Key**
   - 访问 https://console.anthropic.com/
   - 获取 API key
   - 复制保存

### 第 2 步：本地启动后端（1分钟）

```bash
# Windows
cd api
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
set OPENAI_API_KEY=sk_test_xxxx
set ANTHROPIC_API_KEY=sk_xxxx
python main.py

# macOS/Linux
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk_test_xxxx
export ANTHROPIC_API_KEY=sk_xxxx  
python main.py
```

✅ 看到 `Uvicorn running on http://0.0.0.0:8000` 就成功了

### 第 3 步：打开网站（1分钟）

方式 A：直接打开
```
D:\003_True_Code\0.6小说Agent\ai-novel-reader\index.html
```

方式 B：本地服务器
```bash
# 新开一个终端，在项目根目录
python -m http.server 8080
# 然后打开 http://localhost:8080
```

### 第 4 步：测试短剧工厂（1分钟）

1. 打开网站，点击 **"🎬 短剧工厂"** 标签页
2. 输入 API 地址：`http://localhost:8000`
3. 保持批处理数量为 5
4. 点击 **"🚀 开始转换"** 按钮
5. 看到进度条和实时结果！

---

## ☁️ 云部署快速版

### 方案 1：使用 Railway（最快）

用时：5分钟部署

```bash
# 1. 到 railway.app 注册
# 2. 连接 GitHub 仓库
# 3. 添加环境变量：
#    OPENAI_API_KEY=sk_xxxx
#    ANTHROPIC_API_KEY=sk_xxxx
#    GITHUB_TOKEN=ghp_xxxx
# 4. 等待自动部署

# 获取 API 地址
# Settings → Domains → 复制公网 URL
```

### 方案 2：AWS Lambda（最稳定）

用时：15分钟

```bash
# 1. 创建 IAM 角色（AWS 控制台）
# 2. 创建 Lambda 函数
# 3. 上传代码包
cd api && zip -r lambda.zip . && cd ..
aws lambda update-function-code \
  --function-name ai-novel-drama-converter \
  --zip-file fileb://api/lambda.zip

# 4. 创建 API Gateway 并获取 URL
```

---

## 🎯 常用命令速查

```bash
# 启动后端
python api/main.py

# 测试 API (新开终端)
curl http://localhost:8000/health

# 查看日志
tail -f *.log

# 提交代码
git add -A
git commit -m "feat: description"
git push

# 检查依赖
pip list
pip install -r api/requirements.txt --upgrade
```

---

## ✅ 验证清单

- [ ] 获取了 3 个 API Keys
- [ ] 本地后端成功启动
- [ ] 网站能打开
- [ ] 短剧工厂能调用 API
- [ ] 看到了转换结果
- [ ] 审核中心能加载数据

---

## 🆘 卡住了？

### 后端启动失败
```bash
# 检查 Python 版本
python --version  # 需要 3.8+

# 重新安装依赖
pip install -r api/requirements.txt --force-reinstall
```

### API 返回 401
```bash
# 检查 API Key
echo $OPENAI_API_KEY  # 应该不是空的
echo $ANTHROPIC_API_KEY
```

### 转换失败
```bash
# 查看后端输出
# 通常是 API Key 问题或超时
# 尝试增加超时时间
```

### CORS 错误
```bash
# 如果看到 CORS blocked 错误，说明 API 地址输入错误
# 确保是 http://localhost:8000（不是 https）
```

---

## 📞 下一步

完成本地测试后：

1. **阅读** [DEPLOY_GUIDE.md](./DEPLOY_GUIDE.md) 了解云部署
2. **配置** GitHub Actions 自动部署
3. **监控** CloudWatch/Railway 日志
4. **优化** 转换速度和成本

---

## 💡 提示

- 首次测试建议用 1-2 部小说，不要全部 60 部
- 转换过程会调用 LLM，产生费用（大约 $0.1-0.5/部）
- 审核结果保存在 `drama_data/` 下
- 所有数据可以导出到 GitHub 自动备份

---

**准备好了吗？开始转换吧！🎬**

还有问题？查看 [README.md](./README.md) 或提交 Issue
