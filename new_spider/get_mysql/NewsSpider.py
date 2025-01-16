from DrissionPage import Chromium, ChromiumOptions
import mysql.connector
import time

# 自动重试装饰器
def retry(max_retries=3, wait_time=5):
    """
    自动重试装饰器。
    :param max_retries: 最大重试次数
    :param wait_time: 每次重试的等待时间（秒）
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    print(f"重试第 {retries} 次: {e}")
                    time.sleep(wait_time)
            print(f"多次重试失败，跳过 {func.__name__} 操作。")
            return None
        return wrapper
    return decorator

# 初始化数据库
@retry(max_retries=3, wait_time=5)
def init_db():
    conn = mysql.connector.connect(
        host='localhost',        # 数据库地址
        user='root',             # 数据库用户名
        password='root',         # 数据库密码
        database='spider'        # 数据库名称
    )
    cursor = conn.cursor()
    # 创建表，如果表不存在
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS articles (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title TEXT,
        url VARCHAR(500) UNIQUE,         -- 确保 URL 唯一
        content LONGTEXT,
        status TEXT,   -- 状态
        error_msg TEXT,                  -- 错误信息
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    return conn, cursor

# 保存数据到数据库
@retry(max_retries=3, wait_time=5)
def save_to_db(cursor, conn, title, url, content, status, error_msg=None):
    try:
        cursor.execute('''
        INSERT INTO articles (title, url, content, status, error_msg)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        content = VALUES(content), status = VALUES(status), error_msg = VALUES(error_msg)
        ''', (title, url, content, status, error_msg))
        conn.commit()
    except Exception as e:
        print(f"保存数据到数据库时发生错误: {e}")

# 主程序
def main():
    conn, cursor = init_db()  # 初始化数据库连接
    try:
        options = ChromiumOptions()
        # 设置不加载图片、静音
        options.no_imgs(True).mute(True)
        options.incognito()
        options.headless(False)
        browser = Chromium(addr_or_opts=options)
        tab1 = browser.latest_tab
        tab2 = browser.new_tab()

        @retry(max_retries=3, wait_time=5)
        def load_page(tab, url):
            tab.get(url)

        @retry(max_retries=3, wait_time=5)
        def get_element(tab, selector):
            return tab.ele(selector)

        @retry(max_retries=3, wait_time=5)
        def get_elements(tab, selector):
            return tab.eles(selector)

        @retry(max_retries=3, wait_time=5)
        def scroll_page(tab, scroll_height):
            tab.actions.scroll(scroll_height)

        @retry(max_retries=3, wait_time=5)
        def execute_js(tab, script):
            return tab.run_js(script)

        load_page(tab1, 'https://www.toutiao.com/')
        main_content = get_element(tab1, '.ttp-feed-module')
        window_height = execute_js(tab1, 'return window.innerHeight')
        new_eles = None
        urls = set()

        while True:
            if new_eles is not None:
                last_ele = new_eles[-1]
                new_eles = last_ele.afters('@class=feed-card-wrapper feed-card-article-wrapper')
            else:
                new_eles = get_elements(main_content, '@class=feed-card-wrapper feed-card-article-wrapper')

            for card in new_eles:
                try:
                    title = get_element(card, '.feed-card-article-l').ele('tag:a').attr('aria-label')
                    url = get_element(card, 't:a').attr('href')
                    if not url.startswith("http"):
                        url = f"https://www.toutiao.com{url}"  # 补全相对链接
                    if url in urls:
                        continue

                    print(f"正在处理文章: {title}")
                    print(f"URL: {url}")

                    load_page(tab2, url)
                    article = get_element(tab2, '.article-content')
                    if not article:
                        raise Exception("未找到正文内容")

                    all_paragraphs = get_elements(article, 't:p')
                    valid_paragraphs = [p for p in all_paragraphs if p.text.strip()]
                    content = ''.join(p.text for p in valid_paragraphs if p.text)

                    if not content.strip():
                        raise Exception("提取到的正文内容为空")

                    # 保存到数据库，状态为 'done'
                    save_to_db(cursor, conn, title, url, content, 'done')
                    print("文章保存成功")

                    urls.add(url)
                except Exception as e:
                    # 保存错误信息到数据库，状态为 'failed'
                    print(f"处理文章时发生错误: {e}")
                    save_to_db(cursor, conn, title, url, '', 'failed', str(e))

            # 滚动页面加载更多内容
            try:
                page_height = execute_js(tab1, 'return document.body.scrollHeight')
                current_height = execute_js(tab1, 'return window.pageYOffset')
                scroll_page(tab1, page_height - current_height - window_height)
                time.sleep(5)
            except Exception as e:
                print(f"页面滚动时发生错误: {e}")
    except KeyboardInterrupt:
        print("检测到手动中断，正在释放资源...")
    except Exception as e:
        print(f"主程序发生错误: {e}")
    finally:
        # 释放资源
        print("释放资源...")
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        if browser:
            browser.quit()
        print("资源已释放，程序结束。")

# 执行主程序
if __name__ == "__main__":
    main()