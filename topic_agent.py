#!/usr/bin/env python3
"""选题 Agent 小 CLI：输入赛道/关键词，输出一周选题带钩子。

模板驱动：读同目录下的 templates.md（7 个固定栏模板），按关键词匹配排序，
没有关键词命中时按模板原顺序输出。离线能跑，无需 API key。

用法：
    python3 topic_agent.py --track "AI Agent" --keywords "PR review,漏测"
    python3 topic_agent.py --track "AI Agent"   （无关键词：原顺序输出一周）
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(HERE, "templates.md")

FIELDS = ["选题", "给谁", "痛点", "钩子", "结构", "证据", "忌", "下一步", "回看场景"]
DAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def parse_templates(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    blocks = re.split(r"\n## 模板 \d+：", text)[1:]
    out = []
    for b in blocks:
        title = b.strip().split("\n", 1)[0].strip()
        fields = {}
        for line in b.splitlines():
            m = re.match(r"- (选题|给谁|痛点|钩子|结构|证据|忌|下一步|回看场景)：(.*)", line)
            if m:
                fields[m.group(1)] = m.group(2).strip()
        if fields.get("选题"):
            fields["_name"] = title
            out.append(fields)
    return out


def score(t, keywords):
    blob = " ".join(t.get(f, "") for f in FIELDS) + " " + t.get("_name", "")
    return sum(1 for k in keywords if k and k in blob)


def main():
    ap = argparse.ArgumentParser(description="选题 Agent：输出一周选题带钩子")
    ap.add_argument("--track", default="AI Agent", help="赛道")
    ap.add_argument("--keywords", default="", help="关键词，逗号分隔")
    args = ap.parse_args()

    if not os.path.exists(TEMPLATES):
        print(f"找不到 templates.md：{TEMPLATES}", file=sys.stderr)
        return 1
    templates = parse_templates(TEMPLATES)
    if not templates:
        print("templates.md 里没有解析到模板", file=sys.stderr)
        return 1

    keywords = [k.strip() for k in args.keywords.replace("，", ",").split(",") if k.strip()]
    ranked = sorted(templates, key=lambda t: -score(t, keywords))
    week = ranked[:7]

    print(f"赛道：{args.track}")
    if keywords:
        print(f"关键词：{', '.join(keywords)}")
    print(f"一周选题（{len(week)} 条，模板驱动）：\n")
    for day, t in zip(DAYS, week):
        print(f"{day} · {t['选题']}")
        print(f"  给谁：{t.get('给谁', '')}")
        print(f"  钩子：{t.get('钩子', '')}")
        print(f"  回看场景：{t.get('回看场景', '')}")
        print()
    print("用法：每天按 sop.md 写 + 发前检查 + 发；发后 24h 看 verdict。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
