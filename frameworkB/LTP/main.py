import pandas as pd
import argparse
from extractor import extract_knowledge
from storage import save_to_neo4j, save_to_file

def read_text_from_csv(file_path, text_column):
    """
    从 CSV 文件的指定列逐行读取内容。
    :param file_path: CSV 文件路径
    :param text_column: 包含正文内容的列名
    :return: 正文内容列表
    """
    df = pd.read_csv(file_path, encoding='utf-8') # encoding为文件编码格式
    return df[text_column].dropna().astype(str).tolist()

def read_text_from_dir(dir_path):
    """
    从指定目录下的所有文件读取文本内容。
    :param dir_path: 目录路径
    :return: 正文内容列表
    """
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Knowledge extraction from CSV.')
    parser.add_argument('--csv_file', type=str, default='D:/CodeField/knowledge_extraction/demo_data.csv', help='Path to the CSV file.')
    parser.add_argument('--text_column', type=str, default='正文', help='Name of the column containing text.')
    parser.add_argument('--need_neo4j', type=bool, default=False, help='Whether to save the results to Neo4j database.')
    parser.add_argument('--neo4j_uri', type=str, default='bolt://localhost:7687', help='URI for the Neo4j database.')
    parser.add_argument('--neo4j_user', type=str, default='neo4j', help='Username for the Neo4j database.')
    parser.add_argument('--neo4j_password', type=str, default='passw0rd', help='Password for the Neo4j database.')
    parser.add_argument('--neo4j_database', type=str, default='neo4j', help='Database name for the Neo4j database.')
    parser.add_argument('--output_file', type=str, default='knowledge.json', help='Output file to save the results.')
    args = parser.parse_args()
    
    texts = read_text_from_csv(args.csv_file, args.text_column)
    result = set()
    tot = 0
    for text in texts:
        if text == '爬取失败: 正文内容为空或未提取成功':
            continue
        knowledge = extract_knowledge(text)
        result.update(knowledge)
        for triple in knowledge:
            print(triple)
    
    # 保存结果到 Neo4j 数据库
    if args.need_neo4j:
        save_to_neo4j(list(result), uri=args.neo4j_uri, user=args.neo4j_user, password=args.neo4j_password, database=args.neo4j_database)
    # 保存结果到文件
    save_to_file(list(result), args.output_file)