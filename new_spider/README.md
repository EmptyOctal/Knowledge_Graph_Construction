# News Spider

## 项目简介

本项目是一个针对今日头条推荐新闻的网页爬虫，用于爬取新闻网站的URL并提取对应的内容。爬虫支持将数据保存为CSV文件或MySQL数据库格式。爬虫具有自动重试、异常处理和从爬取的URL中提取文章内容的功能。

## 项目结构

```bash
news_spider/
├── get_csv/                  # 存放将数据保存为 CSV 文件的爬虫代码
│   ├── get_urls.py         # 爬取新闻 URL 并保存为 CSV
│   └── get_articles.py      # 根据 CSV 中的 URL 爬取新闻正文
├── get_mysql/                # 存放将数据保存到 MySQL 数据库的爬虫代码
│   ├── get_url_mysql.py         # 爬取新闻 URL 并保存到数据库
│   ├── get_articles_mysql.py      # 根据数据库中的 URL 爬取新闻正文
│   └── NewsSpider.py   # 边爬取 URL 边爬取正文内容
├── README.md                 # 项目说明文档
└── requirements.txt          # 项目依赖
```

## 功能说明

### 1. CSV 模式

- **`get_urls.py`**：
  - 从目标网站爬取新闻 URL，并将结果保存到 CSV 文件中。
  - 支持手动停止爬取。
- **`get_articles.py`**：
  - 读取 CSV 文件中的 URL，爬取新闻正文内容并保存到新的 CSV 文件中。

### 2. MySQL 模式

- **`get_url_mysql.py`**：
  - 从目标网站爬取新闻 URL，并将结果保存到 MySQL 数据库中。
  - 支持手动停止爬取。
- **`get_articles_mysql.py`**：
  - 从 MySQL 数据库中读取未爬取的 URL，爬取新闻正文内容并更新数据库记录。
- **`NewsSpider.py`**：
  - 边爬取 URL 边打开新标签页爬取对应的文章内容。

### 环境要求

- Python 3.x
- `DrissionPage`（用于网页爬取）
- `mysql-connector-python`（用于MySQL集成）
- `retrying`（用于自动重试）

### 安装与配置

1. **克隆仓库：**
   
   ```bash
   git clone https://github.com/yourusername/news_spider.git
   cd news_spider

2. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

3. **设置MySQL数据库**

   - 修改爬虫文件中的MySQL数据库的登录信息
     ```python
     conn = mysql.connector.connect(
         host='localhost',
         user='root', # 修改为你的数据库用户名
         password='root', # 修改为你的数据库登陆密码
         database='spider'
     )
     ```

   - 通过运行`get_mysql/`目录中的脚本，确保创建了所需的表。

## 使用方法

### 先爬URL后爬正文

1. **爬取URL和文章标题**
   进入对应脚本文件路径，通过运行爬取URL的脚本，将今日头条的推荐文章的网址存储进csv / 数据库中

   ```bash
   python get_urls.py
   python get_url_mysql.py
   ```

2. **手动停止爬取**

3. **启动新的进程提取之前爬取的URL内容**
   进入对应脚本文件路径，通过运行爬取正文的脚本，将今日头条的推荐文章的正文内容存储进csv / 数据库中

   ```bash
   python get_articles.py
   python get_articles_mysql.py
   ```

该方法的优势在于其实现了任务分离，能提高爬虫的效率和稳定性。统一爬取URL时，爬虫只需要专注于获取文章的URL，这一过程相对较简单，页面加载速度较快，可以大规模、稳定地爬取大量的URL。如果在爬取URL时直接提取正文内容，容易导致页面加载缓慢，增加爬虫的停顿时间，降低整体效率。

### 爬URL的同时爬取文章正文

进入对应目录，运行对应脚本。
```bash
python NewsSpider.py
```

该方法优势在于使用简单，不需要中途手动停止爬取，实时性较高。

## 技术细节

(待补充)

## 贡献者

- EmptyCity

## 反馈与建议

如有任何问题或建议，请提交 Issue 或联系项目维护者。