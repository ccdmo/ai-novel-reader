#!/bin/bash
# 部署脚本 - 一键部署到 AWS Lambda

set -e

echo "🚀 开始部署 AI 小说剧本转换服务..."

# 1. 验证环境变量
if [ -z "$AWS_REGION" ]; then
    echo "❌ 错误: 未设置 AWS_REGION"
    exit 1
fi

if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  警告: 未设置 GITHUB_TOKEN，GitHub 上传功能将被禁用"
fi

# 2. 创建 Lambda 部署包
echo "📦 正在创建部署包..."
cd api
mkdir -p build
pip install -r requirements.txt -t build/
cp main.py build/
cp -r handlers build/

# 3. 打包为 ZIP
cd build
zip -r ../lambda_deployment.zip . -x "*.git*"
cd ../..

echo "✅ 部署包创建完成"

# 4. 更新 Lambda 函数
echo "🔄 更新 Lambda 函数..."
aws lambda update-function-code \
    --function-name ai-novel-drama-converter \
    --zip-file fileb://api/lambda_deployment.zip \
    --region $AWS_REGION

# 5. 设置环境变量
echo "⚙️  设置环境变量..."
aws lambda update-function-configuration \
    --function-name ai-novel-drama-converter \
    --environment Variables="{GITHUB_TOKEN=$GITHUB_TOKEN,OPENAI_API_KEY=$OPENAI_API_KEY,ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY}" \
    --region $AWS_REGION

# 6. 验证部署
echo "✔️  验证部署..."
sleep 5
curl -s -X GET "https://your-api-gateway-url/health" | jq '.'

echo "✅ 部署完成！"
echo "API 地址：https://your-api-gateway-url"
