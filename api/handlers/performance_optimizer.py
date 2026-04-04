#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能优化模块 - 并行生成、缓存、批处理
支持多阶段流程的高效执行
"""

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


class ResultCache:
    """结果缓存管理 - 避免重复调用 LLM"""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path(__file__).parent.parent.parent / "drama_data" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_key(self, novel_id: str, stage: str) -> str:
        """生成缓存键"""
        key_str = f"{novel_id}:{stage}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, novel_id: str, stage: str) -> Optional[Dict[str, Any]]:
        """从缓存读取"""
        cache_key = self._get_cache_key(novel_id, stage)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    def set(self, novel_id: str, stage: str, data: Dict[str, Any]) -> None:
        """保存到缓存"""
        cache_key = self._get_cache_key(novel_id, stage)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"缓存写入失败: {str(e)}")
    
    def clear_all(self) -> None:
        """清空所有缓存"""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)


class ParallelDramaGenerator:
    """并行短剧生成器 - 并发执行多个阶段"""
    
    def __init__(self, converter, cache: Optional[ResultCache] = None):
        self.converter = converter
        self.cache = cache or ResultCache()
    
    async def generate_drama_fast(
        self,
        novel_data: Dict[str, Any],
        novel_id: str,
        api_key: str,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """并行生成多阶段结果（快速版本）"""
        
        # 检查缓存
        final_cache_key = f"final_{novel_id}"
        if use_cache:
            cached = self.cache.get(novel_id, "full_package")
            if cached:
                print(f"💾 从缓存加载完整结果: {novel_id}")
                return cached
        
        print(f"🚀 开始并行生成: {novel_id}")
        
        # 并发生成三个分析阶段
        start_time = datetime.now()
        
        synopsis, characters, chapter_outline = await asyncio.gather(
            self._get_or_generate_synopsis(novel_data, api_key, use_cache),
            self._get_or_generate_characters(novel_data, api_key, use_cache),
            self._get_or_generate_chapters(novel_data, api_key, use_cache),
            return_exceptions=True
        )
        
        # 处理错误
        if isinstance(synopsis, Exception):
            print(f"⚠️ 简介生成失败: {str(synopsis)}")
            synopsis = {}
        if isinstance(characters, Exception):
            print(f"⚠️ 角色生成失败: {str(characters)}")
            characters = []
        if isinstance(chapter_outline, Exception):
            print(f"⚠️ 章节生成失败: {str(chapter_outline)}")
            chapter_outline = []
        
        # 然后生成剧本（基于前面的结果）
        script = await self.converter.generate_script(
            novel_data,
            novel_id,
            api_key,
            analysis={
                "synopsis": synopsis,
                "main_characters": characters,
                "chapter_outline": chapter_outline
            }
        )
        
        # 合并所有结果
        final_result = {
            "title": script.get("title"),
            "source_novel_id": novel_id,
            "source_title": novel_data.get("title"),
            "genre": script.get("genre"),
            "episodes": script.get("episodes"),
            "generated_at": datetime.now().isoformat(),
            "generation_time_ms": int((datetime.now() - start_time).total_seconds() * 1000),
            "scenes": script.get("scenes", []),
            "synopsis": synopsis,
            "main_characters": characters,
            "chapter_outline": chapter_outline
        }
        
        # 缓存完整结果
        if use_cache:
            self.cache.set(novel_id, "full_package", final_result)
        
        print(f"✅ 完成并行生成: {novel_id} ({final_result['generation_time_ms']}ms)")
        
        return final_result
    
    async def _get_or_generate_synopsis(self, novel_data, api_key, use_cache):
        """获取或生成故事简介"""
        if use_cache:
            cached = self.cache.get(novel_data.get("id"), "synopsis")
            if cached:
                return cached
        
        result = await self.converter.generate_synopsis(novel_data, api_key)
        
        if use_cache:
            self.cache.set(novel_data.get("id"), "synopsis", result)
        
        return result
    
    async def _get_or_generate_characters(self, novel_data, api_key, use_cache):
        """获取或生成角色列表"""
        if use_cache:
            cached = self.cache.get(novel_data.get("id"), "characters")
            if cached:
                return cached
        
        result = await self.converter.extract_main_characters(novel_data, api_key)
        
        if use_cache:
            self.cache.set(novel_data.get("id"), "characters", result)
        
        return result
    
    async def _get_or_generate_chapters(self, novel_data, api_key, use_cache):
        """获取或生成章节分析"""
        if use_cache:
            cached = self.cache.get(novel_data.get("id"), "chapters")
            if cached:
                return cached
        
        result = await self.converter.analyze_chapter_structure(novel_data, api_key)
        
        if use_cache:
            self.cache.set(novel_data.get("id"), "chapters", result)
        
        return result


class BatchDramaProcessor:
    """批处理优化 - 智能调度和速率限制"""

    def __init__(self, converter, max_concurrent: int = 3):
        from handlers.drama_reviewer import DramaReviewer
        from handlers.batch_manager import BatchManager
        self.converter = converter
        self.max_concurrent = max_concurrent
        self.parallel_gen = ParallelDramaGenerator(converter)
        self.sem = asyncio.Semaphore(max_concurrent)
        self._reviewer_class = DramaReviewer
        self._batch_manager_class = BatchManager
    
    async def process_novels_optimized(
        self,
        novel_ids: List[str],
        openai_key: str,
        anthropic_key: str,
        batch_id: str = "batch_001",
        skip_cache: bool = False
    ) -> List[Dict[str, Any]]:
        """优化的批处理 - 并发控制 + 缓存"""
        
        results = []
        
        # 创建受限的任务
        tasks = [
            self._process_single(novel_id, openai_key, anthropic_key, batch_id, skip_cache)
            for novel_id in novel_ids
        ]
        
        # 并发执行（受信号量限制）
        print(f"🎬 开始批处理 {len(novel_ids)} 部小说（最多 {self.max_concurrent} 个并发）")
        
        for i, task in enumerate(asyncio.as_completed(tasks), 1):
            try:
                result = await task
                results.append(result)
                print(f"[{i}/{len(novel_ids)}] ✅ {result.get('title', 'Unknown')}")
            except Exception as e:
                print(f"[{i}/{len(novel_ids)}] ❌ 处理失败: {str(e)}")
                results.append({"status": "error", "error": str(e)})
        
        return results
    
    async def _process_single(self, novel_id, openai_key, anthropic_key, batch_id, skip_cache):
        """处理单部小说"""
        async with self.sem:
            try:
                # 加载小说
                novel_data = await self.converter.load_novel(novel_id, openai_key)
                
                # 快速并行生成
                script = await self.parallel_gen.generate_drama_fast(
                    novel_data,
                    novel_id,
                    openai_key,
                    use_cache=not skip_cache
                )
                
                reviewer = self._reviewer_class()
                review = await reviewer.review_script(script, novel_id, anthropic_key)

                batch_mgr = self._batch_manager_class()
                await batch_mgr.save_drama_result(novel_id, script, review, batch_id)
                
                return {
                    "status": "success",
                    "novel_id": novel_id,
                    "title": script.get("title"),
                    "score": review.get("quality_score", 0),
                    "generation_time_ms": script.get("generation_time_ms", 0)
                }
                
            except Exception as e:
                return {
                    "status": "error",
                    "novel_id": novel_id,
                    "error": str(e)
                }


def optimize_script_storage(script: Dict[str, Any]) -> Dict[str, Any]:
    """优化剧本存储格式 - 压缩冗余字段"""
    
    optimized = {
        "id": script.get("source_novel_id"),
        "title": script.get("title"),
        "genre": script.get("genre"),
        "ts": script.get("generated_at"),  # 时间戳缩写
        "tm": script.get("generation_time_ms"),  # 生成时间
        "s": script.get("scenes"),  # scenes 缩写
        "syn": script.get("synopsis"),  # synopsis 缩写
        "chr": script.get("main_characters"),  # characters 缩写
        "ch": script.get("chapter_outline")  # chapters 缩写
    }
    
    return optimized


def decompress_script_storage(optimized: Dict[str, Any]) -> Dict[str, Any]:
    """解压缩剧本存储格式"""
    
    return {
        "source_novel_id": optimized.get("id"),
        "title": optimized.get("title"),
        "genre": optimized.get("genre"),
        "generated_at": optimized.get("ts"),
        "generation_time_ms": optimized.get("tm"),
        "scenes": optimized.get("s"),
        "synopsis": optimized.get("syn"),
        "main_characters": optimized.get("chr"),
        "chapter_outline": optimized.get("ch")
    }
