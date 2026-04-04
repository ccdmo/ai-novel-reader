#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI 后端应用 - 支持 Lambda 和本地运行
处理小说转剧本、AI 审核、批次管理
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel
import httpx
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from handlers.drama_converter import DramaConverter
from handlers.drama_reviewer import DramaReviewer
from handlers.batch_manager import BatchManager
from handlers.github_storage import GitHubStorage

# 初始化应用
app = FastAPI(
    title="AI小说创意平台 - 后端服务",
    description="将小说转换为短剧剧本，支持 AI 审核和批处理",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ccdmo.github.io",
        "localhost:3000",
        "127.0.0.1:3000",
        "http://localhost:8000",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化处理器
converter = DramaConverter()
reviewer = DramaReviewer()
batch_mgr = BatchManager()
github_storage = GitHubStorage()

# 数据模型
class ConvertRequest(BaseModel):
    novel_id: str
    batch_id: str = "batch_001"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    conversion_prompt: Optional[str] = None
    review_prompt: Optional[str] = None

class ApprovalRequest(BaseModel):
    batch_id: str = "batch_001"
    notes: str = ""

# 封面生成与上传配置
NOVEL_INDEX_PATH = Path(__file__).resolve().parent.parent / "novels" / "index.json"
COVERS_DIR = Path(__file__).resolve().parent.parent / "novels" / "covers"
COVERS_DIR.mkdir(parents=True, exist_ok=True)
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_IMAGE_MODEL = os.getenv("MINIMAX_IMAGE", "MiniMax-Image-01")
MINIMAX_IMAGE_ENDPOINT = os.getenv("MINIMAX_IMAGE_ENDPOINT", "https://api.minimax.chat/v1/image_generation")

class CoverGenerateRequest(BaseModel):
    novel_id: str
    prompt: Optional[str] = None

class CoverBulkGenerateRequest(BaseModel):
    novel_ids: List[str]


def load_novel_index():
    with NOVEL_INDEX_PATH.open('r', encoding='utf-8') as f:
        return json.load(f)


def save_novel_index(data):
    with NOVEL_INDEX_PATH.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def find_novel(novel_id, index_data):
    return next((item for item in index_data if item.get('id') == novel_id or item.get('slug') == novel_id), None)


def safe_filename(value: str) -> str:
    return re.sub(r'[^0-9A-Za-z\u4e00-\u9fa5\-_. ]+', '_', value).strip().replace(' ', '_')


async def fetch_minimax_cover(prompt: str) -> str:
    if not MINIMAX_API_KEY:
        raise ValueError('Minimax API Key 未配置，请在环境变量中设置 MINIMAX_API_KEY。')

    payload = {
        'model': MINIMAX_IMAGE_MODEL,
        'prompt': prompt,
        'size': '1024x1024'
    }
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(MINIMAX_IMAGE_ENDPOINT, json=payload, headers={
            'Authorization': f'Bearer {MINIMAX_API_KEY}'
        })
        response.raise_for_status()
        data = response.json()

    if isinstance(data, dict) and data.get('data') and isinstance(data['data'], list) and data['data'][0].get('url'):
        return data['data'][0]['url']
    if isinstance(data, dict) and data.get('images') and isinstance(data['images'], list) and data['images'][0].get('url'):
        return data['images'][0]['url']
    raise ValueError(f'无法从 Minimax 响应中解析封面 URL：{data}')


def build_cover_prompt(novel):
    title = novel.get('title', '未知小说')
    genre = novel.get('genre', '现代小说')
    return f'为中文小说《{title}》生成一张高质量中文封面，风格适合{genre}，包含书名，色调丰富，适合小说推广。'

# ============= 健康检查 =============
@app.get("/")
async def root():
    return {
        "service": "AI Novel Drama Converter",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# ============= 封面生成与上传 =============
@app.post("/api/cover/generate")
async def generate_cover(request: CoverGenerateRequest):
    try:
        index_data = load_novel_index()
        novel = find_novel(request.novel_id, index_data)
        if not novel:
            raise HTTPException(status_code=404, detail="小说未找到")

        prompt = request.prompt or build_cover_prompt(novel)
        cover_url = await fetch_minimax_cover(prompt)
        novel['cover'] = cover_url
        save_novel_index(index_data)
        return {"novel_id": request.novel_id, "cover": cover_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cover/generate/bulk")
async def generate_bulk_cover(request: CoverBulkGenerateRequest):
    try:
        index_data = load_novel_index()
        updated = []
        for novel_id in request.novel_ids:
            novel = find_novel(novel_id, index_data)
            if not novel:
                continue
            if novel.get('cover') and (novel['cover'].startswith('http://') or novel['cover'].startswith('https://') or novel['cover'].startswith('data:image') or novel['cover'].startswith('novels/')):
                continue
            prompt = build_cover_prompt(novel)
            cover_url = await fetch_minimax_cover(prompt)
            novel['cover'] = cover_url
            updated.append({"novel_id": novel_id, "cover": cover_url})

        if updated:
            save_novel_index(index_data)
        return {"updated": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cover/upload")
async def upload_cover(novel_id: str = Form(...), file: UploadFile = File(...)):
    try:
        index_data = load_novel_index()
        novel = find_novel(novel_id, index_data)
        if not novel:
            raise HTTPException(status_code=404, detail="小说未找到")

        ext = Path(file.filename).suffix.lower() or '.png'
        if ext not in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
            ext = '.png'
        filename = f"{safe_filename(novel_id)}{ext}"
        target_path = COVERS_DIR / filename
        with target_path.open('wb') as f:
            f.write(await file.read())

        relative_cover = f"novels/covers/{filename}"
        novel['cover'] = relative_cover
        save_novel_index(index_data)
        return {"novel_id": novel_id, "cover": relative_cover}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= 小说转剧本 =============
@app.post("/api/drama/convert")
async def convert_novel_to_drama(request: ConvertRequest, background_tasks: BackgroundTasks):
    """
    将单部小说转换为短剧剧本
    
    流程：
    1. 读取小说内容
    2. 使用 LLM 生成剧本
    3. AI 审核
    4. 保存到 GitHub（后台）
    """
    try:
        novel_id = request.novel_id
        batch_id = request.batch_id
        
        # 使用提交的 API Key，或者回退到环境变量
        openai_key = request.openai_api_key or os.getenv("OPENAI_API_KEY", "")
        anthropic_key = request.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY", "")
        
        if not openai_key:
            raise ValueError("OpenAI API Key 未提供")
        if not anthropic_key:
            raise ValueError("Anthropic API Key 未提供")
        
        # 1. 读取小说数据
        novel_content = await converter.load_novel(novel_id, openai_key)
        
        # 2. 生成短剧剧本
        script = await converter.generate_drama_package(
            novel_content,
            novel_id,
            openai_key,
            prompt_override=request.conversion_prompt
        )
        
        # 3. AI 审核
        review = await reviewer.review_script(
            script,
            novel_id,
            anthropic_key,
            request.review_prompt
        )
        
        # 4. 保存结果
        result = await batch_mgr.save_drama_result(
            novel_id, script, review, batch_id
        )
        
        # 5. 后台上传到 GitHub
        background_tasks.add_task(
            github_storage.save_drama,
            novel_id, batch_id, script, review
        )
        
        return {
            "status": "success",
            "novel_id": novel_id,
            "score": review.get("quality_score", 0),
            "review_notes": review.get("summary", ""),
            "script_url": f"/drama-data/{batch_id}/{novel_id}_script.json",
            "synopsis": script.get("synopsis"),
            "main_characters": script.get("main_characters"),
            "chapter_outline": script.get("chapter_outline"),
            "created_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")

# ============= 批次管理 =============
@app.get("/api/drama/batch/{batch_id}")
async def get_batch_status(batch_id: str):
    """获取批次转换进度"""
    try:
        batch_data = await batch_mgr.get_batch_status(batch_id)
        return batch_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/drama/batch")
async def create_batch(batch_id: str, novels_count: int = 5):
    """创建新批次"""
    try:
        batch = await batch_mgr.create_batch(batch_id, novels_count)
        return batch
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= 审核管理 =============
@app.get("/api/drama/audit-list")
async def get_audit_list(batch_id: str = "batch_001", status: Optional[str] = None):
    """获取待审核的剧本列表"""
    try:
        audits = await batch_mgr.get_audit_list(batch_id, status)
        return audits
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/drama/approve/{novel_id}")
async def approve_drama(novel_id: str, request: ApprovalRequest):
    """审核批准"""
    try:
        result = await batch_mgr.update_approval_status(
            novel_id, "approved", request.batch_id, request.notes
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/drama/reject/{novel_id}")
async def reject_drama(novel_id: str, request: ApprovalRequest):
    """审核拒绝"""
    try:
        result = await batch_mgr.update_approval_status(
            novel_id, "rejected", request.batch_id, request.notes
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= 查询接口 =============
@app.get("/api/drama/{novel_id}")
async def get_drama_detail(novel_id: str, batch_id: str = "batch_001"):
    """获取单部剧本详情"""
    try:
        drama = await batch_mgr.get_drama_detail(novel_id, batch_id)
        return drama
    except Exception as e:
        raise HTTPException(status_code=404, detail="剧本不存在")

# ============= 统计信息 =============
@app.get("/api/stats")
async def get_stats(batch_id: str = "batch_001"):
    """获取转换统计信息"""
    try:
        stats = await batch_mgr.get_batch_stats(batch_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Lambda 入口（生产环境）
handler = Mangum(app)

# 本地调试入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
