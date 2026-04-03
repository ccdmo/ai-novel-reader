#!/usr/bin/env python3
"""
修复所有小说站点文件：统一生成 index.html、chapter_*.json
"""
import json, os, re, glob

SITE_DIR = "/home/gem/workspace/agent/novel-website/novels"

INDEX_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f5f5f5;color:#333}}
.header{{background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:1.5rem 1rem}}
.header h1{{font-size:1.5rem}}.meta{{opacity:0.85;font-size:0.9rem;margin-top:0.3rem}}
.container{{max-width:800px;margin:2rem auto;padding:0 1rem}}
.chapter-list{{background:white;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08)}}
.chapter{{padding:1rem 1.2rem;border-bottom:1px solid #f0f0f0;cursor:pointer;transition:background .15s}}
.chapter:hover{{background:#f8f6ff}}
.chapter-num{{color:#667eea;font-weight:600;font-size:.85rem}}
.chapter-title{{margin-top:.3rem}}
.back-btn{{display:inline-block;margin-bottom:1rem;color:#667eea;text-decoration:none;font-size:.9rem}}
.content-box{{background:white;border-radius:12px;padding:2rem;margin-top:1rem;box-shadow:0 2px 8px rgba(0,0,0,.08);line-height:1.9;font-size:1.05rem;white-space:pre-wrap}}
.chapter-nav{{margin-top:1.5rem;padding-top:1rem;border-top:1px solid #eee;display:flex;justify-content:space-between}}
.chapter-nav a{{color:#667eea;text-decoration:none;font-size:.9rem}}
</style>
</head>
<body>
<div class="header"><div class="container">
<a href="../" class="back-btn">← 返回书库</a>
<h1>📖 {title}</h1>
<div class="meta">{genre} · AI仿写版</div>
</div></div>
<div class="container" id="app"></div>
<script>
var CHAPTERS = {chapters_json};
var BOOK_ID = "{book_id}";

function renderList() {{
    var html = CHAPTERS.map(function(ch, i) {{
        return '<div class="chapter" onclick="renderChapter(' + i + ')"><div class="chapter-num">第' + ch.num + '章</div><div class="chapter-title">' + ch.title + '</div></div>';
    }}).join('');
    document.getElementById("app").innerHTML = html;
}}

function renderChapter(idx) {{
    var ch = CHAPTERS[idx];
    var xhr = new XMLHttpRequest();
    xhr.open('GET', 'chapter_' + String(idx+1).padStart(4,'0') + '.json', true);
    xhr.onload = function() {{
        var data = JSON.parse(xhr.responseText);
        var prev = idx > 0 ? '<a href="javascript:renderChapter(' + (idx-1) + ')">← 上一章</a>' : '<span></span>';
        var next = idx < CHAPTERS.length - 1 ? '<a href="javascript:renderChapter(' + (idx+1) + ')">下一章 →</a>' : '<span></span>';
        document.getElementById("app").innerHTML = '<a href="javascript:renderList()" class="back-btn">← 返回目录</a><div class="content-box"><h2 style="margin-bottom:1.5rem">第' + data.num + '章 · ' + data.title + '</h2>' + data.content + '</div><div class="chapter-nav">' + prev + next + '</div>';
        window.scrollTo(0,0);
    }};
    xhr.send();
}}

// auto from URL param
var params = new URLSearchParams(location.search);
var c = params.get("c");
if (c !== null) {{ renderChapter(parseInt(c)); }} else {{ renderList(); }}
</script>
</body>
</html>"""

def get_title_from_index(dir):
    """从 index.json 读取书名"""
    idx_path = os.path.join(dir, "index.json")
    if os.path.exists(idx_path):
        try:
            with open(idx_path) as f:
                d = json.load(f)
            if isinstance(d, dict):
                return d.get("title", os.path.basename(dir))
            return os.path.basename(dir)
        except:
            pass
    return os.path.basename(dir)

def find_chapter_file(dir, book_id):
    """找章节文件，可能叫 chapter_0001.json, ch1.json, chapter-1.md, chapter_0001.html 等"""
    candidates = [
        os.path.join(dir, "chapter_0001.json"),
        os.path.join(dir, "ch1.json"),
        os.path.join(dir, "chapter-1.json"),
        os.path.join(dir, "chapter_0001.html"),
        os.path.join(dir, "chapter_0001.md"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    # 搜索目录下所有 chapter 相关文件
    for f in os.listdir(dir):
        if "chapter" in f.lower() or f.startswith("ch") and f.endswith((".json",".md",".html",".txt")):
            return os.path.join(dir, f)
    return None

def read_chapter_content(path):
    """读取章节内容，处理不同格式"""
    with open(path, encoding="utf-8") as f:
        content = f.read().strip()
    
    if path.endswith(".json"):
        try:
            d = json.loads(content)
            if isinstance(d, dict) and "content" in d:
                return d["title"], d["content"], d.get("words", len(d.get("content","")))
            if isinstance(d, dict) and "chapter_title" in d:
                return d["chapter_title"], d.get("content","") or d.get("body",""), d.get("words",0)
        except:
            pass
    
    if path.endswith(".html"):
        # 去掉 HTML 标签提取纯文本
        text = re.sub(r"<[^>]+>", "", content)
        return "第一章", text, len(text)
    
    if path.endswith(".md"):
        lines = content.split("\n")
        title = lines[0].strip() if lines else "第一章"
        body = "\n".join(lines[1:]).strip()
        return title, body, len(body)
    
    if path.endswith(".txt"):
        lines = content.split("\n")
        title = lines[0].strip() if lines else "第一章"
        body = "\n".join(lines[1:]).strip()
        return title, body, len(body)
    
    return "第一章", content, len(content)

def fix_one(dir_path):
    """修复一本书"""
    book_id = os.path.basename(dir_path)
    title = get_title_from_index(dir_path)
    genre = "都市"
    
    # 找 chapters.json
    chapters_json_path = os.path.join(dir_path, "chapters.json")
    chapters_data = []
    if os.path.exists(chapters_json_path):
        try:
            with open(chapters_json_path) as f:
                chapters_data = json.load(f)
        except:
            chapters_data = []
    
    # 找章节文件
    chapter_file = find_chapter_file(dir_path, book_id)
    if not chapter_file:
        print(f"  ⚠️ {book_id}: 无章节文件，跳过")
        return False
    
    # 读取并转换章节内容
    try:
        title, content, words = read_chapter_content(chapter_file)
    except Exception as e:
        print(f"  ❌ {book_id}: 读取章节失败 {e}")
        return False
    
    # 生成 chapter_0001.json
    chapter_json_path = os.path.join(dir_path, "chapter_0001.json")
    chapter_out = {
        "num": 1,
        "title": title,
        "content": content,
        "words": words
    }
    with open(chapter_json_path, 'w', encoding='utf-8') as f:
        json.dump(chapter_out, f, ensure_ascii=False, indent=2)
    
    # 生成 chapters.json
    if not chapters_data:
        chapters_data = [{"num": 1, "title": title, "status": "done", "words": words}]
        with open(chapters_json_path, 'w', encoding='utf-8') as f:
            json.dump(chapters_data, f, ensure_ascii=False)
    
    # 生成 index.html
    index_path = os.path.join(dir_path, "index.html")
    html_content = INDEX_HTML_TEMPLATE.format(
        title=title,
        genre=genre,
        book_id=book_id,
        chapters_json=json.dumps(chapters_data, ensure_ascii=False)
    )
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"  ✅ {book_id}: 修复完成 ({words}字)")
    return True

def main():
    dirs = sorted(os.listdir(SITE_DIR))
    print(f"共 {len(dirs)} 本书，开始修复...")
    
    results = {}
    for d in dirs:
        dir_path = os.path.join(SITE_DIR, d)
        if not os.path.isdir(dir_path):
            continue
        results[d] = fix_one(dir_path)
    
    success = sum(1 for v in results.values() if v)
    print(f"\n修复完成: {success}/{len(results)} 本")
    
    # 更新 index.json
    idx_path = os.path.join(SITE_DIR, "index.json")
    with open(idx_path) as f:
        index_data = json.load(f)
    
    for entry in index_data:
        bid = entry["id"]
        dp = os.path.join(SITE_DIR, bid)
        if os.path.exists(dp):
            entry["chapters"] = 1
            entry["status"] = "completed"
    
    with open(idx_path, 'w') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    # Git commit + push
    os.chdir("/home/gem/workspace/agent/novel-website")
    import subprocess
    subprocess.run("git add -A", shell=True)
    r = subprocess.run('git commit -m "fix: 批量修复所有书籍index.html和章节文件"', shell=True, capture_output=True, text=True)
    if r.returncode == 0:
        print("Git commit 成功")
        rr = subprocess.run("git push origin main", shell=True, capture_output=True, text=True)
        if rr.returncode == 0:
            print("Git push 成功!")
        else:
            print(f"Git push 失败: {rr.stderr[:200]}")
    else:
        print(f"Git commit 失败: {r.stderr[:200]}")

if __name__ == "__main__":
    main()
