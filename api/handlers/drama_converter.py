#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说 → 短剧剧本转换模块
使用 OpenAI API 进行转换
"""

import json
import os
from pathlib import Path
import openai
from typing import Dict, List

class DramaConverter:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = "gpt-3.5-turbo"  # 或使用 gpt-4
        openai.api_key = self.api_key
        
        # 数据路径
        self.novels_dir = Path(__file__).parent.parent.parent / "novels"

    async def load_novel(self, novel_id: str) -> Dict:
        """从 JSON 读取小说数据"""
        try:
            novel_dir = self.novels_dir / novel_id
            
            # 优先读 chapter_0001.json
            chapter_file = novel_dir / "chapter_0001.json"
            if not chapter_file.exists():
                raise FileNotFoundError(f"找不到小说: {novel_id}")
            
            with open(chapter_file, 'r', encoding='utf-8') as f:
                chapter = json.load(f)
                
            # 读取 chapters.json 获取元数据
            chapters_file = novel_dir / "chapters.json"
            metadata = {}
            if chapters_file.exists():
                with open(chapters_file, 'r', encoding='utf-8') as f:
                    chapters = json.load(f)
                    if chapters:
                        metadata = chapters[0] if isinstance(chapters, list) else chapters
            
            return {
                "id": novel_id,
                "title": metadata.get("title", novel_id),
                "chapter_title": chapter.get("title", "第一章"),
                "content": chapter.get("content", ""),
                "metadata": metadata
            }
        except Exception as e:
            raise Exception(f"加载小说失败: {str(e)}")

    async def generate_script(self, novel_data: Dict, novel_id: str) -> Dict:
        """
        使用 LLM 将小说转换为短剧剧本
        
        剧本格式:
        {
            "title": "短剧标题",
            "scenes": [
                {
                    "scene": 1,
                    "title": "场景标题",
                    "time": "时间地点",
                    "content": "【场景描写】\\n角色A:对话\\n角色B:对话"
                }
            ]
        }
        """
        try:
            prompt = self._build_conversion_prompt(novel_data)
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位专业的短剧编剧。你需要将小说内容改编成精炼的短剧剧本。"
                                   "剧本应该包含3-5个场景，每个场景包含清晰的场景描写和角色对话。"
                                   "返回 JSON 格式的剧本数据。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # 解析 LLM 返回的剧本
            script_text = response.choices[0].message.content
            script = self._parse_script_response(script_text, novel_data)
            
            return script
            
        except Exception as e:
            raise Exception(f"生成剧本失败: {str(e)}")

    def _build_conversion_prompt(self, novel_data: Dict) -> str:
        """构建转换提示词"""
        content = novel_data.get("content", "")[:2000]  # 限制长度
        
        return f"""请将以下小说内容改编为精炼的短剧剧本。

小说标题: {novel_data.get('title', '未知')}
章节标题: {novel_data.get('chapter_title', '第一章')}

小说内容:
{content}

转换要求:
1. 创作3-5个精彩场景
2. 每个场景包含: 场景号、场景标题、时间地点、详细内容
3. 内容格式: 【场景描写】开头，然后是角色对话(格式: 角色名:对话内容)
4. 突出戏剧冲突和人物对话
5. 返回有效的 JSON 格式

JSON 格式示例:
{{
    "title": "剧本标题",
    "genre": "类型",
    "episodes": 1,
    "scenes": [
        {{
            "scene": 1,
            "title": "场景标题",
            "time": "时间地点",
            "content": "【场景描写】...\\n角色A:对话\\n角色B:对话"
        }}
    ]
}}
"""

    def _parse_script_response(self, script_text: str, novel_data: Dict) -> Dict:
        """解析 LLM 返回的剧本文本"""
        try:
            # 尝试从文本中提取 JSON
            json_start = script_text.find('{')
            json_end = script_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = script_text[json_start:json_end]
                script = json.loads(json_str)
            else:
                # 如果无法解析，创建基本结构
                script = {
                    "title": novel_data.get("title", "未知"),
                    "genre": "短剧",
                    "episodes": 1,
                    "scenes": [
                        {
                            "scene": 1,
                            "title": "转换失败",
                            "time": "未知",
                            "content": script_text
                        }
                    ]
                }
            
            # 补充数据
            script["source_novel_id"] = novel_data.get("id")
            script["source_title"] = novel_data.get("title")
            
            return script
            
        except Exception as e:
            return {
                "title": novel_data.get("title", "未知"),
                "genre": "短剧",
                "error": str(e),
                "raw_content": script_text
            }

    async def validate_script(self, script: Dict) -> bool:
        """验证剧本有效性"""
        if not isinstance(script, dict):
            return False
        
        required_fields = ["title", "scenes"]
        return all(field in script for field in required_fields)
