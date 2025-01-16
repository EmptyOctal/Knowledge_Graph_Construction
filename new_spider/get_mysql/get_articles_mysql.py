import mysql.connector
import time
from retrying import retry
from DrissionPage import Chromium
from DrissionPage import ChromiumOptions

# 配置浏览器选项
options = ChromiumOptions()
options.no_imgs(True).mute(True)
options.incognito()
options.headless(False)
browser = Chromium(addr_or_opts=options)
tab1 = browser.latest_tab

# 初始化数据库
def init_db():
    conn = mysql.connector.connect(
        host='localhost',        # 数据库地址
        user='root',             # 数据库用户名
        password='root',         # 数据库密码
        database='spider'        # 数据库名称
    )
    cursor = conn.cursor()
    return conn, cursor

# 保存数据到数据库
def update_content_in_db(cursor, conn, url, content, status, error_msg=None):
    cursor.execute('''
    UPDATE rec
    SET content = %s, status = %s, error_msg = %s
    WHERE url = %s
    ''', (content, status, error_msg, url))
    conn.commit()

# 从数据库获取待爬取的链接
def get_pending_urls(cursor):
    cursor.execute("SELECT id, title, url FROM rec WHERE status = 'pending'")
    return cursor.fetchall()


# 自动重试装饰器
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

# 爬取正文内容
@retry
def scrape_content_from_db(conn, cursor):
    pending_urls = get_pending_urls(cursor)
    for record in pending_urls:
        id, title, url = record
        print(f"开始爬取: {title}, URL: {url}")
        try:
            # 打开文章链接
            tab1.get(url)
            # 模拟网络错误
            # raise Exception("网络请求失败")

            time.sleep(5)  # 等待页面加载
            
            # 提取正文内容
            article = tab1.ele('.article-content')
            # 故意使用一个不存在的选择器
            # article = tab1.ele('.nonexistent-content')

            if not article:
                raise Exception("未找到正文内容")
            
            # 提取所有 <p> 标签
            all_paragraphs = article.eles('t:p')
            # 过滤掉空白段落
            valid_paragraphs = [p for p in all_paragraphs if p.text.strip()]
            content = ''.join(p.text for p in valid_paragraphs if p.text)

            if not content.strip():
                raise Exception("正文内容为空或未提取成功")

            # 更新数据库中的正文内容和状态
            update_content_in_db(cursor, conn, url, content, 'done')
            print(f"成功爬取: {title}")

        except Exception as e:
            # 如果发生错误，更新数据库中的状态和错误信息
            update_content_in_db(cursor, conn, url, '', 'failed', str(e))
            print(f"经3次重试后仍爬取失败: {title}, 错误: {e}")

# 主函数
def main():
    conn, cursor = None, None
    try:
        # 初始化数据库
        conn, cursor = init_db()

        # 爬取正文并更新数据库
        scrape_content_from_db(conn, cursor)
    
    except KeyboardInterrupt:
        print("检测到手动中断，正在释放资源...")
    except Exception as e:
        print(f"程序发生错误: {e}")
    
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