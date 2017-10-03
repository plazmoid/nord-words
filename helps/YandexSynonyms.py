#coding:utf-8
import string
import threading
import traceback
import urllib.request as req
import urllib.parse as parser
from collections import Counter
from html.parser import HTMLParser


class OneMoreHTMLParser(HTMLParser):
    
    def __init__(self):
        self.was_data = True
        HTMLParser.__init__(self)
    
    def feed(self, data):
        self.similarities = Counter()
        self.grab = False
        self.phraseMaker = ''
        HTMLParser.feed(self, data)
    
    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if 'highlight highlight_active' in attr:
                self.grab = True

    def handle_data(self, data):
        if self.grab:
            self.dat = data.strip().lower()
            if '%' not in self.dat:
                if not self.was_data:
                    self.phraseMaker += ' ' + self.dat
                else:
                    self.phraseMaker = self.dat
                self.grab = False
                self.was_data = False
        else:
            for i in data:
                if i not in string.whitespace:
                    self.was_data = True
                    if self.phraseMaker != '':
                        #print(self.phraseMaker, end=' :: ')
                        self.phraseMaker = self.phraseMaker.replace("'", " ")
                        #print(self.phraseMaker)
                        self.similarities[self.phraseMaker] += 1
                    self.phraseMaker = ''
                    break
    
    def getSim(self): #подсвеченные слова: кол-во
        return self.similarities if len(self.similarities) > 0 else None
    

class YandexCacheParser(threading.Thread):
    
    def __init__(self, itm):
        threading.Thread.__init__(self)
        self.fin = (None, set())
        self.cparser = OneMoreHTMLParser()
        self.itm = itm
        self.start()
        
    def run(self):
        try:
            self.page = req.urlopen(self.itm['saved-copy-url'], timeout=5)
            self.enc = self.page.info()['Content-Type']
            self.enc = self.enc[self.enc.find('=')+1:]
            self.page = self.page.read()
        except:
            #print('Exception occured in', self.itm['url'], e)
            return
        try:
            self.decoded = self.page.decode(self.enc)
        except UnicodeDecodeError:
            self.decoded = self.page.decode(self.enc, errors='ignore')
        except:
            traceback.print_exc()
        if self.decoded:
            self.cparser.feed(self.decoded)
        else:
            return
        self.fin = (self.decodeURL(self.itm['url']), self.cparser.getSim())

    def decodeURL(self, url):
        self.urlp = parser.urlsplit(url)
        if self.urlp.query != '':
            self.q = '?'
            self.q += parser.unquote(self.urlp.query) if '%' in self.urlp.query else self.urlp.query 
        else:
            self.q = ''
        self.p = self.urlp.path if '%' not in self.urlp.path else parser.unquote(self.urlp.path)
        return '{}{}{}'.format(self.urlp.netloc if 'xn--' not in self.urlp.netloc else self.urlp.netloc.encode('cp1251').decode('idna'),
                                self.p.replace("'", '%27') , self.q.replace("'", '%27'))

    def getEntries(self):
        return self.fin