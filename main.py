from tkinter import Tk as window_init
from window import Window as window_class

def init(_root, _window):
    _root.title(_window.name)
    _root.geometry(_window.geometry)
    _root.config(menu=_window.menu_bar)
    _root.iconphoto(True, _window.icon)

    _window.pack(side="top", fill="both", expand=True)
    _window.text_widget.pack(side="right", fill="y", expand=True)
    _window.scroll_bar.pack(side="right", fill="y")
    _window.line_counter.pack(side="left", fill="y")

root = window_init()
window = window_class(root)
init(root, window)
root.mainloop()
