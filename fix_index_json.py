#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新生成干净的 index.json
"""

import json
import re
from pathlib import Path

def get_novel_title_from_content(novel_dir):
    """从 chapter_0001.json 中提取小说标题"""
    chapter_file = novel_dir / 'chapter_0001.json'
    if not chapter_file.exists():
        return novel_dir.name
    try:
        with open(chapter_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            content = data.get('content', '')
            if content:
                lines = content.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('# 《') and '》' in line:
                        match = re.search(r'# 《([^》]+)》', line)
                        if match:
                            return match.group(1)
                    elif line.startswith('《') and '》' in line:
                        match = re.search(r'《([^》]+)》', line)
                        if match:
                            return match.group(1)
                    elif line.startswith('## ') or line.startswith('# '):
                        title = line.lstrip('#').strip()
                        if len(title) > 2 and len(title) < 50:
                            return title
        return novel_dir.name
    except:
        return novel_dir.name

def extract_chapter_title(content):
    """从章节内容中提取标题"""
    if not content:
        return None
    lines = content.strip().split('\n')
    for line in lines[:10]:
        line = line.strip()
        if line.startswith('<think>') or line.startswith('```') or line.startswith('【'):
            continue
        if line.startswith('## ') and len(line) > 4:
            return line[3:].strip()
        elif line.startswith('# 《') and '》' in line:
            match = re.search(r'# 《([^》]+)》', line)
            if match:
                return match.group(1)
        elif line.startswith('# ') and len(line) > 4:
            title = line[2:].strip()
            if not title.startswith('<think>') and not title.startswith('【'):
                return title
    return None

def clean_content(content):
    """清理内容中的AI思考标记"""
    if not content:
        return content
    content = re.sub(r'<think>[\s\S]*?「</think>', '', content)
    content = re.sub(r'```[\s\S]*?```', '', content)
    return content

def main():
    novels_dir = Path('d:/003_True_Code/0.6小说Agent/ai-novel-reader/novels')

    novels = []

    for novel_dir in sorted(novels_dir.iterdir()):
        if not novel_dir.is_dir() or novel_dir.name.startswith('.'):
            continue

        novel_id = novel_dir.name
        chapter_files = sorted(novel_dir.glob('chapter_*.json'))

        if not chapter_files:
            continue

        title = get_novel_title_from_content(novel_dir)

        chapters = []
        for i, cf in enumerate(chapter_files):
            try:
                with open(cf, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                num = data.get('num') or data.get('number') or (i + 1)
                raw_content = data.get('content', '')
                clean = clean_content(raw_content)
                ch_title = data.get('title', '').lstrip('#').strip()
                if not ch_title:
                    ch_title = extract_chapter_title(clean) or f'第{num}章'

                chapters.append({
                    'num': num,
                    'title': ch_title,
                    'status': data.get('status', 'done'),
                    'words': data.get('words') or data.get('wordCount') or 0
                })
            except Exception as e:
                print(f"  警告: 处理 {cf.name} 时出错: {e}")
                chapters.append({
                    'num': i + 1,
                    'title': f'第{i+1}章',
                    'status': 'done',
                    'words': 0
                })

        done_count = len([c for c in chapters if c.get('status') == 'done'])
        desc = f"共 {done_count} 章" if done_count > 0 else "章节待生成"

        novel = {
            'id': novel_id,
            'title': title,
            'slug': novel_id,
            'desc': desc,
            'author': 'AI（MiniMax仿写）',
            'genre': '都市/玄幻',
            'heat': 0,
            'status': 'completed' if done_count == len(chapters) else 'writing',
            'cover': '📖',
            'chapters': chapters
        }

        novels.append(novel)
        print(f"✓ {novel_id}: {title} ({len(chapters)}章)")

    index_file = novels_dir / 'index.json'
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(novels, f, ensure_ascii=False, indent=2)

    print(f"\n共生成 {len(novels)} 部小说的索引")

if __name__ == '__main__':
    main()
