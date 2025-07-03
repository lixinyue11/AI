import requests
import json
import re
from lxml import etree
import chardet
import jieba.analyse
from .text2vec import *
def search_bing(query):
    cookies = {
        'MUID': '39BF0C1EB94B694630C719FCB85A6826',
        'MUIDB': '39BF0C1EB94B694630C719FCB85A6826',
        'SRCHD': 'AF=ANNTA1',
        'SRCHUID': 'V=2&GUID=0988F2E4C200415BAB8A7A99DAD83BA3&dmnchg=1',
        'MUIDB': '39BF0C1EB94B694630C719FCB85A6826',
        'SRCHUSR': 'DOB=20250506&DS=1',
        'MSPTC': 'cTGpGaDF4kuIi8WZCyx5KWlCUCRYB1Ibx-yOklKwzfM',
        '_uetvid': '439262c03a0011f082143b4864314665',
        'MMCASM': 'ID=3E025F4CFAEC4A78BFE66A7105F888C4',
        '_tarLang': 'default=zh-Hans',
        '_TTSS_IN': 'hist=WyJlbiIsImF1dG8tZGV0ZWN0Il0=&isADRU=0',
        '_TTSS_OUT': 'hist=WyJ6aC1IYW5zIl0=',
        'SNRHOP': 'I=&TS=',
        'USRLOC': 'HS=1&ELOC=LAT=24.587453842163086|LON=118.09504699707031|N=%E9%9B%86%E7%BE%8E%E5%8C%BA%EF%BC%8C%E7%A6%8F%E5%BB%BA%E7%9C%81|ELT=2|&CLOC=LAT=24.58745387548535|LON=118.09504965479837|A=733.4464586120832|TS=250613020127|SRC=W&BID=MjUwNjEzMTAwMTI3XzVkNjIyNWJlYjA4OGNlMmJjZDQwYTk3OTc2NWVjY2RmMzMwNTM1NGZiMDAwZDdiOGZhMDA3M2I1MjkxZmY3OTI=',
        '_Rwho': 'u=d&ts=2025-06-13',
        '_EDGE_S': 'SID=1394CE15425B60E02389D81F431861F9&mkt=zh-CN',
        'ak_bmsc': '263924EFEA9200D2BE0E07CC9B58C28B~000000000000000000000000000000~YAAQxeNH0iDUwV+XAQAADZ8OaByL/rRZI91Dxa8qosEeX6/DwELaGuHzIAMAR0plk68zBjfX/e8ke/02E6gGi9NOuXqwZx1VAMWSS6OjMiUGJ0YKLQHpsCJQ2Xe4ZOn+Cpe9rfQgExw5JoIWBWb3klMHuXUApVY6f+922Wn3IpU160YYYfBDW7h2s/18oOKFHoQ4hNIjNrbYzQ21aC5NJYO/Ne5bw/IU2wHYZgUbyrQIz/hxZ66KVVcOXpWg/v+ECRiUZhRfvqW/veNIZl/VSE0LfEMSM1/jjqM8z3S8HD8AOj1S0AOtrkl9MDTDqUD9gegN/v/o42ZyJDI32WT+WdZFT/GnmejhV502kULtL+BOkTZLk6Oox3BUC7qbNawswpfKmIfukIBx',
        '_SS': 'SID=1394CE15425B60E02389D81F431861F9&PC=CNNDSP&R=200&RB=0&GB=0&RG=200&RP=200&h5comp=0',
        'GC': '1S2JYSRwK9BhqlviKMbeNPs_yTlzYp14xx7Zg-0xeZljohpGYOXYm47NVymK0NCKLHyRztAM0udZikx5-gG9VA',
        '_RwBf': 'r=0&ilt=142&ihpd=0&ispd=1&rc=200&rb=0&rg=200&pc=200&mtu=0&rbb=0&clo=0&v=1&l=2025-06-13T07:00:00.0000000Z&lft=0001-01-01T00:00:00.0000000&aof=0&ard=0001-01-01T00:00:00.0000000&rwdbt=0&rwflt=0&rwaul2=0&g=&o=2&p=&c=&t=0&s=0001-01-01T00:00:00.0000000+00:00&ts=2025-06-13T08:25:32.0961905+00:00&rwred=0&wls=&wlb=&wle=&ccp=&cpt=&lka=0&lkt=0&aad=0&TH=&cid=0&gb=',
        'dsc': 'order=BingPages',
        'SRCHHPGUSR': 'SRCHLANG=zh-Hans&PV=19.0.0&BZA=0&DM=1&BRW=XW&BRH=T&CW=1752&CH=1314&SCW=1737&SCH=4162&DPR=1.5&UTC=480&EXLTT=33&HV=1749803167&HVE=CfDJ8Inh5QCoSQBNls38F2rbEpRArrSP641d7vLDxh0NJA9hb7oQ5HfmYwwR1PsK5MLVg3TTK2awnNrGahtOYWB_HSpPb_rGstQKn5aMzJvQlFxLX_BUO4YwFOoJxm_-Wv28pbmkgTJBSycL1Uoo8QGQe9sUL1Bop7pU0-wtAvRk7nH5-r5NvjB7fHGPihhHztAsrg&WTS=63885399931&PRVCW=2552&PRVCH=1314&AV=14&ADV=14&RB=0&MB=0&PREFCOL=1&IG=3AD75242B38B4BE9BF8510DBCCA00E3C',
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'avail-dictionary': 'KQKOjm-b',
        'cache-control': 'max-age=0',
        'ect': '4g',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-bitness': '"64"',
        'sec-ch-ua-full-version': '"137.0.3296.68"',
        'sec-ch-ua-full-version-list': '"Microsoft Edge";v="137.0.3296.68", "Chromium";v="137.0.7151.69", "Not/A)Brand";v="24.0.0.0"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"19.0.0"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'sec-ms-gec': '136AE4648F6B70F3A9D87714633C6B2845B98F8C5A3438BD335550B666EAFED1',
        'sec-ms-gec-version': '1-137.0.3296.68',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0',
        'x-client-data': 'eyIxIjoiMCIsIjIiOiIwIiwiMyI6IjAiLCI0IjoiMzQwMTcxMjgwODg5NzY0Njc3IiwiNiI6InN0YWJsZSIsIjkiOiJkZXNrdG9wIn0=',
        'x-edge-shopping-flag': '0',
        # 'cookie': 'MUID=39BF0C1EB94B694630C719FCB85A6826; MUIDB=39BF0C1EB94B694630C719FCB85A6826; SRCHD=AF=ANNTA1; SRCHUID=V=2&GUID=0988F2E4C200415BAB8A7A99DAD83BA3&dmnchg=1; MUIDB=39BF0C1EB94B694630C719FCB85A6826; SRCHUSR=DOB=20250506&DS=1; MSPTC=cTGpGaDF4kuIi8WZCyx5KWlCUCRYB1Ibx-yOklKwzfM; _uetvid=439262c03a0011f082143b4864314665; MMCASM=ID=3E025F4CFAEC4A78BFE66A7105F888C4; _tarLang=default=zh-Hans; _TTSS_IN=hist=WyJlbiIsImF1dG8tZGV0ZWN0Il0=&isADRU=0; _TTSS_OUT=hist=WyJ6aC1IYW5zIl0=; SNRHOP=I=&TS=; USRLOC=HS=1&ELOC=LAT=24.587453842163086|LON=118.09504699707031|N=%E9%9B%86%E7%BE%8E%E5%8C%BA%EF%BC%8C%E7%A6%8F%E5%BB%BA%E7%9C%81|ELT=2|&CLOC=LAT=24.58745387548535|LON=118.09504965479837|A=733.4464586120832|TS=250613020127|SRC=W&BID=MjUwNjEzMTAwMTI3XzVkNjIyNWJlYjA4OGNlMmJjZDQwYTk3OTc2NWVjY2RmMzMwNTM1NGZiMDAwZDdiOGZhMDA3M2I1MjkxZmY3OTI=; _Rwho=u=d&ts=2025-06-13; _EDGE_S=SID=1394CE15425B60E02389D81F431861F9&mkt=zh-CN; ak_bmsc=263924EFEA9200D2BE0E07CC9B58C28B~000000000000000000000000000000~YAAQxeNH0iDUwV+XAQAADZ8OaByL/rRZI91Dxa8qosEeX6/DwELaGuHzIAMAR0plk68zBjfX/e8ke/02E6gGi9NOuXqwZx1VAMWSS6OjMiUGJ0YKLQHpsCJQ2Xe4ZOn+Cpe9rfQgExw5JoIWBWb3klMHuXUApVY6f+922Wn3IpU160YYYfBDW7h2s/18oOKFHoQ4hNIjNrbYzQ21aC5NJYO/Ne5bw/IU2wHYZgUbyrQIz/hxZ66KVVcOXpWg/v+ECRiUZhRfvqW/veNIZl/VSE0LfEMSM1/jjqM8z3S8HD8AOj1S0AOtrkl9MDTDqUD9gegN/v/o42ZyJDI32WT+WdZFT/GnmejhV502kULtL+BOkTZLk6Oox3BUC7qbNawswpfKmIfukIBx; _SS=SID=1394CE15425B60E02389D81F431861F9&PC=CNNDSP&R=200&RB=0&GB=0&RG=200&RP=200&h5comp=0; GC=1S2JYSRwK9BhqlviKMbeNPs_yTlzYp14xx7Zg-0xeZljohpGYOXYm47NVymK0NCKLHyRztAM0udZikx5-gG9VA; _RwBf=r=0&ilt=142&ihpd=0&ispd=1&rc=200&rb=0&rg=200&pc=200&mtu=0&rbb=0&clo=0&v=1&l=2025-06-13T07:00:00.0000000Z&lft=0001-01-01T00:00:00.0000000&aof=0&ard=0001-01-01T00:00:00.0000000&rwdbt=0&rwflt=0&rwaul2=0&g=&o=2&p=&c=&t=0&s=0001-01-01T00:00:00.0000000+00:00&ts=2025-06-13T08:25:32.0961905+00:00&rwred=0&wls=&wlb=&wle=&ccp=&cpt=&lka=0&lkt=0&aad=0&TH=&cid=0&gb=; dsc=order=BingPages; SRCHHPGUSR=SRCHLANG=zh-Hans&PV=19.0.0&BZA=0&DM=1&BRW=XW&BRH=T&CW=1752&CH=1314&SCW=1737&SCH=4162&DPR=1.5&UTC=480&EXLTT=33&HV=1749803167&HVE=CfDJ8Inh5QCoSQBNls38F2rbEpRArrSP641d7vLDxh0NJA9hb7oQ5HfmYwwR1PsK5MLVg3TTK2awnNrGahtOYWB_HSpPb_rGstQKn5aMzJvQlFxLX_BUO4YwFOoJxm_-Wv28pbmkgTJBSycL1Uoo8QGQe9sUL1Bop7pU0-wtAvRk7nH5-r5NvjB7fHGPihhHztAsrg&WTS=63885399931&PRVCW=2552&PRVCH=1314&AV=14&ADV=14&RB=0&MB=0&PREFCOL=1&IG=3AD75242B38B4BE9BF8510DBCCA00E3C',
    }

    res = []
    url = 'https://cn.bing.com/search?q=' + query + '&qs=n&form=QBRE'
    print(url)

    r = requests.get(url, headers=headers, cookies=cookies)
    try:
        encoding = chardet.detect(r.content)['encoding']
        r.encoding = encoding
        dom = etree.HTML(r.content.decode(encoding))

    except:
        dom = etree.HTML(r.content)

    url_list = []
    tmp_url = []
    # 只采集列表的第一页
    for sel in dom.xpath('//ol[@id="b_results"]/li/h2'):
        l = ''.join(sel.xpath('a/@href'))
        title = ''.join(sel.xpath('a//text()')).split('-')[0].strip()
        if 'http' in l and l not in tmp_url and 'doc.' not in l:
            url_list.append([l, title])
            tmp_url.append(l)

    for turl, title in url_list:
        try:
            tr = requests.get(turl, headers=headers, timeout=(5, 5))
            tdom = etree.HTML(tr.content.decode('utf-8'))
            text = '\n'.join(tdom.xpath('//p/text()'))
            if len(text) > 15:
                tmp = {}
                tmp['url'] = turl
                tmp['text'] = text
                tmp['title'] = title
                res.append(tmp)
        except Exception as e:
            print(e)
            pass


    return res
class TextRecallRank():
    """
    实现对检索内容的召回与排序
    """

    def __init__(self,cfg):
        self.topk = cfg.topk    #query关键词召回的数量
        self.topd = cfg.topd    #召回文章的数量
        self.topt = cfg.topt    #召回文本片段的数量
        self.maxlen = cfg.maxlen  #召回文本片段的长度
        self.recall_way = cfg.recall_way  #召回方式
    def query_analyze(self,query):
        keywords = jieba.analyse.extract_tags(query, topK=self.topk, withWeight=True)
        total_weight = self.topk / sum([r[1] for r in keywords])
        return keywords,total_weight
    def recall_title_score(self,title,keywords,total_weight):
        score = 0
        for item in keywords:
            kw, weight = item
            if kw in title:
                score += round(weight * total_weight, 4)
        return score
    def text_segmentate(self, text, maxlen, seps='\n', strips=None):
        """将文本按照标点符号划分为若干个短句
        """
        text = text.strip().strip(strips)
        if seps and len(text) > maxlen:
            pieces = text.split(seps[0])
            text, texts = '', []
            for i, p in enumerate(pieces):
                if text and p and len(text) + len(p) > maxlen - 1:
                    texts.extend(self.text_segmentate(text, maxlen, seps[1:], strips))
                    text = ''
                if i + 1 == len(pieces):
                    text = text + p
                else:
                    text = text + p + seps[0]
            if text:
                texts.extend(self.text_segmentate(text, maxlen, seps[1:], strips))
            return texts
        else:
            return [text]
    def recall_text_score(self, text, keywords, total_weight):
        """计算query与text的匹配程度"""
        score = 0
        for item in keywords:
            kw, weight = item
            p11 = re.compile('%s' % kw)
            pr = p11.findall(text)
            # score += round(weight * total_weight, 4) * len(pr)
            score += round(weight * total_weight, 4)
        return score

    def rank_text_by_keywords(self,query,data):
        # query分析
        keywords, total_weight = self.query_analyze(query)
        # 先召回title
        title_score = {}
        for line in data:
            title = line['title']
            title_score[title] = self.recall_title_score(title, keywords, total_weight)
        title_score = sorted(title_score.items(), key=lambda x: x[1], reverse=True)
        recall_title_list = [t[0] for t in title_score[:self.topd]]

        # 召回sentence
        sentence_score = {}
        for line in data:
            title = line['title']
            text = line['text']
            if title in recall_title_list:
                for ct in self.text_segmentate(text,self.maxlen, seps='\n。'):
                    ct = re.sub('\s+', ' ', ct)
                    if len(ct) >= 20:
                        sentence_score[ct] = self.recall_text_score(ct, keywords, total_weight)
        sentence_score = sorted(sentence_score.items(), key=lambda x: x[1], reverse=True)
        recall_sentence_list = [s[0] for s in sentence_score[:self.topt]]
        return '\n'.join(recall_sentence_list)
    def rank_text_by_text2vec(self,query,data):
        """通过text2vec召回"""

        if not data:
            print("Warning: No data provided for ranking")
            return ""

        # 先召回title
        title_list = [query]

        for line in data:
            title = line['title']
            title_list.append(title)
            # 确保至少有两个标题，否则无法进行相似度计算

        if len(title_list) <= 1:
            print("Warning: Not enough titles for similarity calculation")
            return ""
        title_vectors = get_vector(title_list, 8)###向量

        # 检查向量化是否成功
        if title_vectors.numel() == 0 or title_vectors.size(0) <= 1:
            print("Warning: Title vectorization failed or returned insufficient vectors")
            return ""
        title_score = get_sim(title_vectors)###相似度计算，问题和答案
        print(title_score)
        # 检查相似度计算是否成功
        if not title_score:
            print("Warning: Title similarity calculation failed")
            return ""

        title_score = dict(zip(title_score, range(1, len(title_list))))
        title_score = sorted(title_score.items(), key=lambda x: x[0], reverse=True)

        # 确保有足够的标题用于召回
        if not title_score or self.topd <= 0:
            print("Warning: No title scores or invalid topd parameter")
            return ""

        recall_title_list = [title_list[t[1]] for t in title_score[:min(self.topd, len(title_score))]]



        # 召回sentence
        sentence_list = [query]
        for line in data:
            title = line['title']
            text = line['text']
            if title in recall_title_list:
                for ct in self.text_segmentate(text, self.maxlen, seps='\n。'):
                    ct = re.sub('\s+', ' ', ct)
                    if len(ct) >= 20:
                        sentence_list.append(ct)

        # 确保至少有两个句子，否则无法进行相似度计算
        if len(sentence_list) <= 1:
            print("Warning: Not enough sentences for similarity calculation")
            return ""

        sentence_vectors = get_vector(sentence_list, 8)

        # 检查向量化是否成功
        if sentence_vectors.numel() == 0 or sentence_vectors.size(0) <= 1:
            print("Warning: Sentence vectorization failed or returned insufficient vectors")
            return ""

        sentence_score = get_sim(sentence_vectors)

        # 检查相似度计算是否成功
        if not sentence_score:
            print("Warning: Sentence similarity calculation failed")
            return ""

        sentence_score = dict(zip(sentence_score, range(1, len(sentence_list))))
        sentence_score = sorted(sentence_score.items(), key=lambda x: x[0], reverse=True)

        # 确保有足够的句子用于召回
        if not sentence_score or self.topt <= 0:
            print("Warning: No sentence scores or invalid topt parameter")
            return ""

        recall_sentence_list = [sentence_list[s[1]] for s in sentence_score[:min(self.topt, len(sentence_score))]]
        return '\n'.join(recall_sentence_list)

    def query_retrieve(self,query):
        #利用搜索引擎获取相关信息
        # data = search_bing(query)
        # print(data)
        data=[{'url': 'https://www.yixue.com/%e5%b8%83%e6%b4%9b%e8%8a%ac', 'text': '称：\n\n\n英文名称：Ibuprofen\n\n中文别名：\n、\n、\n\n\n英文别名：Algofen、Amersol、Andran、Apsifen、Brufen、Ebufac、Emodin、Inflam、Motrin、Rurana\u3000\u3000\n\n\n\n本品的\n、\n作用机制尚未完全阐明，可能作用于\n组织局部，通过抑制\n或其他\n的合成而起作用，由于\n活动及\n酶释放被抑制，使组织局部的\n冲动减少，痛觉\n的敏感性降低。治疗\n是通过消炎、镇痛、并不能纠正\n。治疗\n的作用机理可能是前列腺素合成受到抑制使子宫内压力下降、宫缩减少。\n\n\n\n口服易吸收，与食物同服时吸收减慢，但吸收量不减少。与含铝和镁的\n同服不影响吸收。\n为99%。服药后1.2～2.1小时\n达峰值, 用量200mg,血药浓度为22～27μg/ml, 用量400mg时为23～45μg/ml, 用量600mg时为43～57μg/ml。一次给药后半衰期一般为1.8～2小时。本品在肝内\n, 60～90%经肾由尿排出，100%于24小时内排出，其中约1％为原形物，一部分随粪便排出。\u3000\u3000\n\n布洛芬是有效的PG\n，具有\n镇痛及抗炎作用。用于\n、\n、下\n痛、\n、\n、\n及\n。\n和术后疼痛、\n、\n以及其他\n阴性(非\n性)\n。\u3000\u3000\n\n用于减轻中度疼痛，如\n、\n、\n、头痛、牙痛、\n、\n，也可用于减轻普通\n或\n引起的\n。\n\n1．成人常用量口服。①\n，一次 0.4—0.8g，一日 3-4次，类风湿性关节炎比骨关节炎用量要大些；②轻或中等疼痛及痛经的止痛，一次 0.2—0.4，每 4-6小时一次。成人用药最大限量一般为每天 2.4g(国外有人用至每天 3.6g)。\n\n2．小儿常用量口服。每次按体重 5-10mg/kg，一日 3次。\n\n[制剂与规格]\n(1)0.1g(2)0.2g\n\n口服,一日g,分3次饭时服.\u3000\u3000\n\n(1)交叉过敏：对\n或其他非甾体类消炎药过敏者对本品可有交叉\n。对阿司匹林过敏的\n患者，本品也可引起\n。\n\n(2)用于\n妇女可使孕期延长，引起难产及产程延长。孕妇及\n妇女不宜用。\n\n(3)对阿司匹林或其他非甾体类消炎药有严重过敏反应者禁用。有下列情况者应慎用：①哮喘，用药后可加重；②\n、\n，用药后可致水\n、\n；③\n或其他\n性\n(包括\n及\n功能异常)，用药后\n，\n加重；④有\n病史者，应用本品时易出现\n，包括产生新的溃疡；⑤\n者用药后\n增多，甚至导致\n。\n\n有潜在的\n患睚 三十地厅于有模有样。周身性\n患者发生过敏反应的危险大大高于\n病患者。\u3000\u3000\n\n①有些应用阿司匹林引起胃肠道不良反应的患者，可改用本品，但应密切注意不良反应、形成溃疡或发生出血等；②治疗类风湿性关节炎，本品还可与金制剂或皮质激素同用，症状缓解可更明显；③用药期间如出现胃肠出血，肝、肾功能损害，\n障碍、血象异常以及过敏反应等情况，应立即停药。\n\n长期用药时应定期检查血象及肝、\n。\u3000\u3000\n\n①\n、胃烧灼感或\n、\n或不适感(胃肠道刺激或溃疡形成)、\n、\n、\n等，发生率可达 3-9％；②\n、\n、\n或体重骤增、\n、\n、\n、\n或消失、\n、\n等，发生率可达 1—3％；③血便或\n(\n)、过敏性\n、\n、\n、\n或肾功能衰竭、\n、支气管痉挛、视力模溯、\n、\n减退、精神恍惚、\n、\n等很少见，发生率＜1％。\n\n个别病例有\n,消化不良,胃肠道溃疡及出血,\n。\n\n最常见的不良反应是胃肠系统，其发生率高达30％，从\n到严重的出血或使消化溃疡复发。\n的不良反应极为常见，但较轻，如头痛或头晕。长期大剂量使用时可发生\n病或\n。肝\n作用十分轻微。过敏反应不常见，可能出现伴有皮疹的\n、\n、头痛、恶心和呕吐，\n损害甚至出现\n症状。\n\n应用此药时常见盐及\n，从而引起充血性\n，但很罕见。\n\n此药对\n能引起哮喘发作。它能引起哮喘患者的\n收缩。\n\n中枢神经系统症状较常见，其中头痛、\n、耳鸣和失眠的发生率最高，但很少出现\n或其他精神症状。有些中枢神经系统症状如\n、脑膜炎、嗜睡及易\n，可能是由于过敏反应。\n\n此药具有强的胃毒性作用，各种胃肠道的刺激症状(如恶心、呕吐、\n、消化不良、烧心、腹痛、隐血、\n和溃疡发作而致大出血)的发生率极高，一般在30～40％左右。使用布洛芬\n后可发生疼痛和刺激\n粘膜。\n\n布洛芬在体内、体外均抑制\n，剂量低于1g时，\n无明显变化；但大剂量下可使出血时间延长，但不如阿司匹林。它还可诱致不同程度的各种血液病，如\n、\n、血小板缺乏症及致命的全\n减少症。有报告发生不易恢复的白细胞再生不良伴\n增多及\n中有依赖IgG\n的\n。个别病例可因胃肠道隐血而导致\n。\n\n它使\n中\n浓度升高，甚至有时达到有病理学意义。\n\n过敏性皮肤反应不常见，多为短暂性荨麻疹、\n性或\n性改变，常伴有瘙痒。也有报告发生\n者。\u3000\u3000\n\n(1)饮酒或与其他非甾体类消炎药同用时增加胃肠道副作用，并有致溃疡的危险。长期与\n同用时可增加对肾脏的\n。\n\n(2)与阿司匹林或其他\n类药物同用时，药效不增强，而胃肠道不良反应及出血倾向发生率增高。\n\n(3)与\n、\n等\n及血小板聚集抑制药同用时有增加出血的危险。\n\n(4)与\n同用时，后者的排钠和降压作用减弱。\n\n(5)与\n、\n同用时，本品的\n。\n\n(6)本品可增高\n的血浓度，同用时须注意调整地高辛的剂量。\n\n(7)本品可增强抗\n药(包括口服\n)的作用。\n\n(8)本品与\n同用时可影响后者的降压效果。\n\n(9)\n可降低本品的\n，增加血药浓度，从而增加毒性，故同用时宜减少本品剂量。\n\n(10)本品可降低\n的排泄，增高其血浓度，甚至可达\n水平，故本品不应与中或大剂量甲氨蝶呤\n同用。\n\n它使各种降压药的降压作用减低，它抑制\n的降解。\n', 'title': '布洛芬'}, {'url': 'https://m.youlai.cn/sjingbian/article/3A3309gPUOf.html', 'text': '布洛芬是一种非甾体类抗炎镇痛药，这类药物通过抑制体内环氧化酶活性，减少局部组织前列腺素的生物合成，从而发挥药理作用。具有解热、镇痛和抗炎的作用。并且布洛芬有多种剂型，包括布洛芬片、布洛芬糖浆、布洛芬混悬液、布洛芬缓释胶囊等，以满足不同患者的需求。\n布洛芬可通过下丘脑体温调节中心起到解热作用，临床可用于缓解普通感冒或流行性感冒引起的发热。布洛芬是世界卫生组织推荐的解热止痛药之一，其优点是退热平稳且持久，控制退热时间平均为6-8小时，对于39℃以上的高热退热效果较好。\n布洛芬可通过抑制前列腺素的合成，减轻因前列腺素引起的组织充血、肿胀，降低周围神经痛觉的敏感性，从而起到镇痛作用。临床多用于缓解轻至中度疼痛，如头痛、关节痛、偏头痛、牙痛、肌肉痛、神经痛、痛经等。\n布洛芬还可通过抑制前列腺素的合成来抑制炎症反应，可用于缓解类风湿关节炎、痛风性关节炎、风湿性关节炎等各种慢性关节炎导致的不适。此外，布洛芬还能抑制血小板活化因子引起的血小板聚集，预防血栓形成。\n在使用布洛芬时，患者需要注意用药前应仔细阅读药品说明书，了解药物的用法用量和注意事项，以确保用药的安全和有效性。', 'title': '布洛芬是什么，有什么作用'}]

        if self.recall_way == 'keyword':
            bg_text = self.rank_text_by_keywords(query,data)
        else:
            bg_text = self.rank_text_by_text2vec(query,data)
        return (bg_text)


from .config import Config
cfg = Config()
trr = TextRecallRank(cfg)
q_searching = trr.query_retrieve