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
from typing import Any, Dict, List, Optional

class DramaConverter:
    def __init__(self):
        self.default_api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = "gpt-3.5-turbo"  # 或使用 gpt-4
        
        # 数据路径
        self.novels_dir = Path(__file__).parent.parent.parent / "novels"

    async def load_novel(self, novel_id: str, api_key: str = None) -> Dict:
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

    async def generate_drama_package(self, novel_data: Dict, novel_id: str, api_key: str = None, prompt_override: str = None) -> Dict:
        """多阶段生成：提炼简介、角色、章节分析，再生产剧本"""
        try:
            synopsis = await self.generate_synopsis(novel_data, api_key)
            characters = await self.extract_main_characters(novel_data, api_key)
            chapter_outline = await self.analyze_chapter_structure(novel_data, api_key)
            script = await self.generate_script(
                novel_data,
                novel_id,
                api_key,
                prompt_override=prompt_override,
                analysis={
                    "synopsis": synopsis,
                    "main_characters": characters,
                    "chapter_outline": chapter_outline
                }
            )

            script["synopsis"] = synopsis
            script["main_characters"] = characters
            script["chapter_outline"] = chapter_outline

            return script
        except Exception as e:
            raise Exception(f"生成剧本包失败: {str(e)}")

    async def generate_synopsis(self, novel_data: Dict, api_key: str = None) -> Dict:
        """生成小说简介与核心冲突"""
        key_to_use = api_key or self.default_api_key
        if not key_to_use:
            raise ValueError("OpenAI API Key 未提供")

        openai.api_key = key_to_use
        prompt = self._build_synopsis_prompt(novel_data)

        response_text = self._call_openai_chat([
            {
                "role": "system",
                "content": "你是一位出版级小说分析师，负责提炼小说故事核心、类型和人物结构。返回严格的 JSON。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ], max_tokens=900)

        return self._parse_json_response(response_text, {
            "synopsis": novel_data.get("content", "")[:200],
            "genre": "未知",
            "themes": [],
            "tone": "沉浸",
            "key_conflict": ""
        })

    async def extract_main_characters(self, novel_data: Dict, api_key: str = None) -> List[Dict[str, Any]]:
        """提取主要角色及其性格、身份、关系、冲突"""
        key_to_use = api_key or self.default_api_key
        if not key_to_use:
            raise ValueError("OpenAI API Key 未提供")

        openai.api_key = key_to_use
        prompt = self._build_characters_prompt(novel_data)

        response_text = self._call_openai_chat([
            {
                "role": "system",
                "content": "你是一位小说人物结构专家。请提取小说中的主要角色，并用 JSON 输出角色关系和特性。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ], max_tokens=900)

        parsed = self._parse_json_response(response_text, {"main_characters": []})
        return parsed.get("main_characters", [])

    async def analyze_chapter_structure(self, novel_data: Dict, api_key: str = None) -> List[Dict[str, Any]]:
        """按章节生成情节提要、核心场景、人物与冲突"""
        key_to_use = api_key or self.default_api_key
        if not key_to_use:
            raise ValueError("OpenAI API Key 未提供")

        openai.api_key = key_to_use
        prompt = self._build_chapter_analysis_prompt(novel_data)

        response_text = self._call_openai_chat([
            {
                "role": "system",
                "content": "你是一位小说结构分析师。请按章节输出简洁的章节概要、关键场景、主要人物和核心冲突。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ], max_tokens=1200)

        parsed = self._parse_json_response(response_text, {"chapter_outline": []})
        return parsed.get("chapter_outline", [])

    async def generate_script(self, novel_data: Dict, novel_id: str, api_key: str = None, prompt_override: str = None, analysis: Dict[str, Any] = None) -> Dict:
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
            # 使用提交的 API Key 或者默认 Key
            key_to_use = api_key or self.default_api_key
            if not key_to_use:
                raise ValueError("OpenAI API Key 未提供")
            
            openai.api_key = key_to_use
            prompt = prompt_override or self._build_conversion_prompt(novel_data, analysis)
            
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

    def _build_conversion_prompt(self, novel_data: Dict, analysis: Dict[str, Any] = None) -> str:
        """构建转换提示词"""
        content = novel_data.get("content", "")[:2000]  # 限制长度
        analysis_text = ""
        if analysis:
            synopsis = analysis.get("synopsis") or {}
            characters = analysis.get("main_characters") or []
            chapter_outline = analysis.get("chapter_outline") or []

            analysis_text = "\n已提炼内容：\n"
            if isinstance(synopsis, dict):
                analysis_text += f"故事简介: {synopsis.get('synopsis', '')}\n"
                analysis_text += f"类型: {synopsis.get('genre', '')}\n"
                analysis_text += f"主题: {', '.join(synopsis.get('themes', [])) if isinstance(synopsis.get('themes', []), list) else synopsis.get('themes', '')}\n"
                analysis_text += f"核心冲突: {synopsis.get('key_conflict', '')}\n\n"

            if characters:
                analysis_text += "主要角色：\n"
                for char in characters:
                    analysis_text += f"- {char.get('name', '')} ({char.get('role', '')})，性格：{char.get('traits', '')}，关系：{char.get('relationship', '')}，弧线：{char.get('arc', '')}\n"
                analysis_text += "\n"

            if chapter_outline:
                analysis_text += "章节概要：\n"
                for chapter in chapter_outline:
                    analysis_text += f"章节{chapter.get('chapter', '')}：{chapter.get('chapter_title', '')}，概要：{chapter.get('summary', '')}，冲突：{chapter.get('major_conflict', '')}\n"
                analysis_text += "\n"

        return f"""请将以下小说内容改编为精炼的短剧剧本。

小说标题: {novel_data.get('title', '未知')}
章节标题: {novel_data.get('chapter_title', '第一章')}

小说内容:
{content}
{analysis_text}
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

    def _call_openai_chat(self, messages: List[Dict[str, str]], max_tokens: int = 2000, temperature: float = 0.7) -> str:
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content

    def _parse_json_response(self, raw_text: str, fallback: Any) -> Any:
        try:
            json_start = raw_text.find('{')
            json_end = raw_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_text = raw_text[json_start:json_end]
                return json.loads(json_text)
            return fallback
        except Exception:
            return fallback

    async def validate_script(self, script: Dict) -> bool:
        """验证剧本有效性"""
        if not isinstance(script, dict):
            return False
        
        required_fields = ["title", "scenes"]
        return all(field in script for field in required_fields)
