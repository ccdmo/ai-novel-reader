#!/usr/bin/env python3
import urllib.request
import json
import sys

api_key = "sk-cp-KG6ZNyxnLNH9xjQXgN5ta_pC3IA4gZZAif9IcRWnvt9PdJPVlRE0NXW1_h6j9_T2dwd5y1Dbox3NLh_oJO1lNlLNJ4SO3fXEenVzNLaxGpReltTxoRX2j44"

prompt = """请用简体中文写小说第一章，约3000字。

书名：《刚当皇帝，就被气运之子刺杀》
背景：玄幻修仙世界，九州大陆，大萧皇朝。

核心爽点：
- 皇帝身份反转：刚当上皇帝就被刺杀，逆天改命系统激活
- 气运之子与皇帝的天命对决
- 先被碾压再反杀的极致落差感
- 皇帝特有的权谋与武力双重碾压

金手指：「逆天改命系统」：被刺杀时觉醒，每次化解危机或击杀气运之子可获积分，积分兑换修为/技能/情报/神器，系统可预知下一次刺杀的时间和人物

核心人设：
- 萧烬：大萧皇朝新帝，年仅二十二岁登基，外表温润如玉，实则深沉似海。体内封印着上古帝王血脉（他自己不知）。
- 顾长歌：气运之子，携天雷之势的神秘年轻强者，天命所归，被天道眷顾，来刺杀新帝。

第一章钩子/期待感：
①新皇登基大典，万众瞩目，却遭遇气运之子顾长歌刺杀
②刺客实力碾压禁军，皇帝命悬一线
③"逆天改命系统"激活，逆天改命时刻到来
④悬念：顾长歌为何要刺杀新帝？背后有何阴谋？皇帝如何翻盘？

要求：
1. 语言流畅，网文风格，节奏紧凑
2. 开篇直接切入登基大典场景，金銮殿上，百官朝贺
3. 前500字内出现刺杀，节奏要快
4. 系统激活要有仪式感和震撼感
5. 必须在结尾留下强烈悬念：刺客的真实身份或目的
6. 标题：《第一章：朕刚登基，你就来刺杀？》
7. 约3000字"""

payload = json.dumps({
    "model": "MiniMax-Text-01",
    "tokens_to_generate": 4000,
    "messages": [{"role": "user", "content": prompt}],
    "bot_setting": [{"bot_name": "novel_writer", "content": "你是一个玄幻小说作家。"}]
}).encode('utf-8')

req = urllib.request.Request(
    "https://api.minimaxi.com/v1/text/chatcompletion_pro",
    data=payload,
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        if data.get("choices") and len(data["choices"]) > 0:
            print(data["choices"][0]["messages"][0]["content"])
        else:
            print("ERROR: No choices in response")
            print(json.dumps(data, ensure_ascii=False, indent=2), file=sys.stderr)
            sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
