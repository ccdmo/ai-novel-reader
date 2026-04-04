#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用 Minimax 生成小说封面图，并把封面 URL 写回 novels/index.json。"""

import json
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).parent.resolve()
INDEX_FILE = ROOT / 'novels' / 'index.json'
MINIMAX_API_KEY = os.getenv('MINIMAX_API_KEY')
MINIMAX_MODEL = os.getenv('MINIMAX_IMAGE', 'MiniMax-Image-01')
MINIMAX_ENDPOINT = os.getenv('MINIMAX_IMAGE_ENDPOINT', 'https://api.minimax.chat/v1/image_generation')

if not MINIMAX_API_KEY:
    print('请先在环境变量中设置 MINIMAX_API_KEY。', file=sys.stderr)
    sys.exit(1)

if not INDEX_FILE.exists():
    print(f'找不到小说索引文件：{INDEX_FILE}', file=sys.stderr)
    sys.exit(1)


def build_prompt(novel: dict) -> str:
    title = novel.get('title') or novel.get('id') or '小说'
    desc = novel.get('desc', '')
    genre = novel.get('genre', '现代玄幻')
    return (
        f'为小说《{title}》生成一张高清封面图，'
        f'风格适合{genre}类型小说。'
        f'封面应简洁、色彩鲜明，突出故事氛围。'
        f'{desc} 如果没有描述，则只需强调小说标题与气质。'
        f' 输出效果适合用作网页或短剧封面。'
    )


def generate_cover_url(prompt: str) -> str:
    headers = {
        'Authorization': f'Bearer {MINIMAX_API_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        'model': MINIMAX_MODEL,
        'prompt': prompt,
        'aspect_ratio': '1:1',
    }
    resp = requests.post(MINIMAX_ENDPOINT, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    images = data.get('data', {}).get('images')
    if not images or not isinstance(images, list):
        raise ValueError(f'无法从 Minimax 响应中解析 images：{data}')
    url = images[0].get('url')
    if not url:
        raise ValueError(f'响应未返回图片 URL：{data}')
    return url


def main():
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        novels = json.load(f)

    updated = False
    for novel in novels:
        cover = novel.get('cover', '')
        if isinstance(cover, str) and cover.startswith(('http://', 'https://', 'data:image')):
            print(f'已存在封面 URL，跳过：{novel.get("id") or novel.get("title")}')
            continue

        if cover and cover != '📖':
            print(f'当前封面为文本，仍将生成图片：{novel.get("id") or novel.get("title")}')
        else:
            print(f'生成封面：{novel.get("id") or novel.get("title")}')

        prompt = build_prompt(novel)
        try:
            url = generate_cover_url(prompt)
            novel['cover'] = url
            print(f'  -> 封面 URL: {url}')
            updated = True
        except Exception as exc:
            print(f'  生成失败：{exc}', file=sys.stderr)
        time.sleep(1)

    if updated:
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(novels, f, ensure_ascii=False, indent=2)
        print(f'已更新 {INDEX_FILE}')
    else:
        print('未检测到需要更新的封面。')


if __name__ == '__main__':
    main()
