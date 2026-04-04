#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 验证新的多阶段短剧生成流程
测试项：简介提取、角色提取、章节分析、剧本生成
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# 添加 API 路径到 Python path
sys.path.insert(0, str(Path(__file__).parent / "api"))

from handlers.drama_converter import DramaConverter


async def test_single_novel(novel_id: str, openai_key: str):
    """测试单部小说的多阶段转换流程"""
    print("\n" + "="*80)
    print(f"🔍 开始测试小说: {novel_id}")
    print("="*80)
    
    converter = DramaConverter()
    
    try:
        # 第1步：加载小说
        print("\n[1/5] 加载小说数据...")
        novel_data = await converter.load_novel(novel_id, openai_key)
        print(f"✅ 小说标题: {novel_data.get('title')}")
        print(f"✅ 章节标题: {novel_data.get('chapter_title')}")
        print(f"✅ 内容长度: {len(novel_data.get('content', ''))} 字符")
        
        # 第2步：提取简介
        print("\n[2/5] 提取故事简介与核心冲突...")
        synopsis = await converter.generate_synopsis(novel_data, openai_key)
        print(f"✅ 故事类型: {synopsis.get('genre')}")
        print(f"✅ 主题: {', '.join(synopsis.get('themes', []))}")
        print(f"✅ 故事语气: {synopsis.get('tone')}")
        print(f"✅ 核心冲突: {synopsis.get('key_conflict', '')[:100]}...")
        
        # 第3步：提取主要角色
        print("\n[3/5] 提取主要角色及关系...")
        characters = await converter.extract_main_characters(novel_data, openai_key)
        print(f"✅ 提取到 {len(characters)} 个主要角色")
        for i, char in enumerate(characters, 1):
            print(f"   - {i}. {char.get('name')} ({char.get('role')}): {char.get('traits', '')[:50]}")
        
        # 第4步：分析章节结构
        print("\n[4/5] 分析章节结构与场景...")
        chapter_outline = await converter.analyze_chapter_structure(novel_data, openai_key)
        print(f"✅ 分析了 {len(chapter_outline)} 章")
        for chapter in chapter_outline:
            scenes = chapter.get('scene_breakdown', [])
            print(f"   章节{chapter.get('chapter')}: {chapter.get('chapter_title')}")
            print(f"   - 小叙: {chapter.get('summary', '')[:60]}...")
            print(f"   - 关键人物: {', '.join(chapter.get('key_characters', []))}")
            print(f"   - 冲突: {chapter.get('major_conflict', '')[:60]}...")
            print(f"   - 场景数: {len(scenes)}")
        
        # 第5步：生成完整剧本（包含分析结果）
        print("\n[5/5] 生成短剧剧本（集成分析结果）...")
        script = await converter.generate_drama_package(
            novel_data,
            novel_id,
            openai_key,
            prompt_override=None
        )
        print(f"✅ 剧本标题: {script.get('title')}")
        print(f"✅ 剧本类型: {script.get('genre')}")
        print(f"✅ 场景数: {len(script.get('scenes', []))}")
        
        # 验证集成结果
        print("\n[验证] 集成的分析结果...")
        has_synopsis = "synopsis" in script and script.get("synopsis")
        has_characters = "main_characters" in script and len(script.get("main_characters", [])) > 0
        has_outline = "chapter_outline" in script and len(script.get("chapter_outline", [])) > 0
        
        print(f"✅ 简介已集成: {has_synopsis}")
        print(f"✅ 角色已集成: {has_characters}")
        print(f"✅ 章节已集成: {has_outline}")
        
        # 计算统计信息
        print("\n[统计] 剧本内容...")
        total_scenes = len(script.get('scenes', []))
        for i, scene in enumerate(script.get('scenes', []), 1):
            content = scene.get('content', '')
            dialogue_count = content.count(':')
            print(f"   场景{i} - {scene.get('title')}: {len(content)} 字符, ~{dialogue_count//2} 句对白")
        
        # 保存测试结果
        result = {
            "status": "success",
            "novel_id": novel_id,
            "title": novel_data.get("title"),
            "synopsis": synopsis,
            "characters_count": len(characters),
            "chapters_count": len(chapter_outline),
            "scenes_count": len(script.get('scenes', [])),
            "script_generated": True,
            "integrated_analysis": {
                "has_synopsis": has_synopsis,
                "has_characters": has_characters,
                "has_outline": has_outline
            }
        }
        
        return result
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "status": "failed",
            "novel_id": novel_id,
            "error": str(e)
        }


async def main():
    """主测试函数"""
    openai_key = os.getenv("OPENAI_API_KEY", "")
    
    if not openai_key:
        print("❌ 缺少 OPENAI_API_KEY 环境变量")
        print("请设置环境变量: set OPENAI_API_KEY=your_key_here")
        sys.exit(1)
    
    # 选择几个不同类型的小说进行测试
    test_novels = [
        "安全屋",  # 系统流
        "第一章：毒舌影帝的逆袭",  # 娱乐圈
    ]
    
    results = []
    
    for novel_id in test_novels:
        try:
            result = await test_single_novel(novel_id, openai_key)
            results.append(result)
        except Exception as e:
            print(f"\n❌ 测试异常: {str(e)}")
            results.append({
                "status": "error",
                "novel_id": novel_id,
                "error": str(e)
            })
        
        # 避免 API 限流
        await asyncio.sleep(2)
    
    # 汇总结果
    print("\n" + "="*80)
    print("📊 测试汇总")
    print("="*80)
    
    success_count = sum(1 for r in results if r.get("status") == "success")
    failed_count = sum(1 for r in results if r.get("status") in ["failed", "error"])
    
    print(f"\n总体成功: {success_count}/{len(results)}")
    print(f"总体失败: {failed_count}/{len(results)}")
    
    print("\n详细结果:")
    for result in results:
        status_icon = "✅" if result.get("status") == "success" else "❌"
        print(f"\n{status_icon} {result.get('novel_id')}")
        if result.get("status") == "success":
            print(f"   - 简介: {result.get('synopsis', {}).get('genre', 'N/A')}")
            print(f"   - 角色数: {result.get('characters_count', 0)}")
            print(f"   - 章节数: {result.get('chapters_count', 0)}")
            print(f"   - 场景数: {result.get('scenes_count', 0)}")
            integrated = result.get('integrated_analysis', {})
            print(f"   - 集成简介: {integrated.get('has_synopsis', False)}")
            print(f"   - 集成角色: {integrated.get('has_characters', False)}")
            print(f"   - 集成章节: {integrated.get('has_outline', False)}")
        else:
            print(f"   - 错误: {result.get('error', 'Unknown error')}")
    
    # 保存测试报告
    report_path = Path(__file__).parent / "test_drama_package_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "test_date": str(Path(__file__).stat().st_mtime),
            "total_tests": len(results),
            "success": success_count,
            "failed": failed_count,
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 测试报告已保存到: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
