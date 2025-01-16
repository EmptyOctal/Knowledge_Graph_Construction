import json
from neo4j import GraphDatabase

def save_to_file(triples, filename='knowledge.json'):
    """保存三元组到文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(triples, f, ensure_ascii=False, indent=4)

class Neo4jSaver:
    def __init__(self, uri, user, password, database):
        """
        初始化 Neo4j 数据库连接。
        :param uri: Neo4j 数据库地址
        :param user: 用户名
        :param password: 密码
        :param database: 数据库名称
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        """
        关闭数据库连接。
        """
        self.driver.close()

    def save_to_neo4j(self, triples):
        """
        保存三元组到指定的 Neo4j 数据库。
        """
        with self.driver.session(database=self.database) as session:
            for head, relation, tail in triples:
                session.execute_write(self._create_relationship, head, relation, tail)

    @staticmethod
    def _create_relationship(tx, head, relation, tail):
        """
        创建三元组的节点和关系。
        """
        query = (
            "MERGE (h:Entity {name: $head}) "
            "MERGE (t:Entity {name: $tail}) "
            "MERGE (h)-[:RELATION {type: $relation}]->(t)"
        )
        tx.run(query, head=head, relation=relation, tail=tail)

def save_to_neo4j(triples, uri="bolt://localhost:7687", user="neo4j", password="passw0rd", database="neo4j"):
    """
    将三元组保存到 Neo4j 数据库，提供简单的调用接口。
    :param triples: 知识三元组
    :param uri: 数据库地址
    :param user: 用户名
    :param password: 密码
    :param database: 数据库名称
    """
    saver = Neo4jSaver(uri, user, password, database)
    try:
        saver.save_to_neo4j(triples)
        print(f"知识保存到 数据库 {database} 成功！")
    finally:
        saver.close()
