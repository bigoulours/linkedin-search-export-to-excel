import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.tooltip import ToolTip
try:
    from .customWidgets import *
except:
    from customWidgets import *

class SearchFrame(ttk.Frame):
    def __init__(self, parent_widget, title='', completion_list=None, fetch_url=None):
        super().__init__(parent_widget)
        first_row = ttk.Frame(self)
        first_row.pack(side='top', fill='x', pady=5)
        self.label = ttk.Label(first_row, text=title)
        self.label.pack(side='left', expand=False)
        ToolTip(self.label, text=f"Type characters matching the desired {title} and press <Down> to show available options.")
        self.entry = AutocompleteCombobox(first_row, completion_list=completion_list, fetch_fct=fetch_url)
        self.entry.pack(side='left', expand=True, fill="x", padx=10)

        second_row = ttk.Frame(self)
        second_row.pack(side='top', fill='x', pady=5)
        self.labels_scrolled_text = ScrolledText(second_row, wrap="word", height=2, autohide=True)
        self.labels_scrolled_text.pack(side='top', fill='x', padx=5, pady=0)
        self.labels_scrolled_text._text.configure(state="disabled")

        self.entry.set_selection_text(self, self.labels_scrolled_text)

    def get_current_selection(self):
        return [self.nametowidget(x[1]).lbl_name
                for x in self.labels_scrolled_text.dump('1.0', 'end-1c')[1:]]