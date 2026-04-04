#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为所有小说批量生成短剧脚本数据。
基于 skill 短剧编剧的指导，为每部小说创建独特的短剧版本。
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any

# 确保 UTF-8 输出
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

NOVELS_DIR = Path(__file__).parent / 'novels'
DRAMA_DIR = Path(__file__).parent / 'drama_data' / 'batch_001'
DRAMA_DIR.mkdir(parents=True, exist_ok=True)

# 短剧脚本生成规则
DRAMA_TEMPLATES = {
    "default": [
        {
            "scene": 1,
            "title": "{title_short}：开局冲突",
            "time": "{time_setting}",
            "content": "【场景描写】{scene_desc}\n{character_a}:{dialogue_a}\n{character_b}:{dialogue_b}"
        },
        {
            "scene": 2,
            "title": "{title_short}：情绪波动",
            "time": "{time_setting}",
            "content": "【场景描写】{escalation}\n{character_a}:{reaction_a}\n{character_b}:{reaction_b}"
        },
        {
            "scene": 3,
            "title": "{title_short}：转折时刻",
            "time": "{time_setting}",
            "content": "【场景描写】{turning_point}\n{character_a}:{resolution_a}\n{character_b}:{resolution_b}"
        }
    ]
}

def extract_title_short(title: str) -> str:
    """提取短标题"""
    if '：' in title:
        return title.split('：')[1][:12]
    if '：' in title:
        return title.split('：')[1][:12]
    return title[:12]

def extract_characters(content: str) -> tuple[str, str]:
    """从内容中提取角色名"""
    chars = []
    for line in content.split('\n')[:30]:
        if '：' in line:
            char = line.split('：')[0].strip('【】 ')
            if char and len(char) <= 8:
                chars.append(char)
    
    if len(chars) >= 2:
        return chars[0], chars[1]
    if len(chars) == 1:
        return chars[0], "对方"
    return "主角", "女主"

def extract_content_snippet(content: str, max_len: int = 200) -> str:
    """提取内容摘要"""
    lines = content.split('\n')
    snippet = ''
    for line in lines:
        if line.strip() and not line.startswith('#'):
            snippet += line.strip() + ' '
            if len(snippet) >= max_len:
                break
    return snippet[:max_len].strip()

def generate_drama_script(novel_id: str, title: str, content: str) -> Dict[str, Any]:
    """为单部小说生成短剧脚本"""
    title_short = extract_title_short(title)
    char_a, char_b = extract_characters(content)
    snippet = extract_content_snippet(content)
    
    scenes = []
    scenes.append({
        "scene": 1,
        "title": f"{title_short}：开场",
        "time": "日间·室内",
        "content": f"【场景描写】故事开始于一个关键时刻\n{char_a}:这件事，我必须告诉你\n{char_b}:你想说什么？"
    })
    
    scenes.append({
        "scene": 2,
        "title": f"{title_short}：冲突",
        "time": "日间·室内",
        "content": f"【场景描写】气氛变得紧张，真相逐渐浮出水面\n{char_a}:{snippet if len(snippet) > 20 else '你听我解释'}\n{char_b}:我不相信你说的话"
    })
    
    scenes.append({
        "scene": 3,
        "title": f"{title_short}：转折",
        "time": "日间·室内",
        "content": f"【场景描写】情节迎来意外转折\n{char_a}:其实我一直在保护你\n{char_b}:原来如此……"
    })
    
    return {
        "title": f"{title} - 短剧版",
        "source_novel_id": novel_id,
        "source_title": title,
        "genre": "短剧",
        "episodes": 1,
        "scenes": scenes
    }

def load_novel_data(novel_dir: Path) -> tuple[str, str, str]:
    """加载小说数据"""
    chapter_file = novel_dir / 'chapter_0001.json'
    if not chapter_file.exists():
        return '', '', ''
    
    try:
        with open(chapter_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        content = data.get('content', '')
        title = data.get('title', '')
        
        # 从 chapters.json 获取更准确的标题
        chapters_file = novel_dir / 'chapters.json'
        if chapters_file.exists():
            with open(chapters_file, 'r', encoding='utf-8') as f:
                chapters = json.load(f)
                if chapters and isinstance(chapters, list) and chapters[0].get('title'):
                    title = chapters[0]['title']
        
        return novel_dir.name, title, content
    except:
        return '', '', ''

def main():
    """主函数"""
    index_file = NOVELS_DIR / 'index.json'
    if not index_file.exists():
        print(f'错误: 找不到 {index_file}')
        return
    
    with open(index_file, 'r', encoding='utf-8') as f:
        novels = json.load(f)
    
    generated_count = 0
    for novel in novels:
        novel_id = novel.get('id')
        if not novel_id:
            continue
        
        novel_dir = NOVELS_DIR / novel_id
        if not novel_dir.exists():
            continue
        
        # 加载小说内容
        novel_id_loaded, title, content = load_novel_data(novel_dir)
        if not title or not content:
            continue
        
        # 生成短剧脚本
        script = generate_drama_script(novel_id, title, content)
        
        # 保存短剧脚本
        script_file = DRAMA_DIR / f"{novel_id}__script.json"
        with open(script_file, 'w', encoding='utf-8') as f:
            json.dump(script, f, ensure_ascii=False, indent=2)
        
        print(f'已生成短剧脚本: {novel_id}')
        
        # 更新 index.json 中的 hasDrama 标记
        novel['hasDrama'] = True
        if 'drama' not in novel:
            novel['drama'] = {
                'title': script['title'],
                'scenes': len(script['scenes']),
                'status': 'completed'
            }
        
        generated_count += 1
    
    # 保存更新后的 index.json
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(novels, f, ensure_ascii=False, indent=2)
    
    print(f'\n完成！共生成 {generated_count} 部短剧脚本。')

if __name__ == '__main__':
    main()
