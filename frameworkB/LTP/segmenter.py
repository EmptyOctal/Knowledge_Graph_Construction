from .model import get_model

def segment_and_tag(text):
    """对文本进行分词和词性标注"""
    ltp = get_model()
    result = ltp.pipeline([text], tasks = ["cws", "pos"])
    words = result.cws[0]
    tags = result.pos[0]
    # 例如: [("我", "r"), ("喜欢", "v"), ("吃", "v"), ("KFC", "n")]
    return list(zip(words, tags))