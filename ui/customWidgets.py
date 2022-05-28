import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText

PADDING = 1

class RemovableLabel(ttk.Frame):
    def __init__(self, parent_widget, label_name, value=None, **kw):
        super().__init__(parent_widget, **kw)
        self.lbl_name = label_name
        self.value = value
        self.configure(borderwidth=1, relief="solid")
        lbl = ttk.Label(self, text=label_name, bootstyle='inverse-secondary', padding=PADDING)
        lbl.pack(side='left')
        close_btn = ttk.Button(self, text='x', bootstyle='secondary', padding=PADDING)
        close_btn.pack(side='left')
        close_btn['command'] = self.destroy

    def destroy(self) -> None:
        super().destroy()
        return

class AutocompleteCombobox(ttk.Combobox):

    def __init__(self, parent, completion_list=None, fetch_fct=None):
        super().__init__(parent)
        self.unbind_class("TCombobox", "<Down>")
        self.bind('<KeyRelease>', self.handle_keyrelease)
        if completion_list:
            self._completion_list = sorted(completion_list, key=str.lower)
            self['values'] = self._completion_list
        elif fetch_fct:
            self.fetch_fct = fetch_fct
            self.autocomplete = self.autocomplete_fetch

    def autocomplete(self):
        """autocomplete the Combobox"""
        # collect hits
        _hits = []
        for element in self._completion_list:
                if self.get().lower() in element.lower(): # Match case insensitively
                    _hits.append(element)
        # perform auto completion
        if _hits:
            self['values'] = _hits
        else:
            self['values'] = self._completion_list

        self.event_generate('<Button-1>')

    def handle_keyrelease(self, event):
        """event handler for the keyrelease event on this widget"""
        if event.keysym == "Down": 
            self.autocomplete() 
    
    def set_selection_text(self, parent_widget, selection_txt: ScrolledText):
        self.scrolled_text = selection_txt
        self.parent = parent_widget
        self.bind('<<ComboboxSelected>>', self.add_selection_to_scrolled_text)

    def add_selection_to_scrolled_text(self, event):
        if self.get() in self.parent.get_current_selection():
            pass
        else:
            rm_lbl = RemovableLabel(self.parent, self.get())
            self.scrolled_text.window_create("insert", window=rm_lbl, padx=3, pady=2)
        self.set('')
        self.parent.update()
    
    def autocomplete_fetch(self):
        """autocomplete the Combobox"""
        # collect hits
        _hits = []
        for element in self._completion_list:
                if self.get().lower() in element.lower(): # Match case insensitively
                    _hits.append(element)
        # perform auto completion
        if _hits:
            self['values'] = _hits
        else:
            self['values'] = self._completion_list

        self.event_generate('<Button-1>')

