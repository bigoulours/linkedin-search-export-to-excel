import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText

PADDING = 1

class RemovableLabel(ttk.Frame):
    def __init__(self, parent_widget, label_name, value=None, **kw):
        super().__init__(parent_widget, **kw)
        self.parent = parent_widget
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
        try:
            self.parent.resize_text_box()
        except:
            pass
        return

class AutocompleteCombobox(ttk.Combobox):

    def __init__(self, parent, completion_list=None, completion_dict={}, fetch_fct=None):
        self.string_var = ttk.StringVar()
        super().__init__(parent, textvariable=self.string_var)
        self.unbind_class("TCombobox", "<Down>")
        self.bind('<KeyRelease>', self.handle_keyrelease)
        self._completion_dict = completion_dict
        if completion_list:
            self._completion_list = sorted(completion_list, key=str.lower)
            self['values'] = self._completion_list
        elif completion_dict:
            self._completion_list = sorted(completion_dict.keys(), key=str.lower)
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
        if self.string_var.get() in self.parent.get_current_selection():
            pass
        else:
            rm_lbl = RemovableLabel(self.parent, self.string_var.get(), 
                                    value=self._completion_dict.get(self.string_var.get(), None))
            self.scrolled_text.window_create("insert", window=rm_lbl, padx=3, pady=2)
        self.set('')
        self.parent.resize_text_box()
    
    def autocomplete_fetch(self):
        """fetch dropdown content"""
        if self.string_var.get():
            fct_res = self.fetch_fct(self.string_var.get())
            if isinstance(fct_res, list):
                self['values'] = fct_res
            elif isinstance(fct_res, dict):
                self['values'] = sorted(fct_res.keys(), key=str.lower)
                self._completion_dict = fct_res
            else:
                print("Fetch function returned neither a list nor a dict. Not filling dropdown...")

        self.event_generate('<Button-1>')


class PlaceholderEntry(ttk.Entry):

    def __init__(self, container, placeholder, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.placeholder = placeholder

        self.placeholder_color = ttk.Style().colors.secondary
        self.default_fg_color = ttk.Style().colors.inputfg
        self['foreground'] = self.placeholder_color

        self.insert("0", self.placeholder)
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

    def _clear_placeholder(self, e):
        if self['foreground'].string == self.placeholder_color:
            self.delete("0", "end")
            self['foreground'] = self.default_fg_color

    def _add_placeholder(self, e):
        if not self.get():
            self.insert("0", self.placeholder)
            self['foreground'] = self.placeholder_color

    def get(self):
        if self['foreground'].string == self.placeholder_color:
            return ''
        else:
            return super().get()