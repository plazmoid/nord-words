from win32com.client import Dispatch

class Excel:

    def __init__(self, path):
        self.obj = None
        self.path = path
        
    def __call__(self):
        if self.obj == None:
            print('Excel открывается...')
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
        self.sh = self.book.Sheets(name)
    
    def setVal(self, row, col, val):
        self.sh.Cells(row, col).value = val
        
    def getVal(self, row, col):
        return self.sh.Cells(row, col).value
        
    def changeColumnSize(self, col, px):
        self.sh.Columns(col).ColumnWidth = px

    def findFreeRow(self):
        self.row = 1
        while True:
            if self.sh.Cells(self.row,1).value == None:
                return self.row
            self.row += 1

    def quit(self):
        if self.obj != None:
            self.book.Save()
            self.book.Close()
            self.obj.Quit()
            self.obj = None
            print('Excel закрывается...')
        
    def __del__(self):
        self.quit()
