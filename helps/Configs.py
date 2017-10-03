import re
import sys
import os

def sorting(method):
    def wrapper(self, fname):
        if self.CONFIGS['main']['sort'].lower() == 'true':
            self.__alph_sort(fname)
        return method(self, fname)
    return wrapper

class CFGParser:
    
    def __init__(self):
        self.PATH = os.getcwd() + '\\'
        self.COMMENTS = re.compile(r'#+.*')
        self.SPACES = re.compile(r'\s')
        self.CONFIGS = {}
        self.trans = None
        self.req_head = {'main', 'api'}
        self.req_par = {'default_show', 'use_SearchedAlso', 'url', 'token', 'login', 'sort', 'geoID'}
        self.__readConfigs()
    
    def readAll(self, file, rem_comments=True, splitby=None):
        try:
            with open(self.PATH+file, 'r') as fi:
                self.text = fi.read()
                if rem_comments:
                    self.text = self.COMMENTS.sub('', self.text)
                if splitby != None:
                    return self.text.split(splitby)
                else:
                    return self.text
        except Exception as e:
            print('Ошибка при открытии файла', file, e)

    def readGen(self, file):
        try:
            with open(self.PATH+file, 'r') as fi:
                for fstr in fi:
                    cfstr = self.COMMENTS.sub('', fstr.strip())
                    if len(cfstr) <= 1:
                        continue
                    else:
                        yield cfstr
        except Exception as e:
            print('Ошибка при открытии файла', file, e)
    
    @sorting
    def getMinus(self, file):
        self.rd = self.readAll(file, splitby='\n')
        return list(filter(lambda wlen: len(wlen) >=2, map(lambda phrase: phrase.replace('+', ' '), self.rd)))

    #@sorting
    def getTranslation(self, tm, item):
        if not self.trans:
            self.trans = self.readAll('cfg_data\\translations.txt', splitby='\n')
        for i in self.trans:
            if tm in i:
                res = list(map(lambda a: a.strip(), i.split('-')))
                translated = ['%s %s' % (item, res[0])]
                try:
                    translated += list(map(lambda a: '%s %s' % (item, a.strip()), res[1].split(',')))
                except IndexError:
                    pass
                return translated
        return ['%s %s' % (item, tm)]

    def getConfigs(self, param):
        if param == None or param not in self.req_head:
            raise Exception('Неверный конфигурационный заголовок', param)
        return self.CONFIGS[param].copy()
    
    def __alph_sort(self, file):
        self.data = self.readAll(file, False)
        with open(self.PATH+file, 'w') as fo:
            fo.write('\n'.join(sorted(self.data.split('\n'))))

    def __readConfigs(self):
        res_par = set()
        spltd = re.findall(r'\[\w+\][^\[]*', self.readAll('cfg_data\\config.ini'))
        for params in [i.split('\n', 1) for i in spltd]:
            it = {}
            for i in params[1].split('\n'):
                par = i.split('=')
                if len(par) == 2:
                    it[par[0].strip()] = par[1].strip()
            self.CONFIGS[params[0][1:-1]] = it
            res_par |= set(it.keys())
        if set(self.CONFIGS.keys()) != self.req_head or res_par != self.req_par:
            print('Конфигурационный файл повреждён')
            sys.exit(1)
        self.CONFIGS['api']['geoID'] = list(map(lambda x: int(x), self.CONFIGS['api']['geoID'].split(','))) 