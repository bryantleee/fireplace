#!/usr/bin/env python
import tkinter as tk
from PIL import ImageTk, Image

import fireplace

win = tk.Tk()
win.title('fireplace')
win.geometry('500x360')  
win.resizable(0, 0)

panel = tk.Label(win)
panel.pack()

fp = fireplace.Fireplace()
images = iter(fp)  

def next_img():    
    img = next(images)  # get the next image from the iterator

    img = ImageTk.PhotoImage(img)
    panel.img = img  # keep a reference so it's not garbage collected
    panel['image'] = img
    
    win.after(100, next_img)

panel.config(image='')
next_img()

win.mainloop()
