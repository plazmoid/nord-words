from html.parser import HTMLParser
from YandexDirectAPI import W_API
from threading import Thread
from Configs import CFGParser
import re


__all__ = ['ALittleHTMLParser', 'Selector', 'NORD', 'cfgparser', 'CONFIGS']
NORD = 'https://www.nord24.ru'
cfgparser = CFGParser()
CONFIGS = cfgparser.getConfigs('main')
minus = cfgparser.getMinus('cfg_data\\minus-phrases.txt')
version_filter = re.compile(r'[0-9]')
symb_filter = re.compile(r'[^a-zA-Zа-яёА-ЯЁ0-9 ]*')

W_API().deleteAll()


class ALittleHTMLParser(HTMLParser):

    def __init__(self):
        self.grab = 0
        HTMLParser.__init__(self)

    def feed(self, data, mode=0):
        self.mode = mode
        self.result = {} if not self.mode else [] #{название товара: ссылка на товар} или список производителей
        #with open(r'd:\temp\just\page.html', 'w') as fo:
        #    fo.write(data)
        HTMLParser.feed(self, data)

    def handle_starttag(self, tag, attrs):
        if self.mode == 0: #первичная загрузка всех сортов товара
            try:
                if not self.grab and tag == 'div' and ('class', 'level2_li') in attrs:
                    self.grab = 1
                if self.grab and tag == 'a':
                    self.lbl, self.href = None, None
                    for i in attrs:
                        if i[0] == 'href':
                            self.href = i[1]
                        elif i[0] == 'title':
                            self.lbl = i[1]
                    if self.lbl != None and self.href != None:
                        self.result.update({self.lbl.lower(): self.href})
                    self.grab = 0
            except Exception as e:
                print(e)
        elif self.mode == 1: #загрузка производителей
            if tag == 'input' and ('class', 'trademark_checkbox') in attrs:
                self.grab = 1
            elif self.grab and tag == 'a':
                self.result.append(attrs[0][1].replace(attrs[0][1].strip('/').split('/')[-2]+'-', '')) #перепилить и перенести эту срань в nord.py
                self.grab = 2

    def handle_data(self, data):
        if self.mode == 1:
            if self.grab == 2:
                self.result[-1] = '{} | {}'.format(symb_filter.sub('', data), NORD + self.result[-1])
                self.grab = 0


#TODO: убрать фильтр с названий фирм с цифрами
class Selector(Thread): #в одном потоке могут вертеться одновременно до 10 записей, максимум - 5 потоков (ограничение яндекса)
    
    ACTIVE_SELECTORS = []
    
    def __init__(self, phrases, tname):
        Thread.__init__(self)
        self.setName('Thread #'+tname)
        self.phrases = phrases
        self.api_answer = None
        self.result = []
        
    def info(self):
        return (self.getName(), self.isAlive(), self.api_answer)
    
    def run(self):
        Selector.ACTIVE_SELECTORS.append(self)
        try:
            self.api_answer = W_API().simpleRequest(self.phrases)
            if self.findPhraseShows('"%s"' % self.phrases[0]) == 0:
                return
            self.api_answer = list(filter(lambda unit: unit['Phrase'][0] == '"' or \
                                       (unit['Phrase'][0] != '"' and self.findPhraseShows('"%s"' % unit['Phrase']) != 0), self.api_answer))
            self.api_answer = list(filter(lambda unit: unit['Phrase'][0] != '"', self.api_answer))
            for query in self.api_answer:
                if CONFIGS['use_SearchedAlso'].lower() == 'true':
                    try:
                        query['SearchedWith'] = query['SearchedWith']+query['SearchedAlso']
                    except KeyError:
                        pass
                query['SearchedWith'] = list(filter(lambda unit: version_filter.search(unit['Phrase']) == None, query['SearchedWith']))
                self.result += query['SearchedWith']
            for m_word in minus:
                self.result = list(filter(lambda unit: m_word.lower() not in unit['Phrase'].lower(), self.result))
            self.result.sort(key=lambda unit: unit['Shows'], reverse=True)
        except Exception as e:
            print('Error in %s: %s' % (self.getName(), e))
        finally:
            Selector.ACTIVE_SELECTORS.remove(self)

    def findPhraseShows(self, qr):
        for k in self.api_answer:
            for i in k['SearchedWith']:
                if qr in i['Phrase']:
                    return i['Shows']
