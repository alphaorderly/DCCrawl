import CrawlMain
from information import *
import os
import tkinter
import information
import threading



if not os.path.isdir(SAVE_DIRECTORY):
    os.makedirs(SAVE_DIRECTORY)

def main():
    wn = tkinter.Tk()
    wn.geometry("300x100")
    wn.title("디시 크롤링")

    inp = tkinter.Entry(wn, width=250)
    inp.insert(0, '갤러리 주소 입력')
    inp.pack()

    button = tkinter.Button(wn, text="가져오기", command=lambda: ActionThread(inp, inp.get(), button, 2))
    button.pack()

    wn.mainloop()


def Action(Entry, URL, btn, am):
    Entry.config(state='disabled')
    btn.config(state='disabled')
    try:
        CrawlMain.mainCrawl(URL, am)
    except:
        Entry.config(state='normal')
        btn.config(state='normal')

def ActionThread(Entry, URL, btn, am):
    at = threading.Thread(target=Action, args=(Entry, URL, btn, am, ), daemon=True)
    at.start()


mainThread = threading.Thread(target=main)
mainThread.start()

