#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批次管理模块 - 管理转换批次、进度跟踪、审核状态
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class BatchManager:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent / "drama_data"
        self.data_dir.mkdir(exist_ok=True)
    
    async def create_batch(self, batch_id: str, novel_count: int) -> Dict:
        """创建新批次"""
        batch_file = self.data_dir / f"{batch_id}_status.json"
        
        batch_data = {
            "batch_id": batch_id,
            "created_at": datetime.now().isoformat(),
            "total_required": novel_count,
            "completed": 0,
            "failed": 0,
            "approved": 0,
            "rejected": 0,
            "novels": {}
        }
        
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(batch_data, f, ensure_ascii=False, indent=2)
        
        return batch_data
    
    async def get_batch_status(self, batch_id: str) -> Dict:
        """获取批次状态"""
        batch_file = self.data_dir / f"{batch_id}_status.json"
        
        if not batch_file.exists():
            return {
                "error": "批次不存在",
                "batch_id": batch_id
            }
        
        with open(batch_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def save_drama_result(self, novel_id: str, script: Dict, review: Dict, batch_id: str) -> Dict:
        """保存单部剧本结果"""
        # 创建批次目录
        batch_dir = self.data_dir / batch_id
        batch_dir.mkdir(exist_ok=True)
        
        # 保存剧本
        script_file = batch_dir / f"{novel_id}_script.json"
        with open(script_file, 'w', encoding='utf-8') as f:
            json.dump(script, f, ensure_ascii=False, indent=2)
        
        # 保存审核结果
        review_file = batch_dir / f"{novel_id}_review.json"
        with open(review_file, 'w', encoding='utf-8') as f:
            json.dump(review, f, ensure_ascii=False, indent=2)
        
        # 更新批次状态
        await self._update_batch_progress(batch_id, novel_id, review)
        
        return {
            "status": "saved",
            "script_url": str(script_file),
            "review_url": str(review_file)
        }
    
    async def _update_batch_progress(self, batch_id: str, novel_id: str, review: Dict):
        """更新批次进度"""
        batch_file = self.data_dir / f"{batch_id}_status.json"
        
        if batch_file.exists():
            with open(batch_file, 'r', encoding='utf-8') as f:
                batch = json.load(f)
        else:
            batch = {
                "batch_id": batch_id,
                "created_at": datetime.now().isoformat(),
                "total_required": 0,
                "completed": 0,
                "failed": 0,
                "novels": {}
            }
        
        # 更新统计
        batch["completed"] = batch.get("completed", 0) + 1
        batch["novels"][novel_id] = {
            "score": review.get("quality_score", 0),
            "status": "pending",
            "completed_at": datetime.now().isoformat()
        }
        
        batch["updated_at"] = datetime.now().isoformat()
        
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(batch, f, ensure_ascii=False, indent=2)
    
    async def update_approval_status(self, novel_id: str, status: str, batch_id: str, notes: str = "") -> Dict:
        """更新审核状态"""
        batch_dir = self.data_dir / batch_id
        batch_file = self.data_dir / f"{batch_id}_status.json"
        
        if batch_file.exists():
            with open(batch_file, 'r', encoding='utf-8') as f:
                batch = json.load(f)
            
            if novel_id in batch.get("novels", {}):
                batch["novels"][novel_id]["approval_status"] = status
                batch["novels"][novel_id]["approval_notes"] = notes
                batch["novels"][novel_id]["approved_at"] = datetime.now().isoformat()
                
                with open(batch_file, 'w', encoding='utf-8') as f:
                    json.dump(batch, f, ensure_ascii=False, indent=2)
        
        return {
            "status": "updated",
            "novel_id": novel_id,
            "approval_status": status
        }
    
    async def get_audit_list(self, batch_id: str, status: Optional[str] = None) -> List[Dict]:
        """获取待审核列表"""
        batch_file = self.data_dir / f"{batch_id}_status.json"
        
        if not batch_file.exists():
            return []
        
        with open(batch_file, 'r', encoding='utf-8') as f:
            batch = json.load(f)
        
        audit_list = []
        for novel_id, data in batch.get("novels", {}).items():
            if status is None or data.get("approval_status") == status:
                audit_list.append({
                    "novel_id": novel_id,
                    "score": data.get("score", 0),
                    "status": data.get("approval_status", "pending"),
                    "status_cn": self._get_status_cn(data.get("approval_status", "pending")),
                    "notes": data.get("approval_notes", ""),
                    "title": novel_id
                })
        
        return audit_list
    
    async def get_drama_detail(self, novel_id: str, batch_id: str) -> Dict:
        """获取单部剧本详情"""
        script_file = self.data_dir / batch_id / f"{novel_id}_script.json"
        review_file = self.data_dir / batch_id / f"{novel_id}_review.json"
        
        if not script_file.exists():
            raise FileNotFoundError(f"剧本不存在")
        
        with open(script_file, 'r', encoding='utf-8') as f:
            script = json.load(f)
        
        review = {}
        if review_file.exists():
            with open(review_file, 'r', encoding='utf-8') as f:
                review = json.load(f)
        
        return {
            "novel_id": novel_id,
            "script": script,
            "review": review
        }
    
    async def get_batch_stats(self, batch_id: str) -> Dict:
        """获取批次统计信息"""
        batch_file = self.data_dir / f"{batch_id}_status.json"
        
        if not batch_file.exists():
            return {"error": "批次不存在"}
        
        with open(batch_file, 'r', encoding='utf-8') as f:
            batch = json.load(f)
        
        scores = [data.get("score", 0) for data in batch.get("novels", {}).values()]
        
        return {
            "batch_id": batch_id,
            "total_required": batch.get("total_required", 0),
            "completed": batch.get("completed", 0),
            "approved": batch.get("approved", 0),
            "rejected": batch.get("rejected", 0),
            "average_score": sum(scores) / len(scores) if scores else 0,
            "max_score": max(scores) if scores else 0,
            "min_score": min(scores) if scores else 0
        }
    
    def _get_status_cn(self, status: str) -> str:
        """状态中文映射"""
        status_map = {
            "pending": "待审核",
            "approved": "已批准",
            "rejected": "已拒绝",
            "modified": "已修改"
        }
        return status_map.get(status, status)
