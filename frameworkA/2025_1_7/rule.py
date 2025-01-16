
class KnowledgeExtractor:
    def __init__(self):
        self.rules = []

    def add_rule(self, name, pattern, extract_func):
        self.rules.append({
            'name': name,
            'pattern': re.compile(pattern, re.DOTALL | re.IGNORECASE | re.UNICODE),
            'extract_func': extract_func
        })

    def extract(self, text):
        results = {}
        words = list(pseg.cut(text))  # 分词和词性标注

        for rule in self.rules:
            matches = list(rule['pattern'].finditer(text))
            if matches:
                result = rule['extract_func'](matches, words)
                if result:
                    results[rule['name']] = result

        return results


extractor = KnowledgeExtractor()
extractor.add_rule(
    "标题",
    r"^(.+?)(?=,https://|$)",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "链接",
    r"(https?://\S+)",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

# 50条新闻知识抽取规则
extractor.add_rule(
    "事件主体",
    r"([\u4e00-\u9fa5]{2,10}(?:部队|组织|机构|公司|团体|政府|委员会|协会|联盟))",
    lambda matches, words: list(
        set([m.group(1) for m in matches if any(w.word in m.group(1) and w.flag.startswith('n') for w in words)]))
)

extractor.add_rule(
    "人物",
    r"([\u4e00-\u9fa5]{2,4}(?:先生|女士|总统|总理|主席|部长|院士|教授|博士|医生|专家|学者|记者|作家|艺术家|运动员|企业家))",
    lambda matches, words: list(
        set([m.group(1) for m in matches if any(w.word in m.group(1) and w.flag == 'nr' for w in words)]))
)

extractor.add_rule(
    "地点",
    r"([\u4e00-\u9fa5]{2,6}(?:国|省|市|县|区|镇|村|街道|广场|公园|山|河|湖|海|岛))",
    lambda matches, words: list(
        set([m.group(1) for m in matches if any(w.word in m.group(1) and w.flag == 'ns' for w in words)]))
)

extractor.add_rule(
    "时间",
    r"(\d{4}年\d{1,2}月\d{1,2}日|\d{4}年\d{1,2}月|\d{4}年|昨天|今天|明天|上周|本周|下周|上个月|这个月|下个月)",
    lambda matches, words: list(
        set([m.group(1) for m in matches if any(w.word in m.group(1) and w.flag == 't' for w in words)]))
)
# 50条新闻知识抽取规则
extractor.add_rule(
    "事件主体",
    r"([\u4e00-\u9fa5]{2,10}(?:部队|组织|机构|公司|团体|政府|委员会|协会|联盟))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "人物",
    r"([\u4e00-\u9fa5]{2,4}(?:先生|女士|总统|总理|主席|部长|院士|教授|博士|医生|专家|学者|记者|作家|艺术家|运动员|企业家))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "地点",
    r"([\u4e00-\u9fa5]{2,6}(?:国|省|市|县|区|镇|村|街道|广场|公园|山|河|湖|海|岛))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "时间",
    r"(\d{4}年\d{1,2}月\d{1,2}日|\d{4}年\d{1,2}月|\d{4}年|昨天|今天|明天|上周|本周|下周|上个月|这个月|下个月)",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "数字",
    r"(\d+(?:\.\d+)?(?:万|亿|千|百|十)?)",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "事件类型",
    r"([\u4e00-\u9fa5]{2,8}(?:事件|事故|案件|灾害|战争|会议|活动|比赛|展览|演出|庆典|节日|游行|示威|抗议))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "原因",
    r"(?:因为|由于|缘于|源于)(.*?)(?:，|。)",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "结果",
    r"(?:导致|结果是|造成|引起|产生)(.*?)(?:，|。)",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "机构",
    r"([\u4e00-\u9fa5]{2,20}(?:公司|机构|部门|委员会|协会|学院|大学|医院|银行|基金会|研究所|实验室))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "职位",
    r"([\u4e00-\u9fa5]{2,10}(?:总统|总理|主席|部长|局长|院长|校长|总经理|经理|主任|负责人|代表|发言人))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "金额",
    r"(\d+(?:\.\d+)?(?:万|亿|千|百|十)?(?:元|美元|欧元|英镑|日元|港币|澳元|加元|新元))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "比例",
    r"(\d+(?:\.\d+)?%)",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "法律法规",
    r"(《[\u4e00-\u9fa5]{2,20}》(?:法|条例|规定|办法|细则))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "产品",
    r"([\u4e00-\u9fa5]{2,10}(?:产品|商品|设备|系统|软件|硬件|应用|平台|服务))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "观点",
    r"(?:认为|表示|指出|强调|声明|宣称|坚持)(.*?)(?:，|。)",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "措施",
    r"(?:采取|实施|推行|执行|落实)(.*?)(?:措施|办法|政策|方案|计划|战略)",
    lambda matches, words: list(set([m.group(0) for m in matches]))
)

extractor.add_rule(
    "影响",
    r"(?:影响|作用|效果|后果|结果)(.*?)(?:，|。)",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "趋势",
    r"([\u4e00-\u9fa5]{2,10}(?:上升|下降|增长|减少|扩大|缩小|趋势|态势|走向|变化))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "行业",
    r"([\u4e00-\u9fa5]{2,10}(?:行业|产业|领域|市场|经济|贸易|商业|农业|工业|服务业))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "技术",
    r"([\u4e00-\u9fa5]{2,10}(?:技术|科技|工艺|方法|算法|系统|工程|设备|材料))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "社会问题",
    r"([\u4e00-\u9fa5]{2,10}(?:问题|矛盾|冲突|危机|挑战|困境|难题|障碍))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "社会现象",
    r"([\u4e00-\u9fa5]{2,10}(?:现象|趋势|潮流|风气|习俗|传统|文化|价值观))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "政策",
    r"([\u4e00-\u9fa5]{2,15}(?:政策|方针|战略|规划|计划|纲要|决议|条例|法规))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "成果",
    r"([\u4e00-\u9fa5]{2,10}(?:成果|成就|进展|突破|创新|发现|发明|贡献))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "评价",
    r"(?:评价|评论|评估|判断|认为)(.*?)(?:，|。)",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "目标",
    r"(?:目标|目的|宗旨|愿景|使命)(.*?)(?:，|。)",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "挑战",
    r"([\u4e00-\u9fa5]{2,10}(?:挑战|困难|问题|障碍|瓶颈|危机|风险))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "解决方案",
    r"(?:解决方案|对策|措施|办法|方法)(.*?)(?:，|。)",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "合作",
    r"([\u4e00-\u9fa5]{2,10}(?:合作|协作|联盟|伙伴关系|战略合作))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "竞争",
    r"([\u4e00-\u9fa5]{2,10}(?:竞争|对抗|较量|争夺|角逐))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "资源",
    r"([\u4e00-\u9fa5]{2,10}(?:资源|资金|人才|技术|设备|原材料|能源))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "环境",
    r"([\u4e00-\u9fa5]{2,10}(?:环境|生态|气候|污染|保护|可持续发展))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "教育",
    r"([\u4e00-\u9fa5]{2,10}(?:教育|培训|学习|教学|课程|学校|大学|学院))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "医疗",
    r"([\u4e00-\u9fa5]{2,10}(?:医疗|卫生|健康|疾病|治疗|预防|药品|疫苗))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "文化",
    r"([\u4e00-\u9fa5]{2,10}(?:文化|艺术|传统|习俗|价值观|文明|遗产))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "体育",
    r"([\u4e00-\u9fa5]{2,10}(?:体育|运动|比赛|锦标赛|奥运会|世界杯|联赛))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "娱乐",
    r"([\u4e00-\u9fa5]{2,10}(?:娱乐|影视|音乐|游戏|演出|明星|综艺))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "科研",
    r"([\u4e00-\u9fa5]{2,15}(?:科研|研究|实验|调查|分析|论文|专利|成果))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "创新",
    r"([\u4e00-\u9fa5]{2,10}(?:创新|创造|发明|突破|改革|革新|升级))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "安全",
    r"([\u4e00-\u9fa5]{2,10}(?:安全|防护|保护|风险|威胁|隐患|事故|灾害))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "经济指标",
    r"([\u4e00-\u9fa5]{2,10}(?:GDP|通货膨胀|失业率|利率|汇率|股指|指数))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "社会福利",
    r"([\u4e00-\u9fa5]{2,10}(?:福利|保障|救助|补贴|津贴|养老金|医保))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "交通",
    r"([\u4e00-\u9fa5]{2,10}(?:交通|运输|物流|航空|铁路|公路|海运))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "能源",
    r"([\u4e00-\u9fa5]{2,10}(?:能源|电力|石油|天然气|煤炭|新能源|可再生能源))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "外交",
    r"([\u4e00-\u9fa5]{2,10}(?:外交|国际关系|双边关系|多边关系|条约|协定|声明))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "军事",
    r"([\u4e00-\u9fa5]{2,10}(?:军事|国防|武器|装备|演习|战略|战术))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)

extractor.add_rule(
    "社会影响",
    r"([\u4e00-\u9fa5]{2,10}(?:影响|效应|后果|反响|争议|讨论|舆论))",
    lambda matches, words: list(set([m.group(1) for m in matches]))
)
