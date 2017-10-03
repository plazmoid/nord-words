#coding:utf-8
import urllib.request as req
import urllib.parse as parser
import xml.etree.ElementTree as ET
import time
from collections import defaultdict
from YandexSynonyms import YandexCacheParser


class HyperParser():
     
    def __init__(self, q):
        self.q = q
        self.xml = ''

    def toYandex(self):
        self.yand = 'https://yandex.ru/search/xml'
        self.KEY = '03.24114785:cb9c5827646a4708d005539662f9d434' #rizon321
        #self.KEY = '03.274741145:71364e6b1d5afa277cc7d5dd3701f752' #kronos44
        self.GROUPBY = 'attr%3Dd.mode%3Ddeep.groups-on-page%3D10.docs-in-group%3D1'
        self.params = {'user': 'rizon321',
                       #'user': 'kronos44',
                       'query': self.q,
                       'lr': '54',
                       'l10n': 'ru',
                       'sortby': 'rlv',
                       'filter': 'none'}
        self.params = '{}&key={}&groupby={}'.format(parser.urlencode(self.params), self.KEY, self.GROUPBY)
        with req.urlopen(self.yand + '?' + self.params) as query:
            self.xml = query.read().decode('utf-8')
            
    def parseXML(self, data=None): #TODO: группирование?
        if not data: data = self.xml
        #print('Парсируем xml...')
        self.xmldict = self.XMLtodict(ET.fromstring(data))
        try:
            self.primary = self.xmldict['yandexsearch']['response']['results']['grouping']['group']
        except:
            print(self.xmldict)
            raise KeyError
        self.res = []
        for i in self.primary:
            i = i['doc']
            if type(i) == list:
                i = i[0]
            try:
                self.res.append(self.fillres(i))
            except:
                #print('Ошибка в', i['url']+': отсутствует', e)
                pass
        #print('успешно!')

    def fillres(self, dic):
        self.t = {}
        self.t['url'] = dic['url']
        self.t['domain'] = dic['domain']
        self.t['mime-type'] = dic['mime-type']
        self.t['saved-copy-url'] = dic['saved-copy-url']
        self.t['title'] = dic['title']
        return self.t
        
    def XMLtodict(self, t):
        d = {t.tag: {} if t.attrib else None}
        children = list(t)
        if children:
            dd = defaultdict(list)
            for dc in map(self.XMLtodict, children):
                for k, v in dc.items():
                    dd[k].append(v)
            d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.items()}}
        if t.attrib:
            d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
        if t.text:
            text = t.text.strip()
            if children or t.attrib:
                if text:
                    d[t.tag]['#text'] = text
            else:
                d[t.tag] = text
        return d
    
    def toCache(self):
        #print('Ищем в яндо-кэше...')
        self.threads = []
        self.to_ret = []
        self.t = time.time()
        for itm in self.res:
            if itm['mime-type'] == 'text/html':
                self.threadParser = YandexCacheParser(itm)
                self.threads.append(self.threadParser)
        for thr in self.threads:
            thr.join()
        for i in self.threads:
            self.ent = i.getEntries()
            if self.ent[1] != None:
                self.to_ret.append(self.ent) #(url, подсвеченные слова)
        #print('...потрачено:', int(time.time() - self.t), 'сек.')
        return self.to_ret

def main():
    hp = HyperParser(str(input()))
    hp.toYandex()
    hp.parseXML()
    hltd = hp.toCache()
    print(hltd)

if __name__ == '__main__':
    main()