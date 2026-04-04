#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为每部小说生成短剧页面 drama.html。
如果已存在 drama_data/batch_001/<novel_id>_script.json，则页面会自动加载剧本；
否则显示提示说明并保留后续生成入口。
"""

import json
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
NOVELS_DIR = ROOT / 'novels'
DRAMA_DIR = ROOT / 'drama_data' / 'batch_001'
DRAMA_DIR.mkdir(parents=True, exist_ok=True)

DRAMA_HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__ - 短剧版</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f6f8fb; color: #222; }
.header { background: linear-gradient(135deg, #4CAF50 0%, #2e7d32 100%); color: white; padding: 1.5rem 1rem; }
.header a { color: white; text-decoration: none; margin-right: 0.75rem; }
.header h1 { font-size: 1.5rem; margin-top: 0.75rem; }
.container { max-width: 960px; margin: 2rem auto; padding: 0 1rem; }
.notice { background: white; border: 1px solid #dfe3e8; border-radius: 12px; padding: 1.5rem; color: #555; box-shadow: 0 2px 10px rgba(0,0,0,.04); }
.scene { background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 2px 10px rgba(0,0,0,.04); }
.scene-title { font-size: 1.05rem; font-weight: 700; color: #1b5e20; margin-bottom: 0.75rem; }
.scene-meta { font-size: 0.85rem; color: #777; margin-bottom: 1rem; }
.scene-content { line-height: 1.8; color: #333; white-space: pre-wrap; word-break: break-word; }
.button { display: inline-block; padding: 0.55rem 1rem; border-radius: 8px; background: rgba(255,255,255,0.15); color: white; border: 1px solid rgba(255,255,255,0.35); text-decoration: none; }
</style>
</head>
<body>
<div class="header">
  <a href="./" class="button">← 返回小说</a>
  <a href="../../" class="button">← 返回目录</a>
  <h1>__TITLE__ - 短剧版</h1>
</div>
<div class="container">
  <div id="dramaRoot" class="notice">正在加载短剧剧本…</div>
</div>
<script>
const scriptUrl = '/drama_data/batch_001/' + encodeURIComponent('__NOVEL_ID__') + '__script.json';
const root = document.getElementById('dramaRoot');

async function loadDrama() {
  try {
    const resp = await fetch(scriptUrl);
    if (!resp.ok) throw new Error('剧本文件未找到');
    const data = await resp.json();
    if (!data.scenes || !data.scenes.length) throw new Error('剧本格式不完整');

    const html = [`
      <div class="notice" style="background:#e8f5e9;border-color:#c8e6c9;color:#1b5e20;">
        <strong>剧本来源：</strong>__TITLE__<br>
        <strong>小说 ID：</strong>__NOVEL_ID__<br>
        <strong>场景数：</strong>${data.scenes.length}
      </div>
    `];

    data.scenes.forEach(scene => {
      const content = scene.content ? scene.content.trim().replace(/\n/g, '<br>') : '';
      html.push(`
        <div class="scene">
          <div class="scene-title">${scene.scene ? '场景 ' + scene.scene : scene.title}</div>
          <div class="scene-meta">${scene.title || ''} · ${scene.time || ''}</div>
          <div class="scene-content">${content}</div>
        </div>
      `);
    });

    root.outerHTML = html.join('');
  } catch (err) {
    root.innerHTML = `<div class="notice">短剧版剧本尚未生成。请先运行短剧转换脚本或使用 API 生成剧本。<br><br><strong>错误：</strong>${err.message}</div>`;
  }
}

loadDrama();
</script>
</body>
</html>
'''


def load_novels_index():
    index_file = NOVELS_DIR / 'index.json'
    if not index_file.exists():
        raise FileNotFoundError(f'找不到 {index_file}')
    with open(index_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_drama_page(novel_id: str, title: str):
    novel_dir = NOVELS_DIR / novel_id
    if not novel_dir.exists():
        print(f'跳过不存在的小说目录: {novel_id}')
        return

    page_path = novel_dir / 'drama.html'
    html = DRAMA_HTML_TEMPLATE.replace('__TITLE__', title).replace('__NOVEL_ID__', novel_id)
    with open(page_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'生成短剧页面: {page_path}')


def main():
    novels = load_novels_index()
    for novel in novels:
        novel_id = novel.get('id')
        title = novel.get('title') or novel_id
        if not novel_id:
            continue
        build_drama_page(novel_id, title)
    print('短剧页面生成完成。')


if __name__ == '__main__':
    main()
