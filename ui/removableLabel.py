import ttkbootstrap as ttk

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