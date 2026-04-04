#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量将小说转换为短剧剧本，并将结果保存到 drama_data/batch_001。

使用方法：
  python convert_all_novels_to_drama.py --openai YOUR_OPENAI_KEY --anthropic YOUR_ANTHROPIC_KEY
  
性能优化选项：
  --fast              启用快速并行生成
  --concurrent NUM    设置最大并发数（默认3）
  --skip-cache        跳过缓存，重新生成所有内容

生成完成后，可运行 generate_drama_pages.py 为每部小说创建 drama.html 页面。
"""

import argparse
import asyncio
import json
from pathlib import Path
from typing import List

from api.handlers.drama_converter import DramaConverter
from api.handlers.drama_reviewer import DramaReviewer
from api.handlers.batch_manager import BatchManager
from api.handlers.performance_optimizer import ParallelDramaGenerator, BatchDramaProcessor

ROOT = Path(__file__).parent.resolve()
NOVELS_DIR = ROOT / 'novels'
DRAMA_DIR = ROOT / 'drama_data' / 'batch_001'
DRAMA_DIR.mkdir(parents=True, exist_ok=True)


async def convert_novels(novel_ids: List[str], openai_key: str, anthropic_key: str, batch_id: str = 'batch_001', use_fast: bool = False, max_concurrent: int = 3, skip_cache: bool = False):
    """
    批量转换小说为短剧。
    
    Args:
        novel_ids: 小说ID列表
        openai_key: OpenAI API密钥
        anthropic_key: Anthropic API密钥
        batch_id: 批次ID
        use_fast: 启用快速并行模式
        max_concurrent: 最大并发数
        skip_cache: 跳过缓存
    """
    converter = DramaConverter()
    reviewer = DramaReviewer()
    batch_manager = BatchManager()

    await batch_manager.create_batch(batch_id, len(novel_ids))

    if use_fast:
        # 使用批处理器快速生成
        processor = BatchDramaProcessor(converter, max_concurrent)
        results = await processor.process_novels_optimized(novel_ids, skip_cache=skip_cache)
        
        # 保存所有结果
        for novel_id, result in results.items():
            if result.get("status") == "success":
                script = result.get("script")
                review = await reviewer.review_script(script, novel_id, anthropic_key)
                saved = await batch_manager.save_drama_result(novel_id, script, review, batch_id)
                print(f'已保存：{saved.get("script_url")}')
            else:
                print(f'转换失败: {novel_id} -> {result.get("error")}')
    else:
        # 顺序转换
        for novel_id in novel_ids:
            print('-----')
            print(f'开始转换: {novel_id}')
            try:
                novel_data = await converter.load_novel(novel_id, openai_key)
                script = await converter.generate_drama_package(novel_data, novel_id, openai_key)
                review = await reviewer.review_script(script, novel_id, anthropic_key)
                result = await batch_manager.save_drama_result(novel_id, script, review, batch_id)
                print(f'已保存：{result.get("script_url")}')
            except Exception as exc:
                print(f'转换失败: {novel_id} -> {exc}')

    print('批量转换完成。')


def load_novels_index() -> List[str]:
    index_file = NOVELS_DIR / 'index.json'
    if not index_file.exists():
        raise FileNotFoundError(f'找不到 {index_file}')
    with open(index_file, 'r', encoding='utf-8') as f:
        novels = json.load(f)
    return [novel.get('id') for novel in novels if novel.get('id')]


def parse_args():
    parser = argparse.ArgumentParser(description='批量将小说转换为短剧剧本并保存到 drama_data/batch_001')
    parser.add_argument('--openai', help='OpenAI API Key', required=False)
    parser.add_argument('--anthropic', help='Anthropic API Key', required=False)
    parser.add_argument('--batch-id', default='batch_001', help='批次 ID (默认 batch_001)')
    parser.add_argument('--novels', nargs='*', help='仅转换指定小说 ID（默认为全部）')
    parser.add_argument('--fast', action='store_true', help='启用快速并行生成模式')
    parser.add_argument('--concurrent', type=int, default=3, help='最大并发数（默认 3）')
    parser.add_argument('--skip-cache', action='store_true', help='跳过缓存，强制重新生成所有内容')
    return parser.parse_args()


def main():
    args = parse_args()
    openai_key = args.openai or ''
    anthropic_key = args.anthropic or ''

    if not openai_key or not anthropic_key:
        print('需要提供 OpenAI 和 Anthropic API Key。可使用 --openai 和 --anthropic 参数。')
        return

    if args.novels:
        novel_ids = args.novels
    else:
        novel_ids = load_novels_index()

    asyncio.run(convert_novels(
        novel_ids, 
        openai_key, 
        anthropic_key, 
        args.batch_id,
        use_fast=args.fast,
        max_concurrent=args.concurrent,
        skip_cache=args.skip_cache
    ))


if __name__ == '__main__':
    main()
