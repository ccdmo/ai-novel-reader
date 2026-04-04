#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub 集成模块 - 自动上传剧本到 GitHub
"""

import os
import json
import base64
from typing import Dict
from github import Github
from datetime import datetime

class GitHubStorage:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN", "")
        self.repo_name = os.getenv("GITHUB_REPO", "ccdmo/ai-novel-reader")
        
        if self.token:
            self.gh = Github(self.token)
            self.repo = self.gh.get_user().get_repo(self.repo_name.split('/')[-1])
        else:
            self.repo = None
    
    async def save_drama(self, novel_id: str, batch_id: str, script: Dict, review: Dict):
        """保存剧本到 GitHub"""
        if not self.repo or not self.token:
            # 如果没有 GitHub 配置，跳过
            return
        
        try:
            # 保存剧本
            script_path = f"drama_data/{batch_id}/{novel_id}_script.json"
            script_content = json.dumps(script, ensure_ascii=False, indent=2)
            
            self._push_file(
                script_path,
                script_content,
                f"Add drama script for {novel_id}"
            )
            
            # 保存审核结果
            review_path = f"drama_data/{batch_id}/{novel_id}_review.json"
            review_content = json.dumps(review, ensure_ascii=False, indent=2)
            
            self._push_file(
                review_path,
                review_content,
                f"Add review for {novel_id}"
            )
        except Exception as e:
            print(f"GitHub 保存失败: {str(e)}")
    
    def _push_file(self, path: str, content: str, message: str):
        """上传文件到 GitHub"""
        try:
            # 检查文件是否存在
            try:
                file = self.repo.get_contents(path)
                # 文件存在，更新
                self.repo.update_file(
                    path,
                    message,
                    content,
                    file.sha
                )
            except:
                # 文件不存在，创建
                self.repo.create_file(
                    path,
                    message,
                    content
                )
        except Exception as e:
            print(f"上传文件 {path} 失败: {str(e)}")
    
    async def get_drama_from_github(self, novel_id: str, batch_id: str) -> Dict:
        """从 GitHub 读取剧本"""
        if not self.repo:
            return None
        
        try:
            path = f"drama_data/{batch_id}/{novel_id}_script.json"
            file = self.repo.get_contents(path)
            content = file.decoded_content.decode('utf-8')
            return json.loads(content)
        except:
            return None
