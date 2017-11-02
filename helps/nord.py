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


class QueryQueue:
    
    def __init__(self, item, p):
        self.workers = []
        self.phrases = [cfgparser.getTranslation(i, item) for i in p]
        self.appender()
        
    def appender(self):
        for i,v in enumerate(self.phrases):
            quotes_extended = v + list(map(lambda p: '"%s"' % p, v))
            self.workers.append(Selector(quotes_extended[:10], tname=str(i)))
            if len(quotes_extended) > 10:
                self.workers.append(Selector(quotes_extended[10:], tname='e%s' % i))
    
    def q_start(self):
        for worker in self.workers:
            if not worker.api_answer and worker not in Selector.ACTIVE_SELECTORS:
                worker.start()
            if len(Selector.ACTIVE_SELECTORS) == 5:
                self.pause()
        self.pause()
                    
    def pause(self):
        for active in Selector.ACTIVE_SELECTORS:
            active.join()
    
    def getResult(self):
        answers = []
        for worker in self.workers:
            wname = worker.getName()
            if wname.startswith('e'):
                answers[int(wname[1:])] += worker.result
            answers.append(worker.result)
        return filter(lambda res: len(res) > 0, answers)


def toWordstat(qry, phrases):
    query = QueryQueue(qry, [''.join(re.findall(r'[\w+ ]', i.split(' |')[0].strip())) for i in phrases])
    query.q_start()
    if CONFIGS['default_show'] == 'excel':
        toExcel(query.getResult(), phrases, qry)
    elif CONFIGS['default_show'] == 'console':
        printReport(query.getResult())

def toExcel(data, faucetlist, listname):
    BOOK = Excel(os.path.abspath(os.path.dirname(sys.argv[0])) + '\\cfg_data\\data.xlsx')
    try:
        BOOK()
        BOOK.addSheet(listname)
        BOOK.changeColumnSize(2, 72)
        BOOK.changeColumnSize(3, 25)
        BOOK.changeColumnSize(5, 55)
        row = BOOK.findFreeRow()
        print('ROW:', row)
        for phr in data:
            #print(phr)
            BOOK.setVal(row, 1, 1 if row-1 == 0 else int(BOOK.getVal(row-1, 1)) + 1)
            BOOK.setVal(row, 3, phr[0]['Phrase'])
            for i in faucetlist:
                #print('*****', i, phr[0]['Phrase'], end=': ')
                sep = i.find('|')
                trademark = i[:sep-1].strip().lower()
                tm_in_phrase = False
                for qry_tm in range(len(phr)):
                    tm_in_phrase = trademark in phr[qry_tm]['Phrase'].lower()
                    if tm_in_phrase: break
                if tm_in_phrase:
                    BOOK.setVal(row, 2, i[sep+1:])
                    #print('YEYS:', i[sep+1:])
                    faucetlist.remove(i)
                    break
            BOOK.setVal(row, 5, '\n'.join('{} :: {}'.format(i['Phrase'], i['Shows']) for i in phr))
            row += 1
    finally:
        BOOK.quit()        

def printReport(rep_list):
    for rep in rep_list:
        print('***********************')
        for phr in rep:
            print(phr['Phrase'], '::', phr['Shows'])
        print('***********************\n')

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
                if ~(i.find(q.lower())):
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