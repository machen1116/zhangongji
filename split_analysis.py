#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拆分 data.js 中"新思想"部分的 answer 字段
从 answer 中提取【核心定义】和【考点提示】内容
生成新的 data.js，包含 answer 和 analysis 字段
"""

import re
import json

def split_answer(answer_text):
    """
    拆分 answer 字段
    返回 (answer, analysis)
    """
    if not answer_text:
        return answer_text, None
    
    # 初始化
    new_answer = answer_text
    analysis = None
    
    # 检查是否包含【核心定义】
    if '【核心定义】' in answer_text:
        # 提取【核心定义】后面的内容
        parts = answer_text.split('【核心定义】', 1)
        if len(parts) > 1:
            content = parts[1]
            # 检查是否包含【考点提示】
            if '【考点提示】' in content:
                answer_part, prompt_part = content.split('【考点提示】', 1)
                new_answer = answer_part.strip()
                analysis = prompt_part.strip()
            else:
                new_answer = content.strip()
    else:
        # 不包含【核心定义】，检查是否包含【考点提示】
        if '【考点提示】' in answer_text:
            parts = answer_text.split('【考点提示】', 1)
            new_answer = parts[0].strip()
            analysis = parts[1].strip()
    
    return new_answer, analysis

def process_data_file(input_file, output_file):
    """
    处理 data.js 文件
    """
    # 读取文件
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 JavaScript 变量赋值部分
    # 找到 const cardData = 开始的位置
    start_marker = 'const cardData = '
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("错误：找不到 cardData 定义")
        return False
    
    # 找到结束位置（最后一个分号）
    # 使用简单的正则提取 JSON 部分
    match = re.search(r'const cardData = ({.*});', content, re.DOTALL)
    if not match:
        print("错误：无法解析 cardData")
        return False
    
    json_str = match.group(1)
    
    # 解析 JSON（需要做一些处理，因为 JS 格式可能不是严格 JSON）
    # 使用 node.js 来解析
    try:
        import subprocess
        node_script = f"""
        const data = {json_str};
        console.log(JSON.stringify(data));
        """
        with open('/tmp/parse_data.js', 'w', encoding='utf-8') as f:
            f.write(node_script)
        
        result = subprocess.run(
            ['/Users/zhaochanghe/.workbuddy/binaries/node/versions/22.22.2/bin/node', '/tmp/parse_data.js'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Node.js 解析错误：{result.stderr}")
            return False
        
        card_data = json.loads(result.stdout)
        
    except Exception as e:
        print(f"解析错误：{e}")
        return False
    
    # 统计
    total_cards = 0
    split_cards = 0
    
    # 处理每张卡片
    for subject_key in card_data:
        subject = card_data[subject_key]
        if 'subjects' in subject:
            for subj_key, subj_value in subject['subjects'].items():
                if 'chapters' in subj_value:
                    for chapter in subj_value['chapters']:
                        if 'cards' in chapter:
                            for card in chapter['cards']:
                                total_cards += 1
                                if 'answer' in card:
                                    new_answer, analysis = split_answer(card['answer'])
                                    card['answer'] = new_answer
                                    if analysis:
                                        card['analysis'] = analysis
                                        split_cards += 1
    
    # 生成新的 JS 文件
    output_js = content[:start_idx + len(start_marker)] + json.dumps(card_data, ensure_ascii=False, indent=4) + ';\n'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_js)
    
    print(f"处理完成！")
    print(f"总卡片数：{total_cards}")
    print(f"拆分卡片数（含考点提示）：{split_cards}")
    print(f"新文件已保存：{output_file}")
    
    return True

if __name__ == '__main__':
    input_file = '/Users/zhaochanghe/Desktop/战公基-独立版/data-v16.js'
    output_file = '/Users/zhaochanghe/Desktop/战公基-独立版/data.js'
    
    print("开始拆分 answer 字段...")
    process_data_file(input_file, output_file)
