from pygments import lex
import pygments.lexers as lexers
from pygments.token import Generic
from pygments.lexer import bygroups
from pygments.styles import get_style_by_name
import themes

class Lexer():
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.list = {} 
        for _tuple in lexers.get_all_lexers():
            try:
                _lex = lexers.get_lexer_by_name(_tuple[0])
                if _lex is not None:
                    self.list[_tuple[0]] = [_tuple[0], _lex]
            except:
                print("Unable to find lexer class: {}".format(_tuple[0]))

        self.current_lexer = self.list["Python"]
        self.syntax_highlighting_tags = []
        self.style = self.load_style("monokai")
        
        

    def load_style(self, stylename):
        style = get_style_by_name(stylename)
        for token, opts in style.list_styles():
            kwargs = {}
            fg = opts['color']
            bg = opts['bgcolor']
            if fg:
                kwargs['foreground'] = '#' + fg
            if bg:
                kwargs['background'] = '#' + bg
            font = (themes.DEFAULT["font"], themes.DEFAULT["font_size"]) + tuple(key for key in ('bold', 'italic') if opts[key])
            kwargs['font'] = font
            kwargs['underline'] = opts['underline']
            self.text_widget.tag_configure(str(token), **kwargs)
            self.syntax_highlighting_tags.append(str(token))
        self.text_widget.configure(bg=style.background_color,
                        fg=self.text_widget.tag_cget("Token.Text", "foreground"),
                        selectbackground=style.highlight_color)
        self.text_widget.tag_configure(str(Generic.StrongEmph), font=(themes.DEFAULT["font"], themes.DEFAULT["font_size"], 'bold', 'italic'))
        self.syntax_highlighting_tags.append(str(Generic.StrongEmph)) 
        return style
        
    def scan(self):
        start = 'insert linestart'
        end = 'insert lineend'
        data = self.text_widget.get(start, end)

        while data and data[0] == '\n':
            start = self.text_widget.index('%s+1c' % start)
            data = data[1:]

        self.text_widget.mark_set('range_start', start)

        for t in self.syntax_highlighting_tags:
            self.text_widget.tag_remove(t, start, "range_start +%ic" % len(data))

        for token, content in lex(data, self.current_lexer[1]):
            self.text_widget.mark_set("range_end", "range_start + %ic" % len(content))
            for t in token.split():
                self.text_widget.tag_add(str(t), "range_start", "range_end")
            self.text_widget.mark_set("range_start", "range_end")
            


