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
```
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

#### 1. 异常不中断
为了保证爬虫在运行过程中即使遇到错误也不会中断，代码实现了以下机制：
1. **自动重试机制**：
   - 使用 `retry` 装饰器，为关键操作（如加载页面、获取元素、滚动页面等）增加自动重试逻辑。
   - 每个操作最多尝试 `max_retries` 次，失败后会等待 `wait_time` 秒。
   - 如果多次重试失败，打印错误日志并跳过该任务。
   - 装饰器示例：
     ```python
     @retry(max_retries=3, wait_time=5)
     def load_page(tab, url):
         tab.get(url)
     ```
2. **局部异常捕获**：
   - 在处理每篇文章时，通过 `try-except` 捕获异常，保证即使单篇文章处理失败，也不会影响其他文章的爬取。
   - 出现异常时，将相关错误信息保存到数据库，状态记录为 `failed`，方便后续排查问题。
   - 示例：
     ```python
     try:
         load_page(tab2, url)
         # 正文提取逻辑...
     except Exception as e:
         save_to_db(cursor, conn, title, url, '', 'failed', str(e))
     ```
---

#### 2. 自动重试
代码通过 `retry` 装饰器为多个关键操作添加了自动重试功能。关键点包括：
- **重试控制参数**：
  - `max_retries`: 最大重试次数，默认值为 `3`。
  - `wait_time`: 每次重试的等待时间（秒），默认值为 `5`。
- **适用范围**：
  - 页面加载：`load_page`
  - DOM 元素获取：`get_element` 和 `get_elements`
  - 页面滚动：`scroll_page`
  - JavaScript 执行：`execute_js`
  - 数据库初始化和数据保存：`init_db` 和 `save_to_db`
- **逻辑细节**：
  - 如果重试次数耗尽，返回 `None`，并在日志中记录失败操作。
---

#### 3. 接入数据库管理爬取记录
为保证爬取任务的可追溯性，代码中接入了 MySQL 数据库，用于管理爬取记录。细节如下：
1. **数据库初始化**：
   - 表结构设计：
     ```sql
     CREATE TABLE IF NOT EXISTS articles (
         id INT AUTO_INCREMENT PRIMARY KEY,
         title TEXT,
         url VARCHAR(500) UNIQUE,         -- 确保 URL 唯一
         content LONGTEXT,
         status TEXT,                     -- 状态 ('done' 或 'failed')
         error_msg TEXT,                  -- 错误信息
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
     );
     ```
   - 通过 `init_db` 函数初始化数据库连接，并确保表结构存在。
2. **数据存储逻辑**：
   - 使用 `save_to_db` 函数将文章的元信息、正文内容、状态等写入数据库。
   - 支持 `ON DUPLICATE KEY UPDATE`，保证即使重复处理相同 URL，也会更新其内容或错误信息。
   - 示例：
     ```python
     cursor.execute('''
     INSERT INTO articles (title, url, content, status, error_msg)
     VALUES (%s, %s, %s, %s, %s)
     ON DUPLICATE KEY UPDATE
     content = VALUES(content), status = VALUES(status), error_msg = VALUES(error_msg)
     ''', (title, url, content, status, error_msg))
     ```

---

#### 4. 正文提取
针对新闻文章的正文提取实现了以下细节：
1. **目标区域定位**：
   - 使用 CSS 选择器 `.article-content` 定位正文内容区域。
   - 捕获不到目标区域时抛出异常，记录为 `failed` 状态。
2. **段落过滤**：
   - 使用 `t:p` 选择所有段落标签，并过滤掉内容为空的段落。
   - 将有效段落拼接成完整的正文内容：
     ```python
     all_paragraphs = get_elements(article, 't:p')
     valid_paragraphs = [p for p in all_paragraphs if p.text.strip()]
     content = ''.join(p.text for p in valid_paragraphs if p.text)
     if not content.strip():
         raise Exception("提取到的正文内容为空")
     ```
3. **URL 补全**：
   - 如果文章 URL 为相对路径（不以 `http` 开头），自动补全为完整路径。

---

#### 5. 页面滚动加载
本项目爬取的今日头条网页可通过首页滚动，像潜入无底洞一样不断获取头条的文章，代码实现了页面滚动逻辑：
- **滚动计算**：
  - 使用 JavaScript 获取页面高度 `document.body.scrollHeight` 和当前滚动位置 `window.pageYOffset`。
  - 根据差值滚动页面，加载更多内容：
    ```python
    page_height = execute_js(tab1, 'return document.body.scrollHeight')
    current_height = execute_js(tab1, 'return window.pageYOffset')
    scroll_page(tab1, page_height - current_height - window_height)
    ```
- **滚动间隔**：
  - 每次滚动后等待 `5` 秒，以便页面内容加载完成。

---

#### 6. 程序稳定性保障
1. **手动中断处理**：
   - 捕获 `KeyboardInterrupt`，优雅释放资源。
2. **资源管理**：
   - 在 `finally` 块中关闭数据库连接和浏览器，确保资源不泄露。

## 贡献者

- EmptyCity

## 反馈与建议

如有任何问题或建议，请提交 Issue 或联系项目维护者。