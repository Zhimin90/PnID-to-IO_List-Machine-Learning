# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 19:02:39 2020

@author: Zhimin
"""
from tkinter import *

# create the canvas, size in pixels
canvas = Canvas(width=1200, height=800, bg='black')

# pack the canvas into a frame/form
canvas.pack(expand=YES, fill=BOTH)

# load the .gif image file
gif1 = PhotoImage(file='BP Baltimore Satellite.PNG')

def changeBlock( event=None ): 
        # Here, I'm just making a rectangle of size 10. Make it as big as you want
        # notice though that you're "self.canvas" will need to reference the
        # the right thing
        print(str(event.x) + str(event.y))
        canvas.create_rectangle(event.x,event.y,event.x+10,event.y+10,fill='red')

for row in range(10):
    for column in range(10):
        canvas.create_rectangle(10+(row*53),10+(column*53),60+(row*53),60+(column*53),fill='blue')

# Here, I'm binding to the Canvas. Bind to the widget where the event occurs
canvas.bind('<Button-1>',changeBlock)  

# make sure you add the widget somehow, or else it won't appear
canvas.grid()  
# put gif image on canvas
# pic's upper left corner (NW) on the canvas is at x=50 y=10
canvas.create_image(50, 10, image=gif1, anchor=NW)

# run it ...
mainloop()
