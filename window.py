from tkinter import *
from tkinter.ttk import *
import tkinter.filedialog as tk_file_dialog
import tkinter.font as tk_font
import os
import platform
import themes
import syntax

DEFAULT_EDITOR_NAME = "kite-text-editor"
DEFAULT_GEOMETRY = "800x600"
START_TEXT = "print('Hello World!')"

class LineCounter(Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_widget = None
        
    def attach_widget(self, text_widget):
        self.text_widget = text_widget

    def update(self, *args):
        self.delete("all")
        index = self.text_widget.index("@0,0")
        while True:
            line = self.text_widget.dlineinfo(index)
            if line is None: 
                break
            pos = line[1]
            number = str(index).split(".")[0]
            self.create_text(10, pos, anchor="nw", text=number, fill="white")
            index = self.text_widget.index("%s+1line" % index)

class TextWidget(Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.insert(1.0, START_TEXT)

        self._origin = self._w + "_orig"
        self.tk.call("rename", self._w, self._origin)
        self.tk.createcommand(self._w, self._proxy)
        
    def _proxy(self, *args):
        cmd = (self._origin,) + args
        result = self.tk.call(cmd)

        if (args[0] in ("insert", "replace", "delete") or
            args[0:3] == ("mark", "set", "insert") or
            args[0:2] == ("xview", "moveto") or
            args[0:2] == ("xview", "scroll") or
            args[0:2] == ("yview", "moveto") or
            args[0:2] == ("yview", "scroll") 
        ):
            self.event_generate("<<Change>>", when="tail")

        return result

class Window(Frame):
    def save_as(self):
        self.file_name = None
        self.file = tk_file_dialog.asksaveasfile(filetypes=[('Python', '*.py'),('Text', '*.txt')], confirmoverwrite=True, defaultextension=".txt")
        if self.file is None:
            return 
        else:
            self.file_name = self.file.name
            base = os.path.basename(self.file_name)
            self.root_ref.title(self.name + " - '{}'".format(str(base)))
        
        file_text = str(self.text_widget.get(1.0, END))
        self.file.write(file_text)
        self.file.close()

    def save(self):
        try:
            if self.file_name is not None and self.file is not None:
                with open (self.file, 'r+') as file:
                    data = file.read()
                    file.seek(0)
                    file.write(str(main_text.get(1.0, END)))
                    file.truncate()
            elif self.open_file is not None:
                with open (self.open_file, 'r+') as file:
                    data = file.read()
                    file.seek(0)
                    file.write(str(main_text.get(1.0, END)))
                    file.truncate()
        except AttributeError:
            self.save_as()

    def _open(self):
        self.open_file = tk_file_dialog.askopenfile(mode = "r", title = "Open A Text File")
        if self.open_file is not None:
            content = self.open_file.read()
            main_text.delete(0.0, END)
            main_text.insert(END, content) 


    def exit_editor(self):
        self.root_ref.destroy()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        #window properties
        self.name = DEFAULT_EDITOR_NAME
        self.geometry = DEFAULT_GEOMETRY
        self.icon = PhotoImage(file="assets/icon.png")
        self.root_ref = args[0]
        

        #objects
        self.font = tk_font.Font(family=themes.DEFAULT["font"], size=themes.DEFAULT["font_size"])
        self.text_widget = TextWidget(self, width=800, height=600, wrap=WORD, font=self.font, bg=themes.DEFAULT["background"], fg=themes.DEFAULT["foreground"], insertbackground=themes.DEFAULT["foreground"], highlightthickness=0, relief=SOLID, padx=4)
        self.scroll_bar = Scrollbar(self, orient="vertical", command=self.text_widget.yview)
        self.scroll_bar.pack()
        self.text_widget.configure(yscrollcommand=self.scroll_bar.set)
        self.lexer = syntax.Lexer(self.text_widget)
        self.lexer.scan()
        self.line_counter = LineCounter(self, width=40, bg=self.lexer.style.background_color, bd=0)
        self.line_counter.attach_widget(self.text_widget)
        self.line_counter.pack()
       

        self.menu_bar = Menu(self)

        #topbar-objects
        self.tabs = Menu(self.menu_bar, tearoff=0)
        self.tabs.add_command(label="Save File As", command=self.save_as)
        self.tabs.add_command(label="Save File", command=self.save)
        self.tabs.add_command(label="Open", command=self._open)
        self.tabs.add_separator()
        self.tabs.add_command(label="Exit", command=self.exit_editor)

        self.syntax = Menu(self.menu_bar, tearoff=0)
        for idx in self.lexer.list:
            self.syntax.add_command(label=idx, command=None)

        self.menu_bar.add_cascade(label="File", menu=self.tabs)
        #self.menu_bar.add_cascade(label="Syntax", menu=self.syntax)

        #bindings
        self.text_widget.bind("<<Change>>", self._on_change)
        self.text_widget.bind("<Configure>", self._on_change)
        self.text_widget.bind("<KeyRelease>", lambda event: self.lexer.scan())

    def _on_change(self, event):
        self.line_counter.update()
