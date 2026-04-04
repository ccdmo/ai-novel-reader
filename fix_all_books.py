#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复小说阅读器的 index.html 模板和 index.json 数据
统一所有小说页面格式
"""

import os
import re
import json
from pathlib import Path

# 统一的小说详情页 index.html 模板
INDEX_HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - AI 小说阅读器</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f5f5f5;color:#333}}
a{{color:#667eea;text-decoration:none}}
a:hover{{text-decoration:underline}}
.header{{background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:1rem 2rem;display:flex;align-items:center;justify-content:space-between}}
.header-left{{display:flex;align-items:center;gap:1rem}}
.back-btn{{background:rgba(255,255,255,0.2);color:white;padding:0.4rem 0.8rem;border-radius:6px;font-size:0.85rem;border:none;cursor:pointer}}
.back-btn:hover{{background:rgba(255,255,255,0.3);text-decoration:none}}
.header h1{{font-size:1.2rem;font-weight:600}}
.main{{display:flex;max-width:1200px;margin:0 auto;min-height:calc(100vh - 60px)}}
.sidebar{{width:240px;background:white;border-right:1px solid #eee;padding:1rem 0;overflow-y:auto;position:sticky;top:60px;height:calc(100vh - 60px)}}
.sidebar-title{{padding:0.5rem 1rem;font-size:0.75rem;color:#999;text-transform:uppercase;letter-spacing:1px}}
.chapter-list{{list-style:none}}
.chapter-item a{{display:block;padding:0.6rem 1rem;font-size:0.9rem;color:#333;transition:background 0.15s}}
.chapter-item a:hover{{background:#f5f5f5;text-decoration:none}}
.chapter-item.active a{{background:#e8f0fe;color:#4285f4;border-left:3px solid #4285f4}}
.content-area{{flex:1;padding:2rem 3rem;background:white;max-width:800px}}
.novel-title{{font-size:1.8rem;font-weight:700;margin-bottom:0.5rem}}
.novel-meta{{font-size:0.85rem;color:#999;margin-bottom:2rem;padding-bottom:1rem;border-bottom:1px solid #eee}}
.chapter-title{{font-size:1.4rem;font-weight:600;margin-bottom:1.5rem;padding-bottom:0.5rem;border-bottom:2px solid #667eea;display:inline-block}}
.chapter-content{{font-size:1.05rem;line-height:1.9;color:#333}}
.chapter-content p{{margin-bottom:1.2rem;text-indent:2em}}
.chapter-content h2{{font-size:1.3rem;margin:1.5rem 0 1rem;border-bottom:1px solid #eee;padding-bottom:0.5rem}}
.chapter-content h3{{font-size:1.1rem;margin:1.2rem 0 0.8rem}}
.nav-btns{{display:flex;justify-content:space-between;margin-top:3rem;padding-top:2rem;border-top:1px solid #eee}}
.nav-btn{{background:#667eea;color:white;padding:0.6rem 1.2rem;border-radius:6px;font-size:0.9rem;border:none;cursor:pointer}}
.nav-btn:hover{{background:#5568d3}}
.nav-btn:disabled{{background:#ccc;cursor:not-allowed}}
@media(max-width:768px){{
  .main{{flex-direction:column}}
  .sidebar{{width:100%;height:auto;position:relative;top:0;border-right:none;border-bottom:1px solid #eee}}
  .content-area{{padding:1.5rem 1rem}}
}}
</style>
</head>
<body>
<div class="header">
  <div class="header-left">
    <a href="../../" class="back-btn">← 返回列表</a>
    <h1>{title}</h1>
  </div>
  <div style="font-size:0.85rem;opacity:0.8;">AI 创作</div>
</div>
<div class="main">
  <aside class="sidebar">
    <div class="sidebar-title">目录</div>
    <ul class="chapter-list" id="chapterList"></ul>
  </aside>
  <main class="content-area" id="contentArea">
    <div style="padding:2rem;text-align:center;color:#999">加载中...</div>
  </main>
</div>
<script>
var CHAPTERS = {chapters_json};
var BOOK_ID = "{book_id}";

function getChapterFile(idx) {{
  var ch = CHAPTERS[idx];
  if (ch.file) return ch.file;
  return 'chapter_' + String(idx+1).padStart(4,'0') + '.json';
}}

function parseContent(content) {{
  if (!content) return '<p style="color:#999;text-align:center">暂无内容</p>';
  content = content.trim();
  var html = '';
  var lines = content.split('\\n');
  var inParagraph = false;
  var paragraphBuffer = [];

  function flushParagraph() {{
    if (paragraphBuffer.length > 0) {{
      html += '<p>' + paragraphBuffer.join('') + '</p>';
      paragraphBuffer = [];
    }}
    inParagraph = false;
  }}

  for (var i = 0; i < lines.length; i++) {{
    var line = lines[i].trim();
    if (!line) {{
      flushParagraph();
      continue;
    }}
    if (line.startsWith('## ')) {{
      flushParagraph();
      html += '<h2>' + line.substring(3) + '</h2>';
    }} else if (line.startsWith('# ')) {{
      flushParagraph();
      html += '<h2>' + line.substring(2) + '</h2>';
    }} else if (line.startsWith('【') && line.endsWith('】')) {{
      flushParagraph();
      html += '<p style="color:#667eea;font-weight:500">' + line + '</p>';
    }} else {{
      inParagraph = true;
      paragraphBuffer.push(line);
    }}
  }}
  flushParagraph();
  return html;
}}

function renderChapterList() {{
  var html = CHAPTERS.map(function(ch, i) {{
    var title = ch.title || '第' + (ch.num || ch.number || i+1) + '章';
    var wordCount = ch.words || ch.wordCount || 0;
    return '<li class="chapter-item"><a href="?c=' + i + '">' + title + '</a></li>';
  }}).join('');
  document.getElementById('chapterList').innerHTML = html;
}}

function renderChapter(idx) {{
  var ch = CHAPTERS[idx];
  var title = ch.title || '第' + (ch.num || ch.number || idx+1) + '章';

  document.querySelectorAll('.chapter-item').forEach(function(el, i) {{
    el.classList.toggle('active', i === idx);
  }});

  var xhr = new XMLHttpRequest();
  xhr.open('GET', getChapterFile(idx), true);
  xhr.onload = function() {{
    try {{
      var data = JSON.parse(xhr.responseText);
      var content = parseContent(data.content);
      var prev = idx > 0 ? '<button class="nav-btn" onclick="renderChapter(' + (idx-1) + ')">← 上一章</button>' : '<button class="nav-btn" disabled>← 上一章</button>';
      var next = idx < CHAPTERS.length - 1 ? '<button class="nav-btn" onclick="renderChapter(' + (idx+1) + ')">下一章 →</button>' : '<button class="nav-btn" disabled>下一章 →</button>';
      document.getElementById('contentArea').innerHTML =
        '<h1 class="chapter-title">' + title + '</h1>' +
        '<div class="chapter-content">' + content + '</div>' +
        '<div class="nav-btns">' + prev + next + '</div>';
    }} catch(e) {{
      document.getElementById('contentArea').innerHTML = '<div style="color:red;padding:2rem">加载失败: ' + e.message + '</div>';
    }}
    window.scrollTo(0, 0);
  }};
  xhr.onerror = function() {{
    document.getElementById('contentArea').innerHTML = '<div style="color:#999;padding:2rem">章节文件不存在</div>';
  }};
  xhr.send();
}}

var params = new URLSearchParams(location.search);
var c = params.get("c");
renderChapterList();
if (c !== null) {{
  var idx = parseInt(c);
  if (idx >= 0 && idx < CHAPTERS.length) {{
    renderChapter(idx);
  }} else {{
    renderChapter(0);
  }}
}} else {{
  renderChapter(0);
}}
</script>
</body>
</html>
'''


def get_novel_title_from_content(novel_dir):
    """从 chapter_0001.json 中提取小说标题"""
    chapter_file = novel_dir / 'chapter_0001.json'
    if not chapter_file.exists():
        return None
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
        return None
    except:
        return None


def extract_chapter_title(content):
    """从章节内容中提取标题"""
    if not content:
        return None
    lines = content.strip().split('\n')
    for line in lines[:10]:
        line = line.strip()
        # 跳过AI思考标记
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
    # 移除<think>...「</think>」模式
    content = re.sub(r'<think>[\s\S]*?「</think>', '', content)
    # 移除 ```...``` 代码块
    content = re.sub(r'```[\s\S]*?```', '', content)
    return content


def fix_chapters_json(novel_dir, novel_id):
    """修复章节信息"""
    chapters_file = novel_dir / 'chapters.json'
    chapter_files = sorted(novel_dir.glob('chapter_*.json'))

    chapters = []
    for i, cf in enumerate(chapter_files):
        try:
            with open(cf, 'r', encoding='utf-8') as f:
                data = json.load(f)

            num = data.get('num') or data.get('number') or (i + 1)
            title = data.get('title', '')

            # 清理标题中的 Markdown 标记
            title = title.lstrip('#').strip()

            # 尝试从内容中提取标题
            raw_content = data.get('content', '')
            clean = clean_content(raw_content)
            if not title or title.startswith('#'):
                title = extract_chapter_title(clean) or f'第{num}章'

            word_count = data.get('words') or data.get('wordCount') or 0
            status = data.get('status', 'done')

            chapters.append({
                'num': num,
                'title': title,
                'status': status,
                'words': word_count,
                'file': cf.name
            })
        except Exception as e:
            print(f"  警告: 处理 {cf.name} 时出错: {e}")
            chapters.append({
                'num': i + 1,
                'title': f'第{i+1}章',
                'status': 'done',
                'words': 0,
                'file': cf.name
            })

    # 写入 chapters.json
    with open(chapters_file, 'w', encoding='utf-8') as f:
        json.dump(chapters, f, ensure_ascii=False, indent=2)

    return chapters


def fix_index_html(novel_dir, novel_id, title, chapters):
    """修复单个小说的 index.html"""
    chapters_json = json.dumps(chapters, ensure_ascii=False)

    html_content = INDEX_HTML_TEMPLATE.format(
        title=title,
        book_id=novel_id,
        chapters_json=chapters_json
    )

    index_file = novel_dir / 'index.html'
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return True


def get_novel_title(novel_dir, novel_id):
    """获取小说标题，优先从 index.json 获取，否则从内容中提取"""
    novels_index = novel_dir.parent / 'index.json'

    # 尝试从 novels/index.json 获取
    if novels_index.exists():
        try:
            with open(novels_index, 'r', encoding='utf-8') as f:
                novels = json.load(f)
            for n in novels:
                if n.get('id') == novel_id:
                    t = n.get('title', '')
                    if t and not t.startswith('📖'):
                        return t
        except:
            pass

    # 从 chapter_0001.json 提取
    title = get_novel_title_from_content(novel_dir)
    if title:
        return title

    # 使用目录名
    return novel_id


def fix_novel(novel_dir):
    """修复单个小说"""
    novel_id = novel_dir.name

    # 修复 chapters.json
    chapters = fix_chapters_json(novel_dir, novel_id)

    # 获取标题
    title = get_novel_title(novel_dir, novel_id)

    # 修复 index.html
    fix_index_html(novel_dir, novel_id, title, chapters)

    return title, len(chapters)


def fix_main_index_json():
    """修复主 index.json 文件"""
    novels_dir = Path('d:/003_True_Code/0.6小说Agent/ai-novel-reader/novels')
    index_file = novels_dir / 'index.json'

    if not index_file.exists():
        print("index.json 不存在")
        return

    with open(index_file, 'r', encoding='utf-8') as f:
        novels = json.load(f)

    fixed_count = 0
    for novel in novels:
        novel_id = novel.get('id')
        if not novel_id:
            continue

        novel_dir = novels_dir / novel_id
        if not novel_dir.exists():
            continue

        # 获取正确标题
        title = get_novel_title(novel_dir, novel_id)

        # 获取章节数
        chapters = list(novel_dir.glob('chapter_*.json'))
        chapter_count = len(chapters)

        # 修复 title
        if novel.get('title', '').startswith('📖') or novel.get('title', '') != title:
            novel['title'] = title
            fixed_count += 1

        # 修复 desc
        if novel.get('desc', '').startswith('共') or '章' not in novel.get('desc', ''):
            novel['desc'] = f"共 {chapter_count} 章" if chapter_count > 0 else "章节待生成"
            fixed_count += 1

        # 修复 chapters
        if 'chapters' in novel:
            chapters_list = []
            for i, cf in enumerate(sorted(novel_dir.glob('chapter_*.json'))):
                try:
                    with open(cf, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    num = data.get('num') or data.get('number') or (i + 1)
                    raw_content = data.get('content', '')
                    clean = clean_content(raw_content)
                    title = data.get('title', '').lstrip('#').strip()
                    if not title:
                        title = extract_chapter_title(clean) or f'第{num}章'
                    chapters_list.append({
                        'num': num,
                        'title': title,
                        'status': data.get('status', 'done'),
                        'words': data.get('words') or data.get('wordCount') or 0
                    })
                except:
                    pass
            novel['chapters'] = chapters_list

    # 写回 index.json
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(novels, f, ensure_ascii=False, indent=2)

    print(f"修复主 index.json: {fixed_count} 处修改")


def main():
    novels_dir = Path('d:/003_True_Code/0.6小说Agent/ai-novel-reader/novels')

    print("=" * 50)
    print("开始修复小说阅读器...")
    print("=" * 50)

    # 修复每个小说
    novel_dirs = [d for d in novels_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
    fixed = 0

    for novel_dir in sorted(novel_dirs):
        try:
            title, chapter_count = fix_novel(novel_dir)
            print(f"✓ 修复: {novel_dir.name}")
            print(f"  标题: {title}")
            print(f"  章节: {chapter_count}")
            fixed += 1
        except Exception as e:
            print(f"✗ 失败: {novel_dir.name} - {e}")

    print("-" * 50)

    # 修复主 index.json
    fix_main_index_json()

    print("-" * 50)
    print(f"完成! 共修复 {fixed} 部小说")


if __name__ == '__main__':
    main()
