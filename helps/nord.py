import sys
import os

h = False
if len(sys.argv) > 1:
    if sys.argv[1] == '-h':
        from YandexDirectAPI import W_API
        h = True
    else:
        print('Неверный параметр')
        sys.exit(1)
else:
    from urllib import request as req, error
    from Parsers import *
    from ExcelHandler import Excel
    import re
    import time

    BOOK = Excel(os.path.dirname(__file__) + '\\cfg_name\\.data.xlsx')
#queryqueue
#toexcel

class QueryQueue:
    
    def __init__(self, item, p):
        self.workers = []
        self.phrases = [cfgparser.getTranslation(i, item) for i in p]
        for i,v in enumerate(self.phrases):
            self.worker = Selector(v + list(map(lambda p: '"%s"' % p, v)), tname=str(i))
            self.workers.append(self.worker)
        self.workerController()
    
    def workerController(self):
        for worker in self.workers:
            if not worker.api_answer and worker not in Selector.ACTIVE_SELECTORS:
                worker.start()
            if len(Selector.ACTIVE_SELECTORS) == 5:
                for active in Selector.ACTIVE_SELECTORS:
                    active.join()
    
    def getResult(self):
        for worker in self.workers:
            yield worker.result

def fetchURL(url='', q=None):
    page = None
    while page == None:
        try:
            if q == None:
                page = req.urlopen(NORD+url, timeout=10)
            else:
                page = req.urlopen(q, timeout=7)
        except error.URLError:
            print('Ошибка соединения, пробуем снова (Ctrl+C для отмены)')
            time.sleep(1)
    p_encoding = page.info()['Content-Type']
    p_encoding = p_encoding[p_encoding.find('=')+1:]
    page = page.read()
    try:
        return page.decode(p_encoding)
    except UnicodeDecodeError:
        return page.decode(p_encoding, errors='ignore')

def toWordstat(qry, phrases):
    '''if CONFIGS['default_show'] == 'excel':
        BOOK()
        BOOK.addSheet(qry)
        BOOK.changeColumnSize(2, 72)
        BOOK.changeColumnSize(3, 25)
        BOOK.changeColumnSize(5, 55)
    res = []
    workers = []'''
    query = QueryQueue(qry, [''.join(re.findall(r'[\w+ ]', i.split(' |')[0].strip())) for i in phrases])
        
    #if CONFIGS['default_show'] == 'excel':
    #    BOOK.quit()

def helper():
    print('Добро пожаловать в режим прямого взаимодействия с API.')
    inst = W_API()
    attrs = vars(W_API)
    avlb = list(filter(lambda x: not x.startswith('_'), attrs.keys()))
    comms = 'Возможные команды (аргумент вводится через пробел, фразы через запятую):\n\t'+'\n\t'.join(avlb)
    print(comms)
    while True:
        c = str(input('>'))
        sep = c.find(' ')
        if sep != -1:
            if c[:sep] not in avlb:
                print(comms)
            else:
                print(attrs[c[:sep]](inst, c[sep+1:]))
        else:
            if c not in avlb:
                print(comms)
            else:
                print(attrs[c](inst))


def main():
    parser = ALittleHTMLParser()
    parser.feed(fetchURL())
    dic = parser.getd()
    if len(dic) == 0:
        raise Exception('Ошибка при загрузке страницы')
    print('Данные успешно загружены!')
    dkeys = list(dic.keys())
    dkeys.sort()
    while True:
        q = str(input('\nЗапрос: '))
        if q not in dkeys:
            for i in dkeys:
                if i.startswith(q.lower()) or (len(q) > 2 and ~(i.find(q.lower()))):
                    print('-->', i)
        else:
            parser.feed(fetchURL(url=dic[q]), mode=1)
            for i in parser.getd():
                print('-->', i)
            if str(input('Продолжить (y\\n)? ')).lower() == 'y':
                toWordstat(q, parser.getd())    

if __name__ == '__main__':
    if h:
        helper()
    else:
        main()