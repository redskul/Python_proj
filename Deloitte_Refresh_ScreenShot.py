import tkinter as tool
from tkinter import filedialog

import pyautogui

root=tool.Tk()

canvas1=tool.Canvas(root,width=300,height=300)
canvas1.pack()

def takeScreenshot ():
    screenshot = pyautogui.screenshot()
    file_path=filedialog.asksaveasfilename(defaultextension='.png')
   # file_path=filedialog.asksaveasfile("C:\Users\pgarabadu\Desktop\TECO\screenshots")
    screenshot.save(file_path)
Button = tool.Button(text='capture',command='capture',bg='green',font=10)
canvas1.create_window(150,150,window=Button)

root.mainloop()
