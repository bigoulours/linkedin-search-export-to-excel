import ttkbootstrap as ttk
import tkinter
import re


class AutocompleteCombobox(ttk.Combobox):

    def set_completion_list(self, completion_list):
            """Use our completion list as our drop down selection menu, arrows move through menu."""
            self._completion_list = sorted(completion_list, key=str.lower) # Work with a sorted list
            self._hits = []
            self._hit_index = 0
            self.position = 0
            self.bind('<KeyRelease>', self.handle_keyrelease)
            self['values'] = self._completion_list  # Setup our popup menu

    def autocomplete(self):
            """autocomplete the Combobox"""
            self.position = len(self.get())
            # collect hits
            _hits = []
            for element in self._completion_list:
                    if self.get().lower() in element.lower(): # Match case insensitively
                        _hits.append(element)
            # if we have a new hit list, keep this in mind
            if _hits != self._hits:
                    self._hit_index = 0
                    self._hits=_hits
            # now finally perform the auto completion
            if self._hits:
                self['values'] = self._hits
            else:
                self['values'] = self._completion_list

            self.position = len(self.get())

    def handle_keyrelease(self, event):
            """event handler for the keyrelease event on this widget"""
            if event.keysym == "Right":
                    self.position = self.index(tkinter.END) # go to end (no selection)
            if event.keysym == "Down":
                    self.event_generate('<Button-1>')
            if len(event.keysym) == 1 or event.keysym == "BackSpace":
                    self.autocomplete()

