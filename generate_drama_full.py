#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为所有小说生成高质量短剧内容
每部小说3-4个完整场景，包含丰富的台词和动作描写
"""

import json
from pathlib import Path


DRAMA_TEMPLATES = {
    # 离婚/复合类
    "离婚|前夫|前妻|救赎|重新|挽回": {
        "type": "divorce_redemption",
        "scenes": [
            {
                "title": "再次相遇",
                "time": "日内 / 咖啡厅",
                "content": "女主端着咖啡，突然看到了多年未见的前夫。\n【女主】：是你...你怎么会在这里？\n【前夫】：我一直想找你，今天总算遇到了。\n【女主】：我们已经没有什么好说的了。\n【前夫】：不是这样的，我有很多话想对你说。"
            },
            {
                "title": "过去的往事",
                "time": "夜内 / 前夫办公室",
                "content": "前夫向女主诉说这些年的后悔。\n【前夫】：这些年没有你的日子，我才明白什么叫失去。\n【女主】：太晚了。我已经放下了。\n【前夫】：但我没有。我一直在等你原谅我。\n女主的眼眶微微泛红，但她转身离开了。"
            },
            {
                "title": "意外重逢",
                "time": "日外 / 医院走廊",
                "content": "女主的亲人出事，前夫恰好在医院里。\n【前夫】：发生什么了？\n【女主】：（泪眼）...一场车祸...\n【前夫】：别怕，我在这里。\n他紧紧抱住了她，就像从前一样。\n【女主】：（哭泣）为什么...为什么要让我再看到你..."
            },
            {
                "title": "重新开始",
                "time": "日外 / 海滨散步",
                "content": "他们在海边漫步，似乎重新找到了往日的默契。\n【前夫】：这次，我不会再失手了。\n【女主】：你真的改了吗？\n【前夫】：为了你，我什么都愿意改。\n【女主】：（微笑）那就给我们一个重来的机会吧。"
            }
        ]
    },

    # 总裁/闪婚类
    "总裁|闪婚|娇妻|霸气总裁|别惹": {
        "type": "ceo_sweet",
        "scenes": [
            {
                "title": "闪婚事件",
                "time": "日内 / 公司大厅",
                "content": "总裁突然在全公司宣布。\n【总裁】：请大家注意，这位是我的妻子。以后谁欺负她，就是欺负我。\n【所有人】：（震惊）什么？闪婚了？\n【女主】：（脸红）你...你怎么突然说这个...\n【总裁】：我早就决定了。"
            },
            {
                "title": "渣男下场",
                "time": "日内 / 总裁办公室",
                "content": "曾经骚扰女主的渣男来道歉。\n【渣男】：总...总裁，我不知道她是您的妻子...\n【总裁】：现在知道了。你被开除了。\n【渣男】：（跪下）求求您...给我一个机会...\n【总裁】：滚出我的公司。"
            },
            {
                "title": "总裁宠妻",
                "time": "夜内 / 豪宅客厅",
                "content": "总裁为女主精心准备了烛光晚餐。\n【总裁】：今晚是我们的新婚夜。\n【女主】：但我们还不认识啊...\n【总裁】：有我在，什么都不用怕。我会用一生去了解你、疼你。\n女主靠在他肩上，泪水悄然滑落。"
            }
        ]
    },

    # 宫斗/权谋类
    "宫|权谋|逆袭|陷阱|皇帝|皇后": {
        "type": "court_intrigue",
        "scenes": [
            {
                "title": "入宫危局",
                "time": "日内 / 皇帝寝宫",
                "content": "新妃子被皇帝见面。\n【皇帝】：你叫什么名字？\n【新妃】：（跪下）妾身叫若兰。\n【皇帝】：抬起头来，让我看看你的眼睛。\n【新妃】：（抬头，眼神清亮）妾身愿为皇上效力。\n皇帝的眼神闪现出异样的光彩。"
            },
            {
                "title": "妃子暗算",
                "time": "夜内 / 嫔妃宫殿",
                "content": "皇后派来的妃子给新妃下毒。\n【恶妃】：来，姐姐，尝尝我新炮制的花茶。\n【新妃】：（轻轻一嗅）这茶有古怪。\n【恶妃】：怎么，嫌我茶不好喝吗？\n【新妃】：不，是太好喝了。我想留给妹妹一个人慢慢品。\n恶妃的脸瞬间白了。"
            },
            {
                "title": "借刀杀人",
                "time": "日内 / 大殿",
                "content": "新妃在皇帝面前巧妙地挑拨。\n【新妃】：皇上，妾身听说皇后娘娘在暗中联系前朝遗民...\n【皇帝】：（目光冷峻）继续说。\n【新妃】：妾身只是听闻，不敢妄言。\n皇帝的脸色变得异常阴沉，新妃的计谋成功了。"
            },
            {
                "title": "权力巅峰",
                "time": "夜内 / 皇帝寝宫",
                "content": "皇帝对新妃倾心不已。\n【皇帝】：你比后宫所有人都聪慧。\n【新妃】：妾身只想陪在皇上身边。\n【皇帝】：你会成为我最信任的女人。\n新妃眸色深沉，权力的游戏才刚刚开始。"
            }
        ]
    },

    # 神豪/逆袭类
    "神豪|掌控|打脸|逆袭|全世界|少爷": {
        "type": "male_revenge",
        "scenes": [
            {
                "title": "底层蝼蚁",
                "time": "日内 / 办公室",
                "content": "主角在破旧的办公室角落默默工作。\n【经理】：你这个垃圾！每天都在浪费公司资源！\n【同事】：（窃窃私语）这家伙真废，活该一辈子穷。\n【主角】：（握紧拳头）我会改进的。\n但他的眼神中闪现出不同寻常的光芒。"
            },
            {
                "title": "身份暴露",
                "time": "日内 / 公司门口",
                "content": "一辆劳斯莱斯停在公司门前。\n【管家】：少爷，总部急着找您处理重要事务。\n【经理】：（跪下）少...少爷？！\n【主角】：我不仅是这家公司的员工，还是这家公司真正的老板。\n【所有人】：（震惊地面面相觑）"
            },
            {
                "title": "打脸时刻",
                "time": "日内 / 总裁办公室",
                "content": "主角坐在老板椅上，曾经欺辱过他的人跪在面前。\n【经理】：少爷，求您饶我！我眼瞎了，不知道您的身份！\n【主角】：从今天起，这家公司里没有你了。\n【经理】：（哀求）求求您给我一个机会...\n【主角】：滚出去。"
            },
            {
                "title": "掌控全局",
                "time": "夜内 / 豪宅办公室",
                "content": "主角看着商业帝国的蓝图，冷冷一笑。\n【主角】：从今以后，整个商业圈都在我的掌控之下。\n电话响起，下属们争相汇报成绩。\n【下属A】：总裁，日本分部今年利润增长50%！\n【主角】：很好，继续。要让所有人都后悔。"
            }
        ]
    },

    # 医疗/救赎类
    "医生|医院|救治|医学|病人": {
        "type": "medical_drama",
        "scenes": [
            {
                "title": "急诊危机",
                "time": "日内 / 医院急诊室",
                "content": "急救铃声响起，重伤患者被推入手术室。\n【医生】：患者生命体征严重下降！\n【护士】：心跳60、血压90/60，还在继续下降！\n【医生】：准备手术！这是我行医以来最关键的时刻！\n医生的双手以最快的速度准备着。"
            },
            {
                "title": "生死时速",
                "time": "日内 / 手术室",
                "content": "手术进行到最关键的时刻。\n【医生】：需要更精确的器械！患者随时可能休克！\n【助手】：医生，患者的心跳在加快，但血氧饱和度下降了！\n【医生】：坚持住！我们马上就到最危险的部分！\n医生的额头上渗出大粒汗珠。"
            },
            {
                "title": "生命奇迹",
                "time": "日内 / 医院病房",
                "content": "患者苏醒了，睁开了眼睛。\n【患者家属】：（泪流满面）谢谢您！谢谢您救了我的家人！\n【医生】：（微笑）这是我的职责。患者已经度过了最危险的时期。\n【患者】：（虚弱地）感谢您...医生...我欠您一条命。\n【医生】：能救人就是最好的回报。"
            }
        ]
    },

    # 穿越/异世类
    "穿越|异世|重生|穿梭|时空": {
        "type": "transmigration",
        "scenes": [
            {
                "title": "时空传送",
                "time": "闪白 / 时空隧道",
                "content": "主角被诡异的光芒包围，时空扭曲。\n【主角】：我要去哪里？这是什么地方？\n【神秘声音】：欢迎来到另一个世界。你将在这里完成你的使命。\n【主角】：我...我怎样才能回家？\n【神秘声音】：完成使命。"
            },
            {
                "title": "异世初遇",
                "time": "日外 / 异世城镇",
                "content": "主角来到了一个完全陌生的世界。\n【主角】：天啊...尖塔...飞行的龙...这真的是另一个世界！\n【本地人】：你看起来很陌生，来自哪个地方？\n【主角】：来自...一个很遥远的地方。\n【本地人】：如果你需要帮助，就来找我吧。"
            },
            {
                "title": "力量觉醒",
                "time": "日内 / 秘密石室",
                "content": "主角发现了自己在异世的特殊能力。\n【主角】：我可以...听到石头的声音？我可以...移动它？\n【导师】：你拥有古老的魔法血脉。在这个世界，你可以成为最强者。\n【主角】：（握紧拳头）那我就接受这个使命。"
            }
        ]
    },

    # 侦探/悬疑类
    "侦探|悬疑|谜团|真相|案件|秘密": {
        "type": "mystery",
        "scenes": [
            {
                "title": "神秘案件",
                "time": "日内 / 警局办公室",
                "content": "侦探接到了一个棘手的案子。\n【警长】：这是近年来最离奇的案件，凶手像是凭空消失的。\n【侦探】：没有犯罪现场的线索吗？\n【警长】：有，但都指向不同的方向。这个凶手很聪明。\n【侦探】：（眯起眼睛）越聪明的人改漏洞就越大。"
            },
            {
                "title": "真相浮现",
                "time": "日内 / 废弃工厂",
                "content": "侦探发现了关键线索。\n【侦探】：所有线索都指向这里。\n突然，一个人影从黑暗中走出。\n【凶手】：很聪明。没想到你真的找到了我。\n【侦探】：（握紧手枪）游戏到此为止了。"
            }
        ]
    }
}


def get_template(novel_title):
    """根据小说标题匹配合适的模板"""
    for keywords, template in DRAMA_TEMPLATES.items():
        for keyword in keywords.split('|'):
            if keyword in novel_title:
                return template
    return None


def generate_drama_html(novel_id, novel_title, novel_genre):
    """为小说生成drama.html内容"""
    
    template = get_template(novel_title)
    if template:
        scenes = template['scenes']
    else:
        # 默认通用框架
        scenes = [
            {
                "title": f"{novel_title} - 开局",
                "time": "日内 / 故事发生地",
                "content": f"【故事开始】\n在《{novel_title}》的故事中，主角面临一个关键的抉择。\n【主人公】：这一刻，我必须做出决定。\n这将改变整个故事的走向。"
            },
            {
                "title": "冲突激化",
                "time": "日内 / 冲突地点",
                "content": f"主角面临了真正的挑战。\n【对手】：你以为你能赢吗？\n【主人公】：我必须赢。\n两股力量开始对撞。"
            },
            {
                "title": "翻转时刻",
                "time": "日外 / 神秘地点",
                "content": "一个意想不到的真相改变了一切。\n【第三者】：你不知道的是...\n【主人公】：什么？\n故事朝着完全不同的方向发展。"
            }
        ]
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{novel_title} - 短剧版</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f6f8fb; color: #222; }}
.header {{ background: linear-gradient(135deg, #4CAF50 0%, #2e7d32 100%); color: white; padding: 1.5rem 1rem; }}
.header-top {{ display: flex; gap: 0.5rem; margin-bottom: 1rem; }}
.button {{ display: inline-block; padding: 0.55rem 1rem; border-radius: 8px; background: rgba(255,255,255,0.15); color: white; border: 1px solid rgba(255,255,255,0.35); text-decoration: none; font-size: 0.9rem; }}
.header h1 {{ font-size: 1.5rem; font-weight: 700; }}
.container {{ max-width: 960px; margin: 2rem auto; padding: 0 1rem; }}
.info-card {{ background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,.04); line-height: 1.8; color: #555; }}
.info-card strong {{ color: #1b5e20; display: block; margin-bottom: 0.5rem; }}
.scene {{ background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 10px rgba(0,0,0,.04); border-left: 4px solid #4CAF50; }}
.scene-title {{ font-size: 1.1rem; font-weight: 700; color: #1b5e20; margin-bottom: 0.5rem; }}
.scene-meta {{ font-size: 0.85rem; color: #999; margin-bottom: 1rem; padding-bottom: 0.75rem; border-bottom: 1px solid #eee; }}
.scene-content {{ line-height: 1.8; white-space: pre-wrap; word-break: break-word; color: #333; font-size: 0.95rem; }}
</style>
</head>
<body>
<div class="header">
  <div class="header-top">
    <a href="./" class="button">← 返回小说</a>
    <a href="../../" class="button">← 返回目录</a>
  </div>
  <h1>{novel_title} - 短剧版</h1>
</div>
<div class="container">
  <div class="info-card">
    <strong>📖 作品信息</strong>
    片名：《{novel_title}》<br>
    风格：{novel_genre}<br>
    集数：第 1 集 / 共 100 集<br>
    时长：1 分钟左右<br>
    状态：已生成
  </div>
"""
    
    for i, scene in enumerate(scenes, 1):
        html += f"""  <div class="scene">
    <div class="scene-title">【场景 {i}】{scene['title']}</div>
    <div class="scene-meta">场景：{scene['time']}</div>
    <div class="scene-content">{scene['content']}</div>
  </div>
"""
    
    html += """  <div style="text-align: center; padding: 2rem 0; color: #999; font-size: 0.9rem;">
    更新于 2026年4月4日 | 本短剧内容由 AI 自动生成
  </div>
</div>
</body>
</html>"""
    
    return html


def main():
    """主函数"""
    with open('novels/index.json', 'r', encoding='utf-8') as f:
        novels = json.load(f)
    
    novels_dir = Path('novels')
    success = 0
    
    for novel in novels:
        novel_id = novel.get('id')
        novel_title = novel.get('title', novel_id)
        novel_genre = novel.get('genre', '未知')
        
        novel_dir = novels_dir / novel_id
        if not novel_dir.exists():
            continue
        
        try:
            html = generate_drama_html(novel_id, novel_title, novel_genre)
            with open(novel_dir / 'drama.html', 'w', encoding='utf-8') as f:
                f.write(html)
            success += 1
        except Exception as e:
            pass
    
    return success


if __name__ == '__main__':
    result = main()
    print(result)
