import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.tooltip import ToolTip
try:
    from .customWidgets import *
except:
    from customWidgets import *

class SearchFrame(ttk.Frame):
    def __init__(self, parent_widget, title='', completion_list=None, fetch_fct=None):
        super().__init__(parent_widget)
        self.parent=parent_widget
        first_row = ttk.Frame(self)
        first_row.pack(side='top', fill='x', pady=5)
        self.label = ttk.Label(first_row, text=title)
        self.label.pack(side='left', expand=False)
        ToolTip(self.label, text=f"Type characters matching the desired {title} and press <Down> to show available options.")
        self.entry = AutocompleteCombobox(first_row, completion_list=completion_list, fetch_fct=fetch_fct)
        self.entry.pack(side='left', expand=True, fill="x", padx=10)

        second_row = ttk.Frame(self)
        second_row.pack(side='top', fill='x', pady=5)
        self.labels_text_box = ScrolledText(second_row, wrap="word", height=0, autohide=True)
        self.labels_text_box.pack(side='top', fill='x', padx=5, expand=True)
        self.labels_text_box._text.configure(state="disabled", highlightthickness = 0, borderwidth=0)
        self.labels_text_box.bind( "<Configure>", self.resize_text_box)

        self.entry.set_selection_text(self, self.labels_text_box)

    def get_current_selection(self):
        return {(rm_lbl:=self.nametowidget(x[1])).lbl_name : rm_lbl.value
                for x in self.labels_text_box.dump('1.0', 'end-1c', window=True)
                if x[1]}

    def resize_text_box(self, *args):
        if self.get_current_selection():
            self.labels_text_box._text.configure(height=3)
            self.labels_text_box.pack(side='top', fill='x', padx=5, expand=True)
            self.update()
        else:
            self.labels_text_box._text.configure(height=0)
            self.update()
            self.labels_text_box.forget()
            self.update()
