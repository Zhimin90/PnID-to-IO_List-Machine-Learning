# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 19:33:18 2020

@author: Zhimin
"""
from tkinter import *
from pandastable import Table, TableModel
import numpy as np
#import os
#assuming parent is the frame in which you want to place the table

#root = Tk()
#frame = Frame(root)
#frame.pack()
##root.mainloop()
#
#pt = Table(frame)
#pt.show()
#pt.importCSV('test.csv')
#pt.mainloop()

class popupWindow(object):
    
    def changeBlock( self,event ):
        self.location = str(event.x)+ "," + str(event.y)
        self.canvas.create_rectangle(event.x,event.y,event.x+10,event.y+10,fill='blue')
        
    def __init__(self, master, locations):
        top=self.top=Toplevel(master)
        top.minsize(width=1000, height=800)
        self.canvas = Canvas(top, width=120, height=80, bg='black')
        self.canvas.pack(expand=YES, fill=BOTH)
        self.gif1 = PhotoImage(file='BP Baltimore Satellite.PNG')
        self.canvas.create_image(50, 10, image=self.gif1, anchor=NW)

        for location in locations:
            print(location)
            x,y = tuple(location.split(","))
            x = int(x)
            y = int(y)
            self.canvas.create_rectangle(x,y,x+10,y+10,fill='red')
        self.canvas.bind('<Button-1>', self.changeBlock)  
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
        
        """Basic test frame for the table"""
        def __init__(self, parent=None):
            self.parent = parent
            Frame.__init__(self)
            self.main = self.master
            self.main.geometry('1680x1024+200+100')
            self.main.title('Table app')
            f = Frame(self.main)
            f.pack(fill=BOTH,expand=1)
            self.df = None
            #self.df = TableModel.getSampleData()
            self.table = pt = Table(f, dataframe=self.df,
                                    showtoolbar=True, showstatusbar=True)
            self.locColName = 'RLocation'
            try:
                print("loading pickle")
                pt.model.load("temp_model.pickle")
            except IOError:
                print("Couldn't find picke. Will load test.csv")
                pt.importCSV('test.csv')
                pt.model.addColumn(self.locColName, 'object')
            pt.model.moveColumn(pt.model.df.columns.get_loc(self.locColName),1)
            pt.bind('<Control-Button-1>', self.leftClicked)
            pt.bind('<Control-l>', self.learnModel)
            pt.show()
            return
        
        def leftClicked(self, event): 
            row = self.table.get_row_clicked(event)
            col = self.table.get_col_clicked(event)
            print(str(row)+ ", "+str(col))
            self.popUp()
            self.table.model.setValueAt(self.w.location, row, col, df=self.df)
            self.table.redrawVisible()
            self.table.model.save("temp_model.pickle")
            
        def popUp(self):
            self.w=popupWindow(self.master,self.getColumnAsArr(self.table.model.df))
            #self.b["state"] = "disabled" 
            self.master.wait_window(self.w.top)
            #self.b["state"] = "normal"

        def geEntryValue(self):
            return self.w.value
        
        def tagLocation(self):
            self.table.handleCellEntry(self, row, col)
        
        def getColumnAsArr(self, df):
            df = df[self.locColName].dropna()
            x = np.array(df,dtype="object")
            print("x: " + str(x))
            return x
        
        def learnModel(self, event): 
            print("learning Model")
            self.table.model.save("temp_model.pickle")
            import os 
            os.system('python LearnActionScript.py')
            print("done")
            self.table.model.load("learnedmodel.pickle")
            self.table.model.save("temp_model.pickle")
            self.table.model.moveColumn(self.table.model.df.columns.get_loc("ASIGateway_label"),1)
            self.table.redrawVisible()

app = TestApp()
#launch the app
app.mainloop()
