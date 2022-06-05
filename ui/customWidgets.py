import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.tooltip import ToolTip
from tkinter import messagebox

PADDING = 1

class RemovableLabel(ttk.Frame):
    def __init__(self, parent_widget, label_name, value=None, **kw):
        super().__init__(parent_widget, **kw)
        self.parent = parent_widget
        self.lbl_name = ttk.StringVar()
        self.lbl_name.set(label_name)
        self.value = value
        self.configure(borderwidth=1, relief="solid")
        lbl = ttk.Label(self, textvariable=self.lbl_name, bootstyle='inverse-secondary', padding=PADDING)
        lbl.pack(side='left')
        close_btn = ttk.Button(self, text='x', bootstyle='secondary', padding=PADDING)
        close_btn.pack(side='left')
        close_btn['command'] = self.destroy

    def destroy(self) -> None:
        super().destroy()
        try:
            # updating parent size if no more element:
            self.parent.resize_text_box()
        except:
            pass
        return

class AutocompleteCombobox(ttk.Combobox):

    def __init__(self, parent, completion_list=None, completion_dict={}, fetch_fct=None, single_choice=False):
        self.single_choice = single_choice
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
        # to be used inside SearchFrame
        self.scrolled_text = selection_txt
        self.parent = parent_widget
        self.bind('<<ComboboxSelected>>', self.add_selection_to_scrolled_text)

    def add_selection_to_scrolled_text(self, event):
        curr_sel = self.parent.get_current_selection()
        if self.string_var.get() in [x.lbl_name.get() for x in curr_sel]:
            pass
        else:
            rm_lbl = RemovableLabel(self.parent, self.string_var.get(), 
                                    value=self._completion_dict.get(self.string_var.get(), None))
            if curr_sel and self.single_choice:
                curr_sel[0].lbl_name.set(rm_lbl.lbl_name.get())
                curr_sel[0].value = rm_lbl.value
            else:
                self.scrolled_text.window_create("insert", window=rm_lbl, padx=3, pady=2)
        self.set('')
        self.parent.resize_text_box()
    
    def autocomplete_fetch(self):
        """fetch dropdown content"""
        if self.string_var.get():
            try:
                fct_res = self.fetch_fct(self.string_var.get())
            except:
                messagebox.showinfo("Warning", 
                    "Could not fetch dropdown content. Check your connection or log into the corresponding service.")
            if isinstance(fct_res, list):
                self['values'] = fct_res
            elif isinstance(fct_res, dict):
                self['values'] = sorted(fct_res.keys(), key=str.lower)
                self._completion_dict = fct_res
            else:
                print("Fetch function returned neither a list nor a dict. Not filling dropdown...")

        self.event_generate('<Button-1>')


class SearchFrame(ttk.Frame):
    def __init__(self,  parent_widget,
                        title='',
                        completion_list=None, 
                        completion_dict=None,
                        fetch_fct=None,
                        single_choice=False):
        super().__init__(parent_widget)
        self.parent=parent_widget
        first_row = ttk.Frame(self)
        first_row.pack(side='top', fill='x', pady=5)
        label = ttk.Label(first_row, text=title)
        label.pack(side='left', expand=False)
        if fetch_fct:
            ToolTip(label, text=f"Type characters matching the desired {title} and press <Down> to show available options.")
        self.entry = AutocompleteCombobox(first_row, completion_list=completion_list, 
                            completion_dict=completion_dict, fetch_fct=fetch_fct, single_choice=single_choice)
        self.entry.pack(side='left', expand=True, fill="x", padx=10)

        second_row = ttk.Frame(self)
        second_row.pack(side='top', fill='x')
        if single_choice:
            vbar=False
        else:
            vbar=True
        self.labels_text_box = ScrolledText(second_row, wrap="word", height=0, autohide=True, vbar=vbar)
        self.labels_text_box.pack(side='top', fill='x', padx=5, expand=True)
        self.labels_text_box._text.configure(state="disabled", highlightthickness = 0, borderwidth=0)
        self.labels_text_box.bind( "<Configure>", self.resize_text_box)

        self.entry.set_selection_text(self, self.labels_text_box)

    def get_current_selection(self):
        return [self.nametowidget(x[1])
                for x in self.labels_text_box.dump('1.0', 'end-1c', window=True)
                if x[1]]

    def resize_text_box(self, *args):
        # cleaning old labels:
        for lbl in self.labels_text_box.dump("1.0", "end", window=True)[::-1]:
            if not lbl[1]:
                self.labels_text_box.delete(lbl[2])
        # resizing if necessary:
        if self.get_current_selection():
            self.labels_text_box._text.configure(height=3)
            self.labels_text_box.pack(side='top', fill='x', padx=5, expand=True)
            self.update()
        else:
            self.labels_text_box._text.configure(height=0)
            self.update()
            self.labels_text_box.forget()
            self.update()


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