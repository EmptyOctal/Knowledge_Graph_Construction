import re

def to_sentence(words):
    """
    将分词与词性标注结果转换为字符串模式。
    """
    return ' '.join(f"{word}/{tag}" for word, tag in words)

NOUN_TAGS = {'n', 'nh', 'nl', 'ns', 'ni', 'nz'}  # 名词集合
ADJ_TAG = 'a'  # 形容词
VERB_TAG = 'v'  # 动词
TIME_TAG = 'nt'  # 时间名词
LOC_TAG = 'ns'  # 地点名词

def rule_verb_object_relation(sentence):
    """规则1：提取一般动宾结构"""
    triples = set()
    # 匹配模式：名词 + 动词 + 名词，且宾语后面不能是动词或形容词
    pattern = r'(\S+)/({}) (\S+)/v (\S+)/({}) (?!\S+/(v|a|d|u))'.format(
        '|'.join(NOUN_TAGS),  # 主语是名词类
        '|'.join(NOUN_TAGS)   # 宾语也是名词类
    )
    matches = re.finditer(pattern, sentence)
    for match in matches:
        subject = match.group(1)  # 主语
        verb = match.group(3)     # 动词
        obj = match.group(4)      # 宾语
        triples.add((subject, verb, obj))
    return triples


def rule_is_relation(sentence):
    """规则2：提取"A 是 B"的描述性关系"""
    triples = set()
    pattern = r'(\S+)/({}) 是/v (\S+)/({}) (?!\S+/(v|a|d|u))'.format('|'.join(NOUN_TAGS), '|'.join(NOUN_TAGS))
    matches = re.finditer(pattern, sentence)
    for match in matches:
        subject = match.group(1)
        verb = "是"
        obj = match.group(3)
        triples.add((subject, verb, obj))
    return triples

def rule_adj_noun_relation(sentence):
    """规则3：提取形容词修饰名词的属性关系"""
    triples = set()
    pattern = r'(\S+)/a 的/u (\S+)/({})'.format('|'.join(NOUN_TAGS))
    matches = re.finditer(pattern, sentence)
    for match in matches:
        adj = match.group(1)
        noun = match.group(2)
        triples.add((adj, '修饰', noun))
    return triples

def rule_time_loc_relation(sentence):
    """规则4：提取时间或地点的修饰关系"""
    triples = set()
    pattern = r'(\S+)/({}|{}) (\S+)/v (\S+)/({})'.format(TIME_TAG, LOC_TAG, '|'.join(NOUN_TAGS))
    matches = re.finditer(pattern, sentence)
    for match in matches:
        modifier = match.group(1)
        verb = match.group(3)
        obj = match.group(4)
        triples.add((modifier, verb, obj))
    return triples

def rule_verb_loc_relation(sentence):
    """规则5：提取动词+地点的关系"""
    triples = set()
    pattern = r'(\S+)/({}) (\S+)/v (\S+)/({})'.format('|'.join(NOUN_TAGS), LOC_TAG)
    matches = re.finditer(pattern, sentence)
    for match in matches:
        subject = match.group(1)
        verb = match.group(3)
        loc = match.group(4)
        triples.add((subject, verb, loc))
    return triples

def rule_verb_time_relation(sentence):
    """规则6：提取动词+时间的关系"""
    triples = set()
    pattern = r'(\S+)/({}) (\S+)/v (\S+)/({})'.format('|'.join(NOUN_TAGS), TIME_TAG)
    matches = re.finditer(pattern, sentence)
    for match in matches:
        subject = match.group(1)
        verb = match.group(3)
        time = match.group(4)
        triples.add((subject, verb, time))
    return triples

def rule_has_relation(sentence):
    """规则7：提取“具有”关系"""
    triples = set()
    pattern = r'(\S+)/({}) 具有/v .*? (\S+)/({})'.format('|'.join(NOUN_TAGS), '|'.join(NOUN_TAGS))
    matches = re.finditer(pattern, sentence)
    for match in matches:
        subject = match.group(1)
        verb = "具有"
        obj = match.group(3)
        triples.add((subject, verb, obj))
    return triples

def rule_include_relation(sentence):
    """规则8：提取“包括”关系。"""
    triples = set()
    pattern = r'(\S+)/({}) (包括|包含|含有)/v .*? (\S+)/({})'.format('|'.join(NOUN_TAGS), '|'.join(NOUN_TAGS))
    matches = re.finditer(pattern, sentence)
    for match in matches:
        subject = match.group(1)
        verb = "包括"
        obj = match.group(4)
        triples.add((subject, verb, obj))
    return triples

def rule_own_relation(sentence):
    """规则9：提取“拥有”关系。"""
    triples = set()
    pattern = r'(\S+)/({}) (拥有|坐拥|持有|获得)/v .*? (\S+)/({})'.format('|'.join(NOUN_TAGS), '|'.join(NOUN_TAGS))
    matches = re.finditer(pattern, sentence)
    for match in matches:
        subject = match.group(1)
        verb = "拥有"
        obj = match.group(4)
        triples.add((subject, verb, obj))
    return triples

def rule_need_relation(sentence):
    """规则10：提取“需要”关系。"""
    triples = set()
    pattern = r'(\S+)/({}) (需要|急需)/v .*? (\S+)/({})'.format('|'.join(NOUN_TAGS), '|'.join(NOUN_TAGS))
    matches = re.finditer(pattern, sentence)
    for match in matches:
        subject = match.group(1)
        verb = "需要"
        obj = match.group(4)
        triples.add((subject, verb, obj))
    return triples

def rule_cause_relation(sentence):
    """规则11：提取“导致”关系，包括：
    1. 因果关系中的 “n + 导致 + n + (可选副词) + v” 的结构；
    2. 因果关系中的 “n + 导致 + n + (可选副词) + v + n” 的结构；
    3. 因果关系中的 “n + 导致 + 名词 + 形容词” 的结构。
    """
    triples = set()

    # 匹配模式1：n + 导致 + n + (可选副词) + v
    pattern1 = r'(\S+)/({}) (使得|导致|造成|令|让)/v (\S+)/({}) (?:((\S+)/d )?(\S+)/v)'.format(
        '|'.join(['n', 'nz', 'nl', 'ns']),  # 前因是名词类
        '|'.join(['n', 'nz', 'nl', 'ns'])   # 动宾结构的主语
    )
    matches1 = re.finditer(pattern1, sentence)
    for match in matches1:
        
        cause = match.group(1)  # 提取前因
        subject = match.group(4)  # 动宾结构的主语
        verb_modifier = match.group(7) if match.group(7) else ""  # 提取副词（若存在）
        verb = match.group(8)  # 动词
        if verb_modifier:
            verb_modifier = verb_modifier.strip()  # 去掉尾部空格
        effect = f"{subject}{verb_modifier}{verb}"  # 拼接主语 + 副词 + 动词
        triples.add((cause, "导致", effect))

    # 匹配模式2：n + 导致 + n + (可选副词) + v + n
    pattern2 = r'(\S+)/({}) (使得|导致|造成|令|让)/v (\S+)/({}) (?:((\S+)/d )?(\S+)/v (\S+)/({}))'.format(
        '|'.join(['n', 'nz', 'nl', 'ns']),  # 前因是名词类
        '|'.join(['n', 'nz', 'nl', 'ns']),  # 动宾结构的主语
        '|'.join(['n', 'nz', 'nl', 'ns', 'i'])   # 可选的宾语
    )
    matches2 = re.finditer(pattern2, sentence)
    for match in matches2:
        cause = match.group(1)  # 提取前因
        subject = match.group(4)  # 动宾结构的主语
        verb_modifier = match.group(7) if match.group(7) else ""  # 提取副词（若存在）
        verb = match.group(8)  # 动词
        obj = match.group(9)  # 宾语
        if verb_modifier:
            verb_modifier = verb_modifier.strip()  # 去掉尾部空格
        effect = f"{subject}{verb_modifier}{verb}{obj}"  # 拼接主语 + 副词 + 动词 + 宾语
        triples.add((cause, "导致", effect))

    # 匹配模式3：n + 导致 + 名词 + 形容词
    pattern3 = r'(\S+)/({}) (使得|导致|造成|令|让)/v (\S+)/({}) (\S+)/a'.format(
        '|'.join(['n', 'nz', 'nl', 'ns']),  # 前因是名词类
        '|'.join(['n', 'nz', 'nl', 'ns'])   # 形容词前面的名词
    )
    matches3 = re.finditer(pattern3, sentence)
    for match in matches3:
        cause = match.group(1)  # 提取前因
        subject = match.group(4)  # 提取“名词”
        adj = match.group(6)  # 提取“形容词”
        effect = f"{subject}{adj}"  # 拼接名词 + 形容词
        triples.add((cause, "导致", effect))
    return triples

def rule_modify_relation(sentence):
    """规则12：提取“修饰”关系"""
    triples = set()
    pattern = r'(\S+)/({}) (\S+)/a'.format('|'.join(['n', 'nz', 'nl', 'ns']))
    matches = re.finditer(pattern, sentence)
    for match in matches:
        adj = match.group(3)
        noun = match.group(1)
        triples.add((adj, "修饰", noun))
    return triples

def rule_person_location_label(sentence):
    """
    规则13：提取 A/nh 为 'A 是 人物'，提取 A/ns 或 A/nl 为 'A 是 地点'
    """
    triples = set()
    # 提取人物
    person_pattern = r'(\S+)/nh'
    person_matches = re.finditer(person_pattern, sentence)
    for match in person_matches:
        entity = match.group(1)
        triples.add((entity, "是", "人物"))

    # 提取地点
    location_pattern = r'(\S+)/({}|{})'.format(LOC_TAG, 'nl')
    location_matches = re.finditer(location_pattern, sentence)
    for match in location_matches:
        entity = match.group(1)
        triples.add((entity, "是", "地点"))

    return triples

def rule_food_relation(sentence):
    """规则14：提取 动词'吃'/'喝' 或形容词'美味的' 后面名词'A'，标记为 A 是 食物"""
    triples = set()
    # 支持“吃/v”、“喝/v”、“美味/n 的/u” 后接 名词/n
    pattern1 = r'吃/v.*?(\S+)/({})'.format('|'.join(NOUN_TAGS))
    matches = re.finditer(pattern1, sentence)
    for match in matches:
        food = match.group(1)
        triples.add((food, "是", "食物"))
    pattern2 = r'喝/v.*?(\S+)/({})'.format('|'.join(NOUN_TAGS))
    matches = re.finditer(pattern2, sentence)
    for match in matches:
        food = match.group(1)
        triples.add((food, "是", "食物"))
    pattern3 = r'(美味|好吃|美味可口|可口)/n 的/u (\S+)/({})'.format('|'.join(NOUN_TAGS))
    matches = re.finditer(pattern3, sentence)
    for match in matches:
        food = match.group(1)
        triples.add((food, "是", "食物"))
    return triples


def rule_like_relation(sentence):
    """规则15：提取 名词/人物 + 喜欢 + 动词短语 或 动宾结构"""
    triples = set()
    # 匹配“喜欢 + 动词短语”，确保动词后面不是名词
    pattern_phrase = r'(\S+)/(n|nh) 喜欢/v (\S+)/v(?! \S+/n)'
    # 匹配“喜欢 + 动宾结构”
    pattern_verb_object = r'(\S+)/(n|nh) 喜欢/v (\S+)/v (\S+)/({})'.format('|'.join(NOUN_TAGS))

    # 匹配“喜欢 + 动词短语”
    matches_phrase = re.finditer(pattern_phrase, sentence)
    for match in matches_phrase:
        subject = match.group(1)  # 主体：名词或人物
        verb = "喜欢"
        action = match.group(3)  # 动词短语
        triples.add((subject, verb, action))

    # 匹配“喜欢 + 动宾结构”
    matches_verb_object = re.finditer(pattern_verb_object, sentence)
    for match in matches_verb_object:
        subject = match.group(1)  # 主体：名词或人物
        verb = "喜欢"
        object_verb = match.group(3)  # 动宾中的动词
        object_noun = match.group(4)  # 动宾中的名词
        triples.add((subject, verb, f"{object_verb}{object_noun}"))

    return triples

def rule_is_possessive_relation(sentence):
    """规则16：提取 A 是 B 的 C 结构"""
    triples = set()
    pattern = r'(\S+)/({}) 是/v (\S+)/({}) 的/u (\S+)/({})'.format(
        '|'.join(NOUN_TAGS),  # A 和 B 都是名词
        '|'.join(NOUN_TAGS),  # B 和 C 都是名词
        '|'.join(NOUN_TAGS)   # C 是名词
    )
    matches = re.finditer(pattern, sentence)
    for match in matches:
        possessor = match.group(3)  # B：拥有者
        entity = match.group(5)    # C：拥有的对象
        subject = match.group(1)   # A：描述的主体
        triples.add((subject, "是", f'{possessor}的{entity}'))
    return triples

def rule_because_relation(sentence):
    """规则17：提取“因为”关系，包括：
    1. 因果关系中的 “n + 是因为 + n + (可选副词) + v” 的结构；
    2. 因果关系中的 “n + 是因为 + n + (可选副词) + v + n” 的结构；
    3. 因果关系中的 “n + 是因为 + n + 形容词” 的结构。
    """
    triples = set()

    # 匹配模式1：n + 是因为 + n + (可选副词) + v
    pattern1 = r'(\S+)/({}) (是因为|归因于|得益于|归功于|归咎于|是由于|由于|因)/v (\S+)/({}) (?:((\S+)/d )?(\S+)/v)'.format(
        '|'.join(['n', 'nz', 'nl', 'ns']),  # 后果是名词类
        '|'.join(['n', 'nz', 'nl', 'ns'])   # 因果中的主语
    )
    matches1 = re.finditer(pattern1, sentence)
    for match in matches1:
        effect = match.group(1)  # 提取后果
        cause_subject = match.group(4)  # 因果中的主语
        verb_modifier = match.group(7) if match.group(7) else ""  # 提取副词（若存在）
        verb = match.group(8)  # 动词
        if verb_modifier:
            verb_modifier = verb_modifier.split('/')[0]  # 去掉标注符号
        cause = f"{cause_subject}{verb_modifier}{verb}"  # 拼接主语 + 副词 + 动词
        triples.add((effect, "由于", cause))

    # 匹配模式2：n + 是因为 + n + (可选副词) + v + n
    pattern2 = r'(\S+)/({}) (是因为|归因于|得益于|归功于|归咎于|是由于|由于|因)/v (\S+)/({}) (?:((\S+)/d )?(\S+)/v (\S+)/({}))'.format(
        '|'.join(['n', 'nz', 'nl', 'ns']),  # 后果是名词类
        '|'.join(['n', 'nz', 'nl', 'ns']),  # 因果中的主语
        '|'.join(['n', 'nz', 'nl', 'ns', 'i'])   # 可选的宾语
    )
    matches2 = re.finditer(pattern2, sentence)
    for match in matches2:
        all_groups = match.groups()
        for i in range(len(all_groups)):
            print(f"match.group({i}): {match.group(i)}")
        effect = match.group(1)  # 提取后果
        cause_subject = match.group(4)  # 因果中的主语
        verb_modifier = match.group(7) if match.group(7) else ""  # 提取副词（若存在）
        verb = match.group(8)  # 动词
        obj = match.group(9)  # 宾语
        if verb_modifier:
            verb_modifier = verb_modifier.split('/')[0]  # 去掉标注符号
        cause = f"{cause_subject}{verb_modifier}{verb}{obj}"  # 拼接主语 + 副词 + 动词 + 宾语
        triples.add((effect, "由于", cause))

    # 匹配模式3：n + 是因为 + n + 形容词
    pattern3 = r'(\S+)/({}) (是因为|归因于|得益于|归功于|归咎于|是由于|由于|因)/v (\S+)/({}) (\S+)/a'.format(
        '|'.join(['n', 'nz', 'nl', 'ns']),  # 后果是名词类
        '|'.join(['n', 'nz', 'nl', 'ns'])   # 因果中的名词
    )
    matches3 = re.finditer(pattern3, sentence)
    for match in matches3:
        effect = match.group(1)  # 提取后果
        cause_subject = match.group(4)  # 提取因果中的主语
        adj = match.group(6)  # 提取形容词
        cause = f"{cause_subject}{adj}"  # 拼接主语 + 形容词
        triples.add((effect, "由于", cause))

    return triples

def rule_institution_extraction(sentence):
    """规则18：提取所有的 A/ni 为 A 是机构"""
    triples = set()
    # 匹配 A/ni（机构）
    pattern_ni = r'(\S+)/ni'
    matches_ni = re.finditer(pattern_ni, sentence)
    for match in matches_ni:
        entity = match.group(1)  # 提取机构名称
        triples.add((entity, "是", "机构"))
    return triples
def rule_idiom_extraction(sentence):
    """规则19：提取所有的 A/i 为 A 是成语"""
    triples = set()
    # 匹配 A/i（成语）
    pattern_i = r'(\S+)/i'
    matches_i = re.finditer(pattern_i, sentence)
    for match in matches_i:
        entity = match.group(1)  # 提取成语
        if len(entity) > 3:
            triples.add((entity, "是", "成语或俗语"))
    return triples

def rule_similarity_relation(sentence):
    """规则20：提取相似关系，包括：
    1. A 就像 B
    2. A 好像 B
    3. A 如 B
    4. A 和 B 很像
    5. 其他类似表达
    提取为 (A, 相似于, B)
    """
    triples = set()
    # 定义匹配模式，匹配常见的相似表达
    pattern = r'(\S+)/({}) (就像|好像|如|和|如同)/p (\S+)/({}) (?:很像|一样|相似)?'.format(
        '|'.join(['n', 'nz', 'nl', 'ns', 'i']),  # A 是名词类或成语
        '|'.join(['n', 'nz', 'nl', 'ns', 'i'])   # B 是名词类或成语
    )
    matches = re.finditer(pattern, sentence)
    for match in matches:
        entity_a = match.group(1)  # 提取 A
        entity_b = match.group(4)  # 提取 B
        triples.add((entity_a, "相似于", entity_b))
    return triples


def apply_rules(words):
    """应用所有规则"""
    sentence = to_sentence(words)
    # print('sentence:', sentence)
    results = set()
    results.update(rule_verb_object_relation(sentence))  # 规则1
    results.update(rule_is_relation(sentence))  # 规则2
    results.update(rule_adj_noun_relation(sentence))  # 规则3
    results.update(rule_time_loc_relation(sentence))  # 规则4
    results.update(rule_verb_loc_relation(sentence))  # 规则5
    results.update(rule_verb_time_relation(sentence))  # 规则6
    results.update(rule_has_relation(sentence))  # 规则7
    results.update(rule_include_relation(sentence))  # 规则8
    results.update(rule_own_relation(sentence))  # 规则9
    results.update(rule_need_relation(sentence))  # 规则10
    results.update(rule_cause_relation(sentence))  # 规则11
    results.update(rule_modify_relation(sentence))  # 规则12
    results.update(rule_person_location_label(sentence))  # 规则13
    results.update(rule_food_relation(sentence))  # 规则14
    results.update(rule_like_relation(sentence))  # 规则15
    results.update(rule_is_possessive_relation(sentence))  # 规则16
    results.update(rule_because_relation(sentence))  # 规则17
    results.update(rule_institution_extraction(sentence))  # 规则18
    results.update(rule_idiom_extraction(sentence))  # 规则19
    results.update(rule_similarity_relation(sentence))  # 规则20
    return results
