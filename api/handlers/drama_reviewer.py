#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 审核模块 - 使用 Claude/OpenAI 进行质量检查
"""

import os
from typing import Dict, List
import anthropic

class DramaReviewer:
    def __init__(self):
        self.default_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        
    async def review_script(self, script: Dict, novel_id: str, api_key: str = None, prompt_override: str = None) -> Dict:
        """
        审核短剧剧本质量
        
        检查项:
        - 完整性：是否包含完整的场景和对话
        - 可读性：对话是否流畅真实
        - 冲突性：是否有足够的戏剧冲突
        - 敏感词：是否包含不当内容
        """
        try:
            # 使用提交的 API Key 或者默认 Key
            key_to_use = api_key or self.default_api_key
            if not key_to_use:
                raise ValueError("Anthropic API Key 未提供")
            
            client = anthropic.Anthropic(api_key=key_to_use)
            
            # 构建审核提示
            prompt = prompt_override or self._build_review_prompt(script)
            
            # 调用 Claude API
            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            review_text = message.content[0].text
            review = self._parse_review(review_text, script)
            
            return review
            
        except Exception as e:
            # 如果 API 调用失败，返回基本评分
            return {
                "quality_score": 65,
                "summary": f"审核失败: {str(e)}",
                "issues": [],
                "warnings": [],
                "status": "error"
            }
    
    def _build_review_prompt(self, script: Dict) -> str:
        """构建审核提示词"""
        script_str = str(script)[:1500]
        
        return f"""请审核以下短剧剧本质量，并给出 0-100 的评分和建议。

剧本内容:
{script_str}

审核标准:
1. 完整性 (0-25分): 是否包含完整的场景、人物和故事线
2. 可读性 (0-25分): 对话是否自然流畅，是否适合短剧表演
3. 戏剧性 (0-25分): 是否有冲突、转折和吸引力
4. 技术性 (0-25分): 格式是否规范，标记是否清晰

请返回 JSON 格式的评审结果，包括:
{{
    "score": 0-100,
    "summary": "总体评价",
    "issues": ["问题1", "问题2"],
    "suggestions": ["建议1", "建议2"],
    "ready_for_approval": true/false
}}
"""
    
    def _parse_review(self, review_text: str, script: Dict) -> Dict:
        """解析审核结果"""
        try:
            import json
            
            # 尝试提取 JSON
            json_start = review_text.find('{')
            json_end = review_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = review_text[json_start:json_end]
                return json.loads(json_str)
            else:
                return {
                    "quality_score": 70,
                    "summary": review_text,
                    "issues": [],
                    "warnings": []
                }
        except:
            return {
                "quality_score": 70,
                "summary": review_text[:200],
                "issues": [],
                "warnings": []
            }
    
    async def check_sensitive_content(self, script: Dict) -> List[str]:
        """检查敏感内容"""
        issues = []
        
        # 敏感词检查
        sensitive_words = ["暴力", "色情", "毒品", "诈骗"]
        script_str = str(script).lower()
        
        for word in sensitive_words:
            if word in script_str:
                issues.append(f"检测到潜在敏感词: {word}")
        
        return issues
