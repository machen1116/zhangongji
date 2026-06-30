// update_tags.js
// 批量更新 data.js 的 tagText 字段
// 用法：node update_tags.js data.js

const fs = require('fs');
const path = process.argv[2] || 'data.js';

// 分类规则
function classifyTag(question) {
    const q = (question || '').trim();
    
    // 规则1：核心考点
    const coreKeys = ['基本原则', '核心', '本质', '特征', '规定', '根本', '基本制度'];
    for (const k of coreKeys) {
        if (q.includes(k)) return '核心考点';
    }
    
    // 规则2：易错
    const trickyKeys = ['下列', '不属于', '错误', '不包括', '不正确的是', '错误的是', '不正确的是'];
    for (const k of trickyKeys) {
        if (q.includes(k)) return '易错';
    }
    
    // 规则3：难点
    const hardKeys = ['关系', '区别', '如何理解', '为什么说', '理论', '内涵'];
    for (const k of hardKeys) {
        if (q.includes(k)) return '难点';
    }
    
    // 默认：考点
    return '考点';
}

// 读取并执行 data.js，得到 cardData
const content = fs.readFileSync(path, 'utf8');
const fn = new Function(content + '\nreturn cardData;');
const cardData = fn();

// 统计
let total = 0;
let updated = 0;
const tagCount = {};

// 遍历所有卡片
for (const catKey of Object.keys(cardData)) {
    const cat = cardData[catKey];
    if (!cat || !cat.subjects) continue;
    for (const subjKey of Object.keys(cat.subjects)) {
        const subj = cat.subjects[subjKey];
        if (!subj || !subj.chapters) continue;
        for (const ch of subj.chapters) {
            if (!ch || !ch.cards) continue;
            for (const card of ch.cards) {
                total++;
                const oldTag = card.tagText || '';
                const newTag = classifyTag(card.question);
                if (oldTag !== newTag) {
                    card.tagText = newTag;
                    updated++;
                }
                tagCount[newTag] = (tagCount[newTag] || 0) + 1;
            }
        }
    }
}

console.log('📊 处理完成：');
console.log(`  总卡片数：${total}`);
console.log(`  更新标签数：${updated}`);
console.log('\n📋 标签分布：');
for (const [tag, count] of Object.entries(tagCount).sort((a, b) => b[1] - a[1])) {
    console.log(`  ${tag}：${count} 张`);
}

// 写回 data.js（保持原有格式）
const lines = [];
lines.push('// ==================== 数据配置区 ====================');
lines.push('// 学科结构：每个学科包含 subjects（学科字典），每个学科包含 chapters（章节数组），每个章节包含 cards');
lines.push('const cardData = {');

for (const catKey of Object.keys(cardData)) {
    const cat = cardData[catKey];
    lines.push(`    "${catKey}": {`);
    lines.push(`        "name": "${cat.name}",`);
    lines.push(`        "subjects": {`);
    
    for (const subjKey of Object.keys(cat.subjects)) {
        const subj = cat.subjects[subjKey];
        lines.push(`            "${subjKey}": {`);
        lines.push(`                "name": "${subj.name}",`);
        lines.push(`                "chapters": [`);
        
        for (let ci = 0; ci < subj.chapters.length; ci++) {
            const ch = subj.chapters[ci];
            lines.push(`                    {`);
            lines.push(`                        "title": "${ch.title}",`);
            lines.push(`                        "cards": [`);
            
            for (let cci = 0; cci < ch.cards.length; cci++) {
                const card = ch.cards[cci];
                lines.push(`                            {`);
                lines.push(`                                "question": "${card.question.replace(/"/g, '\\"')}",`);
                lines.push(`                                "answer": "${card.answer.replace(/"/g, '\\"').replace(/\n/g, '\\n')}"`);
                if (card.tagText) {
                    lines[lines.length - 1] += ',';
                    lines.push(`                                "tagText": "${card.tagText}"`);
                }
                if (card.difficulty) {
                    lines[lines.length - 1] += ',';
                    lines.push(`                                "difficulty": ${card.difficulty}`);
                }
                if (card.analysis) {
                    lines[lines.length - 1] += ',';
                    lines.push(`                                "analysis": "${card.analysis.replace(/"/g, '\\"').replace(/\n/g, '\\n')}"`);
                }
                if (card.expansion) {
                    lines[lines.length - 1] += ',';
                    lines.push(`                                "expansion": "${card.expansion.replace(/"/g, '\\"').replace(/\n/g, '\\n')}"`);
                }
                lines.push(`                            }${cci < ch.cards.length - 1 ? ',' : ''}`);
            }
            
            lines.push(`                        ]`);
            lines.push(`                    }${ci < subj.chapters.length - 1 ? ',' : ''}`);
        }
        
        lines.push(`                ]`);
        lines.push(`            }${Object.keys(cat.subjects).indexOf(subjKey) < Object.keys(cat.subjects).length - 1 ? ',' : ''}`);
    }
    
    lines.push(`        }`);
    lines.push(`    }${Object.keys(cardData).indexOf(catKey) < Object.keys(cardData).length - 1 ? ',' : ''}`);
}

lines.push('};');
lines.push('');
lines.push('// ==================== Node 环境兼容 ====================');
lines.push('if (typeof module !== "undefined" && module.exports) {');
lines.push('    module.exports = cardData;');
lines.push('}');

// 备份
const bak = path + '.bak';
fs.copyFileSync(path, bak);
console.log(`\n✅ 已备份：${bak}`);

// 写入
fs.writeFileSync(path, lines.join('\n'), 'utf8');
console.log(`✅ 已更新：${path}`);
console.log('\n提示：刷新浏览器即可看到更新后的标签。');
