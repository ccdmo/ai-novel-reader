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
    def __init__(self, model: str = None):
        self.default_api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
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

        return f"""你是一位获奖的短剧编剧。请根据小说和分析数据，创作一部精彩的短剧剧本。

创作约束：
1. 保留核心冲突和人物关系
2. 浓缩为 3-5 个高潮场景
3. 每个场景一次对话转折
4. 人物性格必须前后一致
5. 对话要自然流畅，有各自的说话风格
6. 场景之间有明确的逻辑连接
7. 结尾要有冲击力或悬念

剧本格式标准：
- 场景描写用【】标注
- 对话格式：角色名:说白内容
- 角色动作用（）标注
- 每个场景 200-400 字

小说标题: {novel_data.get('title', '未知')}
章节标题: {novel_data.get('chapter_title', '第一章')}

小说内容:
{content}
{analysis_text}
输出格式（严格 JSON）:
{{
    "title": "短剧标题",
    "genre": "主要类型",
    "episodes": 1,
    "scenes": [
        {{
            "scene": 1,
            "title": "场景标题",
            "time": "时空设定（如：黄昏，公寓客厅）",
            "content": "【场景描写】描写\\n角色A:对话\\n（动作描述）\\n角色B:对话"
        }}
    ]
}}
"""
    
    def _build_synopsis_prompt(self, novel_data: Dict) -> str:
        """构建故事简介提取提示词"""
        content = novel_data.get("content", "")[:1800]
        return f"""你是一位资深出版编辑。请深入分析以下小说内容，提炼出核心要素，并返回严格 JSON。

分析维度：
1. 故事简介 - 用 1-2 句话概括核心故事
2. 类型分类 - 主题类型（科幻/悬疑/言情/奇幻/都市等）
3. 核心主题 - 故事要表达的深层意义（最多 5 个）
4. 故事语气 - 整体基调（紧张/温暖/黑暗/搞笑/浪漫等）
5. 核心冲突 - 驱动故事发展的最主要矛盾

小说标题: {novel_data.get('title', '未知')}
章节标题: {novel_data.get('chapter_title', '第一章')}

小说内容:
{content}

输出格式（严格 JSON）:
{{
  "synopsis": "故事简介文字",
  "genre": "主要类型",
  "themes": ["主题1", "主题2", "主题3"],
  "tone": "故事语气",
  "key_conflict": "核心冲突描述"
}}
"""

    def _build_characters_prompt(self, novel_data: Dict) -> str:
        """构建角色提取提示词"""
        content = novel_data.get("content", "")[:1400]
        return f"""你是一位专业编剧顾问。请从小说内容中提取主要角色，构建完整的人物档案。

角色提取标准：
- 只列出对剧情有重要影响的角色（3-7 个）
- 包含完整的人物设定信息
- 明确角色之间的冲突和关系

角色属性说明：
- name: 角色名字
- role: 角色定位（主角/反派/配角等）
- age: 年龄或年龄段
- traits: 核心性格特质（简短形容词组）
- relationship: 与其他角色的关系
- arc: 角色的成长/变化轨迹
- conflict: 角色面临的主要内部或外部冲突

小说标题: {novel_data.get('title', '未知')}
章节标题: {novel_data.get('chapter_title', '第一章')}

小说内容:
{content}

输出格式（严格 JSON）:
{{
  "main_characters": [
    {{
      "name": "角色名",
      "role": "主角/反派/配角",
      "age": "描述",
      "traits": "性格特质",
      "relationship": "与其他角色的关系",
      "arc": "角色成长弧线",
      "conflict": "主要冲突或困境"
    }}
  ]
}}
"""

    def _build_chapter_analysis_prompt(self, novel_data: Dict) -> str:
        """构建章节分析提示词"""
        content = novel_data.get("content", "")[:1600]
        return f"""你是一位资深剧本分析师。请按照故事结构化分析标准，逐章分析小说内容。

章节分析维度：
1. 章节概要 - 本章核心事件和转折点
2. 关键人物 - 在本章中有重要作用的角色
3. 场景地点 - 主要故事发生的地点
4. 主干冲突 - 本章的核心矛盾或转折
5. 场景拆解 - 将章节分解为 2-4 个清晰的场景

小说标题: {novel_data.get('title', '未知')}
章节标题: {novel_data.get('chapter_title', '第一章')}

小说内容:
{content}

输出格式（严格 JSON）:
{{
  "chapter_outline": [
    {{
      "chapter": 1,
      "chapter_title": "章节标题",
      "summary": "章节概要（1-2 句）",
      "key_characters": ["角色1", "角色2"],
      "settings": "主要场景地点",
      "major_conflict": "本章核心冲突",
      "scene_breakdown": [
        {{
          "scene": 1,
          "title": "场景标题",
          "description": "场景描写",
          "characters": ["角色A", "角色B"],
          "conflict": "本场景的冲突或转折"
        }}
      ]
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
