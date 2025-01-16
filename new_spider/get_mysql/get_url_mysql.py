from DrissionPage import Chromium
from DrissionPage import ChromiumOptions
import mysql.connector
import time

# 初始化数据库
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
    CREATE TABLE IF NOT EXISTS rec (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title TEXT,
        url VARCHAR(500) UNIQUE,         -- 确保 URL 唯一
        content TEXT,
        status TEXT,
        error_msg TEXT
    )
    ''')
    conn.commit()
    return conn, cursor

# 保存数据到数据库
def save_to_db(cursor, conn, title, url, content, status, error_msg=None):
    cursor.execute('''
    INSERT INTO rec (title, url, content, status, error_msg)
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    content = VALUES(content), status = VALUES(status), error_msg = VALUES(error_msg)
    ''', (title, url, content, status, error_msg))
    conn.commit()

def retry(func, max_retries=3, wait_time=5):
    """自动重试装饰器"""
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

@retry
def get_elements(tab, selector):
    """获取元素，支持重试"""
    return tab.eles(selector)

@retry
def get_element(tab, selector):
    """获取元素，支持重试"""
    return tab.ele(selector)

@retry
def scroll_page(tab, scroll_height):
    """滚动页面，支持重试"""
    tab.actions.scroll(scroll_height)

@retry
def execute_js(tab, script):
    """执行 JavaScript，支持重试"""
    return tab.run_js(script)

# 主程序
def main():
    conn, cursor = None, None
    browser = None
    try:
        # 初始化数据库
        conn, cursor = init_db()

        options = ChromiumOptions()
        # 设置不加载图片、静音
        options.no_imgs(True).mute(True)
        options.incognito()
        options.headless(False)
        browser = Chromium(addr_or_opts=options)
        tab1 = browser.latest_tab

        # 打开目标网站
        tab1.get('https://www.toutiao.com/')

        # 获取主要内容模块和窗口高度
        main_content = get_element(tab1, '.ttp-feed-module')
        window_height = execute_js(tab1, 'return window.innerHeight')

        new_eles = None
        urls = set()

        # 主循环
        while True:
            try:
                # 获取新的文章元素
                if new_eles is not None:
                    last_ele = new_eles[-1]
                    new_eles = last_ele.afters('@class=feed-card-wrapper feed-card-article-wrapper')
                else:
                    new_eles = get_elements(main_content, '@class=feed-card-wrapper feed-card-article-wrapper')

                # 遍历新的文章元素
                for card in new_eles:
                    try:
                        title = get_element(get_element(card, '.feed-card-article-l'), 't:a').attr('aria-label')
                        url = get_element(card, 't:a').attr('href')
                        if url in urls:
                            continue

                        # 打印标题和链接
                        print(title)
                        print(url)

                        # 保存到数据库
                        save_to_db(cursor, conn, title, url, '', 'pending')
                        urls.add(url)
                    except Exception as e:
                        print(f"解析文章元素失败: {e}")

                # 滚动页面加载更多内容
                page_height = execute_js(tab1, 'return document.body.scrollHeight')
                current_height = execute_js(tab1, 'return window.pageYOffset')
                scroll_page(tab1, page_height - current_height - window_height)
                time.sleep(5)
            except Exception as e:
                print(f"主循环发生错误: {e}")
                time.sleep(5)  # 等待后重试
    except KeyboardInterrupt:
        print("检测到手动中断，正在释放资源...")
    except Exception as e:
        print(f"程序启动失败或中途异常: {e}")
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