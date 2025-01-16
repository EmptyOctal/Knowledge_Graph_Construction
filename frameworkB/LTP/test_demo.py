from extractor import extract_knowledge
from storage import save_to_file

if __name__ == '__main__':
    # 读取文本
    with open('data.txt', 'r', encoding='utf-8') as file:
        text = file.read()

    # 知识抽取
    knowledge = extract_knowledge(text)
    print("提取的知识：")
    for triple in knowledge:
        print(triple)