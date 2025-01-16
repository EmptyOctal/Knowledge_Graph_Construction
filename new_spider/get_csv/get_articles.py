import csv
import os
import time
from DrissionPage import Chromium
from DrissionPage import ChromiumOptions

# 配置浏览器选项
options = ChromiumOptions()
options.no_imgs(True).mute(True)
options.incognito()
options.headless(False)
browser = Chromium(addr_or_opts=options)
tab1 = browser.latest_tab

def scrape_content(input_csv, output_csv):
    # 检查输出文件是否存在
    file_exists = os.path.exists(output_csv)

    # 打开输入和输出文件
    with open(input_csv, 'r', encoding='utf-8-sig') as infile, open(output_csv, 'r+' if file_exists else 'w+', newline='', encoding='utf-8-sig') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # 如果是空文件，写入表头
        if not file_exists or os.path.getsize(output_csv) == 0:
            writer.writerow(['标题', '链接', '正文'])

        # 读取已写入的行（跳过表头）
        outfile.seek(0)
        existing_rows = list(csv.reader(outfile))
        processed_rows = {row[1]: row for row in existing_rows[1:]} if len(existing_rows) > 1 else {}

        # 跳过输入文件表头
        next(reader, None)
        
        # 遍历输入文件记录
        for row in reader:
            title, url = row
            # 如果该链接已存在并且正文内容有效，跳过
            if url in processed_rows and processed_rows[url][2] and not processed_rows[url][2].startswith("爬取失败"):
                print(f"已处理，跳过: {title}")
                continue

            print(f"开始爬取: {title}")
            try:
                # 打开文章链接
                tab1.get(url)
                time.sleep(5)

                # 提取正文内容
                article = tab1.ele('.article-content')
                if not article:
                    raise Exception("未找到正文内容")

                # 提取所有 <p> 标签
                all_paragraphs = article.eles('t:p')
                valid_paragraphs = [p for p in all_paragraphs if p.text.strip()]
                content = ''.join(p.text for p in valid_paragraphs if p.text)

                if not content.strip():
                    raise Exception("正文内容为空或未提取成功")

                # 写入或更新行
                processed_rows[url] = [title, url, content]
                print(f"成功爬取: {title}")

            except Exception as e:
                # 记录失败内容
                processed_rows[url] = [title, url, f"爬取失败: {e}"]
                print(f"爬取失败: {title}, 错误: {e}")

        # 覆写输出文件
        outfile.seek(0)
        writer.writerow(['标题', '链接', '正文'])
        writer.writerows(processed_rows.values())
        outfile.truncate()  # 清除多余内容

# 主函数调用
scrape_content('toutiao_recommendation_urls.csv', 'toutiao_recommendations.csv')

# 关闭浏览器
browser.quit()
