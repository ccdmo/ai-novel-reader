#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json
import sys

prompt = """你是一个玄幻小说作家。请根据以下设定，创作小说《刚当皇帝，就被气运之子刺杀》的第一章，约3000字。

【核心设定】
- 书名：刚当皇帝，就被气运之子刺杀
- 题材：玄幻脑洞
- 核心爽点：①皇帝身份反转：刚当上皇帝就被刺杀，逆天改命系统激活 ②气运之子与皇帝的天命对决 ③先被碾压再反杀的极致落差感 ④皇帝特有的权谋与武力双重碾压
- 金手指：「逆天改命系统」：被刺杀时觉醒，每次化解危机或击杀气运之子可获积分，积分兑换修为/技能/情报/神器，系统可预知下一次刺杀的时间和人物
- 核心人设：主角萧烬（刚登基的皇帝）x 沉稳果决 x 帝王心术+绝对武力  顾长歌（气运之子）x 天选之人 x 携天雷之势前来刺杀
- 第一章钩子/期待感：①新皇登基大典，万众瞩目，却遭遇气运之子刺杀 ②刺客实力碾压禁军，皇帝命悬一线 ③系统激活，逆天改命时刻 ④悬念：刺客是谁？为何刺杀？皇帝如何翻盘？

【写作要求】
- 第一章约3000字，标题为"第一章：朕刚登基，你就来刺杀？"
- 语言流畅，网文风格，节奏紧凑
- 开篇直接切入登基大典场景
- 建立核心冲突：皇帝 VS 气运之子
- 系统激活要有仪式感
- 结尾留下悬念，钩住读者继续读第二章

请直接输出小说正文，不需要任何说明。"""

data = {
    "model": "MiniMax-Text-01",
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "max_tokens": 4096,
    "temperature": 0.8
}

body = json.dumps(data).encode("utf-8")
req = urllib.request.Request(
    "https://api.minimax.chat/v1/text/chatcompletion_pro?GroupId=123456",
    data=body,
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer "  # placeholder
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        content = result["choices"][0]["message"]["content"]
        print(content)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
