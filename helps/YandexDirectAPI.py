from urllib import request as req
import json
import time
from Configs import CFGParser

class W_API:
    
    def __init__(self):
        self.data = CFGParser().getConfigs('api')

    def __interact(self):
        self.request = req.Request(self.data['url'], json.dumps(self.data, ensure_ascii=False).encode('utf-8'))
        print(self.data)
        self.answer = json.loads(req.urlopen(self.request, timeout=7).read().decode('utf-8'))
        try:
            return self.answer['data']
        except KeyError:
            return self.__err_handle()

    def __err_handle(self):
        if self.answer['error_code'] == 52:
            print('Error code 52')
            return self.__interact()
        else:
            print(self.answer)

    def createReport(self, phrases):
        if type(phrases) != list:
            phrases = list(map(lambda x: x.strip(), phrases.split(',')))
        self.data['method'] = 'CreateNewWordstatReport'
        self.data['param'] = {'GeoID': self.data['geoID'],
                              'Phrases': phrases}
        return self.__interact()

    def getReportList(self):
        self.data['method'] = 'GetWordstatReportList'
        return self.__interact()
        
    def getReport(self, rid):
        self.data['method'] = 'GetWordstatReport'
        self.data['param'] = rid
        return self.__interact()

    def deleteReport(self, rid):
        self.data['method'] = 'DeleteWordstatReport'
        self.data['param'] = rid
        return self.__interact()
    
    def deleteAll(self):
        for report in self.getReportList():
            print(report['ReportID'], self.deleteReport(report['ReportID']))

    def simpleRequest(self, query):
        self.report_id = self.createReport(query)
        self.ready = False
        print('Создаём отчёт:', query)
        while not self.ready:
            time.sleep(8)
            print('...')
            for report in self.getReportList():
                if report['ReportID'] == self.report_id:
                    if report['StatusReport'] == 'Done':
                        self.ready = True
                        break
                    elif report['StatusReport'] == 'Failed':
                        self.deleteReport(self.report_id)
                        raise Exception('Ошибка при создании отчёта')
        self.result = self.getReport(self.report_id)
        self.deleteReport(self.report_id)
        print(self.result)
        return self.result