import re

def clean_text(text):
    """清理文本，去除空格等"""
    text = text.replace(' ', '') # 去除空格
    # text = re.sub(r'[^\w\s]', '', text)  # 去除标点符号
    return text.strip()

def split_sentences(text):
    """
    将文本按句末标点分割为句子列表
    :param text: 输入文本
    :return: 分句后的列表
    """
    # 按中文常见句末标点分割句子
    sentences = re.split(r'([。！？；：……])', text)    
    # 将句末标点与前文结合，清除空字符串和多余的空格
    sentences = [sentence.strip() + end.strip() for sentence, end in zip(sentences[::2], sentences[1::2])]
    # 返回非空句子
    return [sentence for sentence in sentences if sentence.strip()]
