from tkinter import *
import re


class AutocompleteEntry(Entry):
    def __init__(self, lista, *args, **kwargs):
        Entry.__init__(self, *args, **kwargs)
        self.lista = lista        
        self.var = self["textvariable"]
        init_text = (self.var + '.')[:-1]
        self.var = self["textvariable"] = StringVar()
        self.var.set(init_text)

        self.var.trace('w', self.changed)
        self.bind("<Right>", self.selection)
        self.bind("<Up>", self.up)
        self.bind("<Down>", self.down)

        self.lb_up = False

    def changed(self, name, index, mode):
        if self.var.get() == '':
            if hasattr(self, "lb"):
                self.lb.destroy()
            self.lb_up = False
        else:
            words = self.comparison()
            if words:            
                if not self.lb_up:
                    self.lb = Listbox()
                    self.lb.bind("<Double-Button-1>", self.selection)
                    self.lb.bind("<Right>", self.selection)
                    parent_widget = Widget.nametowidget(self, self.winfo_parent())
                    self.lb.place(x=parent_widget.winfo_x()+self.winfo_x(), y=parent_widget.winfo_y()+self.winfo_y()+self.winfo_height())
                    self.lb_up = True

                self.lb.delete(0, END)
                for w in words:
                    self.lb.insert(END, w)
            else:
                if self.lb_up:
                    self.lb.destroy()
                    self.lb_up = False
        
    def selection(self, event):
        if self.lb_up:
            last_space_index = max({0, self.var.get().rfind('\n'), self.var.get().rfind(' ')})
            self.var.set(self.var.get()[0:last_space_index] + ' ' + self.lb.get(ACTIVE))
            self.var.set(self.var.get().strip() + ' ')
            self.lb.destroy()
            self.lb_up = False
            self.icursor(END)

    def up(self, event):
        if self.lb_up:
            if self.lb.curselection() == ():
                index = '0'
            else:
                index = self.lb.curselection()[0]
            if index != 0 and self.lb.curselection() != ():
                self.lb.selection_clear(first=index)
                index = str(int(index)-1)
            self.lb.selection_set(first=index)
            self.lb.activate(index)

    def down(self, event):
        if self.lb_up:
            if self.lb.curselection() == ():
                index = '0'
            else:
                index = self.lb.curselection()[0]
            if index != self.lb.size()-1 and self.lb.curselection() != ():
                self.lb.selection_clear(first=index)
                index = str(int(index)+1)        
            self.lb.selection_set(first=index)
            self.lb.activate(index)

    def comparison(self):
        if len(self.var.get()) > 0:
            pattern = re.compile('.*' + self.var.get().split()[-1] + '.*', re.IGNORECASE)
            return [w for w in self.lista if re.match(pattern, w)]
        else:
            return None

