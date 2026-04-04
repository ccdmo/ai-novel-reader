#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将所有英文目录名和路由改为中文
根据 novels/index.json 中的 title 字段进行重命名
"""

import json
import os
import shutil
from pathlib import Path
import re

def extract_chinese_name(title):
    """从 title 提取简洁的中文名称"""
    # 去掉 "第X章" 开头
    title = re.sub(r'^第\d+章\s*', '', title)
    
    # 保留前 20 个字符（一般足够了）
    if len(title) > 20:
        # 找到合适的断点，不要在中间截断词语
        title = title[:20]
    
    # 替换特殊字符使其可以作为文件夹名
    title = title.replace('/', '').replace('\\', '').replace(':', '').replace('?', '')
    title = title.replace('*', '').replace('|', '').replace('"', '').replace('<', '').replace('>', '')
    
    return title.strip()

def main():
    novels_dir = Path('novels')
    
    # 读取 index.json
    with open(novels_dir / 'index.json', 'r', encoding='utf-8') as f:
        novels_data = json.load(f)
    
    # 创建映射表：old_id → new_id
    rename_map = {}
    
    print("开始重命名文件夹和更新 ID...")
    print("=" * 60)
    
    for novel in novels_data:
        old_id = novel['id']
        old_slug = novel['slug']
        title = novel['title']
        
        # 生成新的中文 ID 
        new_id = extract_chinese_name(title)
        
        rename_map[old_id] = new_id
        
        old_path = novels_dir / old_id
        new_path = novels_dir / new_id
        
        # 检查目录是否存在
        if not old_path.exists():
            print(f"⚠️  {old_id} 目录不存在，跳过")
            continue
        
        # 如果新路径已存在，跳过
        if new_path.exists():
            print(f"✓  {old_id} → {new_id} (已存在)")
            continue
        
        # 重命名目录
        try:
            shutil.move(str(old_path), str(new_path))
            print(f"✓  {old_id} → {new_id}")
        except Exception as e:
            print(f"✗  重命名失败 {old_id}: {e}")
            continue
    
    print("=" * 60)
    print("更新 novels/index.json ...")
    
    # 更新 index.json 中的 id 和 slug
    for novel in novels_data:
        old_id = novel['id']
        if old_id in rename_map:
            new_id = rename_map[old_id]
            novel['id'] = new_id
            novel['slug'] = new_id
    
    # 保存更新后的 index.json
    with open(novels_dir / 'index.json', 'w', encoding='utf-8') as f:
        json.dump(novels_data, f, ensure_ascii=False, indent=2)
    
    print("✓  novels/index.json 已更新")
    
    # 生成映射表用于前端更新
    print("\n" + "=" * 60)
    print("映射关系（用于参考）：")
    print("=" * 60)
    for old_id, new_id in sorted(rename_map.items()):
        if old_id != new_id:
            print(f"{old_id:<30} → {new_id}")
    
    print("\n✅ 完成！")
    print("\n📝 接下来需要手动更新的地方：")
    print("   1. 检查 index.html 中的路由引用")
    print("   2. 检查 API 中的路由引用")
    print("   3. 运行 git status 查看变更")

if __name__ == '__main__':
    main()
