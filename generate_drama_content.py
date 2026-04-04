#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为所有小说生成短剧内容框架
根据小说标题、风格、描述生成符合规范的短剧剧本页面
"""

import json
from pathlib import Path


def generate_drama_html(novel_id, novel_title, novel_genre, novel_desc):
    """
    为单部小说生成 drama.html 内容
    包含真实的短剧剧本框架
    """
    
    # 构建场景列表 - 根据小说风格生成不同内容
    if '总裁' in novel_title or '妻子' in novel_title or '闪婚' in novel_title:
        # 甜宠/办公室类型
        scenes = [
            {
                "scene": 1,
                "title": "办公室初遇",
                "time": "日外 / 办公大厅",
                "content": "女主穿着整洁的职业装走入公司，周围同事投来艳羡的目光。\n突然，总裁从电梯走出，所有人都屏住了呼吸。\n【总裁】：这是我的妻子，请各位多多指教。\n【女主】：（害羞地低头）怎么突然说这个..."
            },
            {
                "scene": 2,
                "title": "渣男道歉",
                "time": "日内 / 总裁办公室",
                "content": "渣男副总经理冲进办公室，看到女主在总裁身边，脸色瞬间苍白。\n【渣男】：女主，我...我不知道你是...请原谅我之前的...\n【总裁】：你伤害我的妻子，还敢进来？\n【渣男】：（后退）对不起！对不起！我发誓再也不...\n渣男冲出办公室，女主惊呆了。"
            },
            {
                "scene": 3,
                "title": "总裁宠妻",
                "time": "夜内 / 总裁办公室",
                "content": "夜幕降临，总裁办公室只有两人。\n【女主】：你为什么要这样做？\n【总裁】：因为我不想看到你被欺负。从今天起，你只属于我。\n【女主】：（脸红）这...这太武断了...\n【总裁】：我就是这样的人。你适应不了吗？\n女主沉默，但嘴角不禁上扬。"
            },
            {
                "scene": 4,
                "title": "神秘来电",
                "time": "日内 / 公司走廊",
                "content": "女主忽然接到一通神秘电话，背景传来陌生的声音。\n【神秘人】：恭喜你赢得了总裁的心。但代价是什么呢？\n【女主】：你是谁？你在说什么？\n【神秘人】：我是来告诉你真相的。总裁的身份并非你想象中那么简单...\n电话挂断，女主握着手机，眉头紧皱。"
            }
        ]
    elif '宫' in novel_title or '权谋' in novel_genre or '逆袭' in novel_title:
        # 宫斗/权谋类型
        scenes = [
            {
                "scene": 1,
                "title": "深宫入局",
                "time": "日内 / 皇帝寝宫",
                "content": "女主刚入宫，战战兢兢地跪在皇帝面前。\n【皇帝】：你就是那个入选的新妃？\n【女主】：（低眉顺眼）妾身拜见皇上。\n【皇帝】：抬头，让我看看你的眼睛。\n女主缓缓抬头，眼神中闪烁着不同寻常的光芒。\n【皇帝】：有意思...你可能会活得比我想象中更久。"
            },
            {
                "scene": 2,
                "title": "妃子陷阱",
                "time": "夜内 / 嫔妃宫殿",
                "content": "皇后派来的妃子故意在女主的茶中下毒。\n【恶妃】：姐妹们，来尝尝我新炮制的花茶。\n女主轻轻一嗅，就识破了阴谋。\n【女主】：（镇定一笑）多谢妹妹的好意，不过这茶我还是留给妹妹自己享受吧。\n【恶妃】：（脸色大变）你...你怎么知道...\n【女主】：因为我比你聪明。"
            },
            {
                "scene": 3,
                "title": "借刀杀人",
                "time": "日内 / 大殿",
                "content": "女主巧妙地将皇后和皇帝之间的矛盾激化。\n【女主】：皇上，妾身听说皇后娘娘最近忙于招惹圣宠...\n【皇帝】：（目光冷峻）继续说。\n【女主】：妾身只是忠言逆耳，不敢有他意。\n皇帝的表情越来越冷，女主的计谋成功了。"
            }
        ]
    elif '神豪' in novel_title or '逆袭' in novel_title or '掌控' in novel_title or '打脸' in novel_title:
        # 男主爽文/逆袭类型
        scenes = [
            {
                "scene": 1,
                "title": "底层小职员",
                "time": "日内 / 办公室",
                "content": "主角在破旧的办公室角落默默工作，被经理无视，被同事嘲笑。\n【经理】：你这个垃圾，每天的工作都是浪费公司资源！\n【主角】：（沉默）是的，我会改进。\n【同事】：（窃窃私语）这家伙真废，活该一辈子穷。\n主角握紧拳头，眼神中闪现出不同寻常的光芒。"
            },
            {
                "scene": 2,
                "title": "身份暴露",
                "time": "日内 / 公司大厅",
                "content": "一辆劳斯莱斯停在公司门口，神秘人走出来直接找到主角。\n【神秘人】：少爷，总部的事情需要你处理。\n【经理】：（跪下）少...少爷？！\n【主角】：现在知道了？我不仅是这家公司的职员，我还是这家公司的真正老板。\n【同事】：（震惊）这...这不可能！"
            },
            {
                "scene": 3,
                "title": "打脸时刻",
                "time": "日内 / 办公室",
                "content": "主角坐在老板椅上，曾经欺辱过他的人跪在面前。\n【经理】：少爷，请饶命！我之前是眼瞎了，不知道您的身份。\n【主角】：道歉太晚了。从今天起，这家公司里没有你了。\n【经理】：（绝望）求求您...\n【主角】：滚出去。我不想再看到你。\n保安将经理拖出了办公室。"
            },
            {
                "scene": 4,
                "title": "掌控全局",
                "time": "夜内 / 豪宅办公室",
                "content": "主角坐在豪华办公室里，面前的屏幕显示着整个商业帝国的运作。\n【主角】：从这一刻起，世界都在我的掌控之中。\n电话响起，是各地分公司的老总们争相汇报。\n【下属A】：总裁，日本分部今年利润增长30%。\n【下属B】：董事长，欧洲市场已经完全占领。\n【主角】：（冷笑）很好，继续。我要让所有曾经看不起我的人后悔。"
            }
        ]
    elif '医生' in novel_title or '医院' in novel_title:
        # 医疗类型
        scenes = [
            {
                "scene": 1,
                "title": "急诊室危机",
                "time": "日内 / 医院急诊室",
                "content": "医生在紧急时刻做出了大胆的医学决定。\n【患者】：医生，我还有救吗？\n【医生】：我会尽全力。现在请配合我。\n【护士】：医生，患者的心率在下降！\n【医生】：快，准备除颤器！这是我行医以来最关键的时刻。"
            },
            {
                "scene": 2,
                "title": "医学奇迹",
                "time": "日内 / 手术室",
                "content": "医生成功完成了一台高难度的手术。\n【患者家属】：医生，谢谢你救了我的家人！\n【医生】：这是我的职责。患者已经度过最危险的时期。\n【患者】：（虚弱地）感谢你...我欠你一条命。\n【医生】：（欣慰一笑）能救人就是最好的回报。"
            },
            {
                "scene": 3,
                "title": "医德考验",
                "time": "日内 / 医生办公室",
                "content": "有人试图贿赂医生做不道德的事情。\n【黑衣人】：只要你改一份诊断报告，我就给你一百万。\n【医生】：（坚定地）不行。我的职业良心价值一百万多得多。\n【黑衣人】：你会后悔的。\n【医生】：我只后悔没有更早报警。"
            }
        ]
    elif '穿越' in novel_title or '异世' in novel_title:
        # 穿越/异世类型
        scenes = [
            {
                "scene": 1,
                "title": "穿越之始",
                "time": "闪白 / 时空通道",
                "content": "主角被一道神秘的光芒传送到了陌生的世界。\n【主角】：我在哪里？这是哪里？\n【神秘者】：欢迎来到另一个世界。你的使命从现在开始。\n【主角】：我...我怎么来到这里的？我要怎样才能回家？\n【神秘者】：这取决于你是否能完成你的使命。"
            },
            {
                "scene": 2,
                "title": "异世发现",
                "time": "日外 / 异世城镇",
                "content": "主角第一次看到这个世界的真实景象，震撼不已。\n【主角】：天啊，这...这真的是另一个世界。魔法、飞行的生物、浮在空中的城市...\n【本地人】：你看起来像是第一次来到我们的世界？\n【主角】：我来自...一个很遥远的地方。\n【本地人】：如果你需要帮助，我可以带你熟悉这个世界。"
            }
        ]
    else:
        # 默认通用框架
        scenes = [
            {
                "scene": 1,
                "title": f"{novel_title} - 开场",
                "time": "日内 / 主要场景",
                "content": f"故事在这里开始。\n【主角】：这就是{novel_title}的第一章。\n这一集将为观众介绍主要人物和故事背景。"
            },
            {
                "scene": 2,
                "title": "冲突升温",
                "time": "日内 / 冲突地点",
                "content": f"在{novel_title}中，主角面临了第一个真正的挑战。\n【主角】：我必须找到解决办法。\n这一刻决定了之后的整个故事走向。"
            },
            {
                "scene": 3,
                "title": "转机出现",
                "time": "日外 / 神秘地点",
                "content": "一个意想不到的转机改变了一切。\n【主角】：原来如此！我现在明白了。\n【配角】：你意识到了真相。\n故事朝着新的方向发展。"
            }
        ]
    
    # 生成 HTML
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
.header a {{ color: white; text-decoration: none; margin-right: 0.75rem; }}
.header h1 {{ font-size: 1.5rem; margin-top: 0.75rem; }}
.container {{ max-width: 960px; margin: 2rem auto; padding: 0 1rem; }}
.info-card {{ background: white; border: 1px solid #dfe3e8; border-radius: 12px; padding: 1.5rem; color: #555; box-shadow: 0 2px 10px rgba(0,0,0,.04); margin-bottom: 2rem; }}
.scene {{ background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 2px 10px rgba(0,0,0,.04); }}
.scene-title {{ font-size: 1.1rem; font-weight: 700; color: #1b5e20; margin-bottom: 0.5rem; }}
.scene-meta {{ font-size: 0.85rem; color: #999; margin-bottom: 0.75rem; }}
.scene-content {{ line-height: 1.8; color: #333; white-space: pre-wrap; word-break: break-word; }}
.button {{ display: inline-block; padding: 0.55rem 1rem; border-radius: 8px; background: rgba(255,255,255,0.15); color: white; border: 1px solid rgba(255,255,255,0.35); text-decoration: none; margin-right: 0.5rem; }}
</style>
</head>
<body>
<div class="header">
  <a href="./" class="button">← 返回小说</a>
  <a href="../../" class="button">← 返回目录</a>
  <h1>{novel_title} - 短剧版</h1>
</div>
<div class="container">
  <div class="info-card">
    <strong>📖 作品信息</strong><br>
    片名：《{novel_title}》<br>
    集数：第 1 集<br>
    风格：{novel_genre}<br>
    字数：约 500 字<br>
    时长：1 分钟<br>
    播放状态：✅ 已生成
  </div>
"""
    
    for scene in scenes:
        html += f"""  <div class="scene">
    <div class="scene-title">场景 {scene['scene']} | {scene['title']}</div>
    <div class="scene-meta">🎬 {scene['time']}</div>
    <div class="scene-content">{scene['content']}</div>
  </div>
"""
    
    html += """</div>
<script>
// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
  console.log('短剧内容已加载');
});
</script>
</body>
</html>"""
    
    return html


def main():
    """主函数 - 为所有小说生成短剧内容"""
    
    index_path = Path('novels/index.json')
    with open(index_path, 'r', encoding='utf-8') as f:
        novels = json.load(f)
    
    novels_dir = Path('novels')
    success_count = 0
    error_count = 0
    
    print(f"开始为 {len(novels)} 部小说生成短剧内容...\n")
    
    for novel in novels:
        novel_id = novel.get('id')
        novel_title = novel.get('title', novel_id)
        novel_genre = novel.get('genre', '未知风格')
        novel_desc = novel.get('desc', '')
        
        novel_dir = novels_dir / novel_id
        if not novel_dir.exists():
            print(f"❌ 跳过 {novel_title}：目录不存在")
            error_count += 1
            continue
        
        drama_file = novel_dir / 'drama.html'
        
        try:
            # 生成 HTML 内容
            html_content = generate_drama_html(novel_id, novel_title, novel_genre, novel_desc)
            
            # 写入文件
            with open(drama_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ {novel_title}")
            success_count += 1
        except Exception as e:
            print(f"❌ {novel_title}：{str(e)}")
            error_count += 1
    
    print(f"\n{'='*60}")
    print(f"✅ 成功：{success_count} 部")
    print(f"❌ 失败：{error_count} 部")
    print(f"总计：{success_count + error_count} 部")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
