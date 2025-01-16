from DrissionPage import Chromium
from DrissionPage import ChromiumOptions
import time
import csv

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
main_content = tab1.ele('.ttp-feed-module')
window_height = tab1.run_js('return window.innerHeight')

new_eles = None
urls = set()

# 打开CSV文件以写入模式
with open('toutiao_recommendation_urls.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['文章标题', '文章链接'])  # 写入表头

    while True:
        # 获取新的文章元素
        if new_eles is not None and len(new_eles) > 0:
            last_ele = new_eles[-1]
            new_eles = last_ele.afters('@class=feed-card-wrapper feed-card-article-wrapper')
        else:
            new_eles = main_content.eles('@class=feed-card-wrapper feed-card-article-wrapper')

        if not new_eles:  # 如果没有找到新的元素，跳过本轮循环
            print("未找到新的文章元素，尝试滚动页面加载更多内容...")
            # 滚动页面加载更多内容
            page_height = tab1.run_js('return document.body.scrollHeight')
            current_height = tab1.run_js('return window.pageYOffset')
            tab1.actions.scroll(page_height - current_height - window_height)
            time.sleep(5)
            continue
        
        # 遍历新的文章元素
        for card in new_eles:
            title = card.ele('.feed-card-article-l').ele('t:a').attr('aria-label')
            url = card.ele('t:a').attr('href')
            if url in urls:
                continue

            # 打印并保存标题和链接
            print(title)
            print(url)
            writer.writerow([title, url])  # 写入CSV文件
            urls.add(url)

        # 滚动页面加载更多内容
        page_height = tab1.run_js('return document.body.scrollHeight')
        current_height = tab1.run_js('return window.pageYOffset')
        tab1.actions.scroll(page_height - current_height - window_height)
        time.sleep(5)