from win32com.client import Dispatch
import sys

class Excel:

    def __init__(self, path):
        self.obj = None
        self.path = path
        self.logging = False
        
    def __call__(self, logging=True):
        if self.obj == None:
            if logging:
                print('Excel открывается...')
                self.logging = logging
            self.open(self.path)
        
    def open(self, book):
        self.obj = Dispatch('Excel.Application')
        self.book = self.obj.Workbooks.Open(book)

    def addSheet(self, name):
        name = name[:31]
        try:
            self.sh = self.book.Sheets.Add()
            self.sh.Name = name
        except:
            print('Лист "%s" уже существует' % (name))
            self.book.Sheets(self.sh.Name).Delete()
            self.selectSheet(name)
        
    def selectSheet(self, name):
        try:
            self.sh = self.book.Sheets(name)
        except:
            print('Ошибка при загрузке листа "%s"' % name)
            sys.exit(1)
    
    def setVal(self, row, col, val):
        self.sh.Cells(row, col).value = val
        
    def getVal(self, row, col):
        if row < 1:
            print('Недопустимый номер строки:', row)
        try:
            return self.sh.Cells(row, col).value
        except AttributeError:
            print('Не выбран лист')
            sys.exit(1)
        
    def getRow(self, row, rowsize):
        return [self.getVal(row, i) for i in range(1, rowsize+1)]
    
    def changeColumnSize(self, col, px):
        self.sh.Columns(col).ColumnWidth = px

    def findFreeRow(self, col=1):
        self.row = 1
        while True:
            if self.sh.Cells(self.row,col).value == None \
            and self.sh.Cells(self.row+1,col).value == None:
                return self.row
            self.row += 1

    def quit(self):
        if self.obj != None:
            self.book.Save()
            self.book.Close()
            self.obj.Quit()
            self.obj = None
            if self.logging:
                print('Excel закрывается...')
        
    def __del__(self):
        self.quit()
