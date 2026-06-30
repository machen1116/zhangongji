#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量更新 data.js 标签（tagText）
规则：
  1. 包含"基本原则"、"核心"、"本质"、"特征"、"规定" → 核心考点
  2. 包含"下列"、"不属于"、"错误"、"不包括"、"不正确的是" → 易错
  3. 包含"关系"、"区别"、"如何理解"、"为什么说"、"理论" → 难点
  4. 其他 → 考点（保持默认）
"""

import sys, os, re

def read_js(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_js(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ 已写入：{path}")

def classify_tag(question):
    """根据问题内容判断标签"""
    q = question.strip()
    # 规则1：核心考点
    core_keys = ["基本原则", "核心", "本质", "特征", "规定", "根本", "基本制度", "基本原则"]
    for k in core_keys:
        if k in q:
            return "核心考点"
    # 规则2：易错
    tricky_keys = ["下列", "不属于", "错误", "不包括", "不正确的是", "错误的是", "不正确的是"]
    for k in tricky_keys:
        if k in q:
            return "易错"
    # 规则3：难点
    hard_keys = ["关系", "区别", "如何理解", "为什么说", "理论", "内涵", "如何理解"]
    for k in hard_keys:
        if k in q:
            return "难点"
    # 默认：考点
    return "考点"

def update_tags(js_content):
    """更新所有卡片的 tagText"""
    # 匹配每张卡片的对象
    # 格式："question": "....", "answer": "....", "tagText": "...."
    pattern = re.compile(
        r'(\s+"question":\s*")([^"]*)(",\s*"answer":\s*"[^"]*",\s*"tagText":\s*")([^"]*)(")',
        re.DOTALL
    )
    
    def repl(m):
        q = m.group(2)  # question 内容
        old_tag = m.group(4)  # 原 tagText
        new_tag = classify_tag(q)
        # 如果原标签已经是"核心考点"/"易错"/"难点"，保持不变
        if old_tag in ["核心考点", "易错", "难点"]:
            return m.group(0)
        # 否则更新为 new_tag
        return m.group(1) + q + m.group(3) + new_tag + m.group(5)
    
    new_content = pattern.sub(repl, js_content)
    return new_content

def main():
    if len(sys.argv) < 2:
        print("用法：python3 update_tags.py <data.js路径>")
        sys.exit(1)
    
    js_path = sys.argv[1]
    if not os.path.exists(js_path):
        print(f"❌ 文件不存在：{js_path}")
        sys.exit(1)
    
    # 备份
    bak = js_path + ".bak"
    import shutil
    shutil.copy2(js_path, bak)
    print(f"✅ 已备份：{bak}")
    
    print("🏷️  开始分析并更新标签...")
    content = read_js(js_path)
    new_content = update_tags(content)
    
    # 统计
    old_count = content.count('"tagText":')
    new_count = new_content.count('"tagText":')
    
    write_js(js_path, new_content)
    
    print(f"\n📊 统计：")
    print(f"  处理卡片数：{old_count}")
    print(f"  更新后卡片数：{new_count}")
    
    # 统计各标签数量
    for tag in ["考点", "核心考点", "易错", "难点"]:
        n = new_content.count(f'"tagText": "{tag}"')
        print(f"  {tag}：{n} 张")

if __name__ == "__main__":
    main()
