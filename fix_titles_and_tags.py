#!/usr/bin/env python3
"""
修复小说列表中的目录名和标签显示问题
1. 将英文目录名转换为可读的中文格式
2. 为所有小说补充标签信息
"""

import json
import os
from pathlib import Path

def convert_slug_to_title(slug):
    """将目录名转换为可读的标题"""
    # 常见目录名的映射表
    known_titles = {
        'apocalypse-food': '末世之粮',
        'bingjiao-wife': '病娇妻子的秘密',
        'caogaozhi': '什么？！我的草稿纸成国家机密了',
        'chaos-prince': '混沌王子的诈尸',
        'coushu-dashu': '凑数大叔的非凡人生',
        'dao-qiang': '废物逆袭：我的倒反天罡',
        'diss-world': '全网Diss世界',
        'dnf-fanli': '地下城的翻莉奇遇',
        'duoyun-jietu': '多云借图',
        'emperor-qixia': '七侠皇帝的野心',
        'fanpai-novel': '反派小说的救赎',
        'fanpai-qian': '反派前传',
        'fanpai-xian': '反派仙途',
        'gaoleng-exwife': '冷血前夫的救赎',
        'gaowu-qiandao': '高武起道',
        'gongluexitong': '攻略系统的秘密',
        'haneast-luyike': '韩东方的路易克',
        'history-immortal': '历史仙途',
        'hokage-rokudao': '火影六道的轮回',
        'honkai-star-rail-mirror': '崩坏：星轨镜像',
        'jiaqian-ice': '假前冰心',
        'juedingzisha': '绝情自杀',
        'kaijug_shisigjing': '怪兽师者竞技',
        'los-angeles-exorcism': '洛杉矶驱魔事件',
        'lottery-170million': '彩票1.7亿的秘密',
        'luoshanji-zhuomo': '罗刹鸡着魔',
        'meimo-challenge': '眉墨挑战',
        'mingyi-afraidof': '名医害怕什么',
        'mingyi-han-daDan': '名医韩大蛋',
        'mingyi-kshan': '名医K善',
        'naruto-deadth': '火影死亡轮',
        'nvpin-bqz': '女频白绮梓',
        'nvzon-fallenhusband': '女尊坠夫',
        'pokemon-mofeng': '宝可梦魔风',
        'rule-horror-campus': '规则恐怖校园',
        'safe-house': '安全屋',
        'sanjiaozhou-lie_sha': '三角州列杀',
        'sanjiaozhou-wife': '三角州妻子',
        'shenhaoxitum': '深号系统',
        'shuihu-xixue': '水浒西血',
        'sishe-fang': '寺舍坊',
        'six-wing-angel': '六翼天使',
        'tengu-tokyo': '天狗东京',
        'tianfu-cha': '天赋茶',
        'tongwei-chief': '通威族长',
        'wanrenmidaxia': '万人迷大侠',
        'well-dragon': '井龙',
        'wuxia-npc': '武侠NPC的逆袭',
        'xianqi-jiandao': '仙气剑道',
        'xiyou-meifu': '西游美妇',
        'yiyi-yisheng': '一一医生',
        'yule-fanpai': '娱乐反派',
        'zangqing救人': '藏情救人',
        'zhenbei-hou': '真北候',
        'zhenbeihou-daizha': '真北侯待杖',
        'zhengdao-yanfa': '正道研发',
        'zhongjiang_yi_qi_qi': '中将一起起',
        'zhuan-sheng-chose': '转生选择',
        'zibao-luxian': '自爆路仙',
        'zongwu-jiujian': '宗武九剑',
        'zongwu-zuxian': '宗武祖仙',
    }
    
    if slug in known_titles:
        return known_titles[slug]
    
    # 如果不在已知列表中，尝试用连字符生成一个可读的名字
    # 例如: some-random-title -> Some Random Title
    return slug.replace('-', ' ').title()

def get_genre_tag(novel_id):
    """根据小说ID获取分类标签，或返回默认分类"""
    # 可以根据需要扩展
    genre_map = {
        'rule-horror-campus': '恐怖',
        'hokage-rokudao': '机甲',
        'honkai-star-rail-mirror': '游戏',
        'pokemon-mofeng': '游戏',
    }
    return genre_map.get(novel_id, '都市/玄幻')

def fix_titles_and_tags():
    """修复 index.json 中的标题和标签"""
    index_file = 'novels/index.json'
    
    with open(index_file, 'r', encoding='utf-8') as f:
        novels = json.load(f)
    
    updated_count = 0
    
    for novel in novels:
        old_title = novel.get('title', '')
        old_genre = novel.get('genre', '都市/玄幻')
        
        # 检查是否需要修复标题（英文目录名形式）
        if old_title and old_title.replace('-', '').replace('_', '').islower() and len(old_title.split('-')) > 1:
            # 这看起来是一个目录名
            new_title = convert_slug_to_title(novel['id'])
            if new_title != old_title:
                print(f"📝 修复标题: {old_title} -> {new_title}")
                novel['title'] = new_title
                updated_count += 1
        
        # 添加标签信息（如果没有）
        if 'tags' not in novel:
            novel['tags'] = [old_genre.split('/')[0]] if old_genre else ['都市']
    
    # 保存回文件
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(novels, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 修复完成！共更新了 {updated_count} 个小说标题")
    print(f"📁 文件已保存: {index_file}")

if __name__ == '__main__':
    fix_titles_and_tags()
