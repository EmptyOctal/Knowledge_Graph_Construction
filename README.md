# Knowledge_Graph_Construction
自动化知识图谱构建项目

总体任务：完成自子任务并撰写Markdown文档实现。

1、【数据爬虫】 完成一个高效的爬虫，自动遍历新闻网站的文章和下载，需要具备出现异常不中断、自动重试、接入数据库管理爬取记录、正文提取的功能。

2、【知识抽取】 设计一个高效的框架，以分词-词性标注-匹配的传统“规则”方法实现知识的挖掘，完成基本框架+20条高质量规则最多5分，每10条额外高质量规则1分。

项目组成员：

刘力铮, 郑芮芳, 周志昊

项目组成员贡献：

llz：独立完成【数据爬虫】的功能，成果在 [new_spider/](https://github.com/EmptyOctal/Knowledge_Graph_Construction/tree/main/new_spider) 中。

zrf：独立完成【知识抽取】框架A的搭建，成果在 [frameworkA/](https://github.com/EmptyOctal/Knowledge_Graph_Construction/tree/main/frameworkA) 中。

zzh：独立完成【知识抽取】框架B的搭建，成果在 [frameworkB/](https://github.com/EmptyOctal/Knowledge_Graph_Construction/tree/main/frameworkB) 中。

项目整体流程为：

> 数据爬取今日头条的各类新闻文章 -> 分词+词性标注 -> 基于人为设置的规则进行匹配 -> 得到 (头实体, 关系, 尾实体)的三元组知识 -> 知识存储

可运行demo.py，查看整体流程效果

```python
python demo.py
```

这边录制了一个动图展示实际运行效果：
https://picbed.octalzhihao.top/img/test.gif