from .preprocessor import clean_text, split_sentences
from .segmenter import segment_and_tag
from .rules.base_rules import apply_rules

def extract_knowledge(text):
    """
    知识抽取主逻辑
    :param text: 输入的长文本
    :return: 知识三元组列表 [(主语, 谓语, 宾语)]
    """
    all_knowledge = set()
    sentences = split_sentences(text)
    for sentence in sentences:
        # 1. 文本清理
        cleaned_text = clean_text(sentence)
        # 2. 分词与词性标注
        words = segment_and_tag(cleaned_text)
        # 3. 应用规则提取三元组
        knowledge = apply_rules(words)
        all_knowledge.update(knowledge)
    return all_knowledge
