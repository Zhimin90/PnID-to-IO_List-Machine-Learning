# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 19:33:18 2020

@author: Zhimin
"""
from tkinter import *
from pandastable import Table, TableModel
#assuming parent is the frame in which you want to place the table

root = Tk()
frame = Frame(root)
frame.pack()
#root.mainloop()

pt = Table(frame)
pt.show()
pt.importCSV('test.csv')
pt.mainloop()

class popupWindow(object):
    
    def changeBlock( self,event ):
        self.location = (event.x,event.y)
        print(str(event.x) + str(event.y))
        self.canvas.create_rectangle(event.x,event.y,event.x+10,event.y+10,fill='red')
        
    def __init__(self, master):
        top=self.top=Toplevel(master)
        top.minsize(width=800, height=600)
        self.canvas = Canvas(top, width=120, height=80, bg='black')
        self.canvas.pack(expand=YES, fill=BOTH)
        self.gif1 = PhotoImage(file='BP Baltimore Satellite.PNG')
        self.canvas.bind('<Button-1>', self.changeBlock)  
        self.canvas.create_image(50, 10, image=self.gif1, anchor=NW)
        self.b=Button(top,text='Ok',command=self.cleanup)
        self.b.pack()
        #self.l=Label(top,text="Hello World")
        #self.l.pack()
        #self.e=Entry(top)
        #self.e.pack()

        
    def cleanup(self):
        self.value=self.location
        self.top.destroy()

class TestApp(Frame):
        def importExcel(self, filename=None):
        if filename is None:
            filename = filedialog.askopenfilename(parent=self.master,
                                                          defaultextension='.xls',
                                                          initialdir=os.getcwd(),
                                                          filetypes=[("xls","*.xls"),
                                                                     ("xlsx","*.xlsx"),
                                                            ("All files","*.*")])

        data = pd.read_excel(filename,sheetname=None)
        for n in data:
            self.addSheet(n, df=data[n], select=True)
        return
    
        def leftClicked(self, event): 
            print("invoked")
            print(event)
            row = self.table.get_row_clicked(event)
            col = self.table.get_col_clicked(event)
            print(str(row)+ ", "+str(col))
            self.popUp()
            self.table.model.setValueAt(999, row, col, df=self.df)
            
        """Basic test frame for the table"""
        def __init__(self, parent=None):
       
            self.parent = parent
            Frame.__init__(self)
            self.main = self.master
            self.main.geometry('600x400+200+100')
            self.main.title('Table app')
            f = Frame(self.main)
            f.pack(fill=BOTH,expand=1)
            self.importExcel(filename=None)
            #self.df = TableModel.getSampleData()
            self.table = pt = Table(f, dataframe=self.df,
                                    showtoolbar=True, showstatusbar=True)
            pt.bind('<Button-1>', self.leftClicked)
            pt.show()
            return
        
        def popUp(self):
            self.w=popupWindow(self.master)
            #self.b["state"] = "disabled" 
            self.master.wait_window(self.w.top)
            #self.b["state"] = "normal"

        def geEntryValue(self):
            return self.w.value
        
        def tagLocation(self):
            self.table.handleCellEntry(self, row, col)

app = TestApp()
#launch the app
app.mainloop()
