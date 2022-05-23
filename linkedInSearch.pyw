import ttkbootstrap as ttk
import os
import configparser
from pathlib import Path
from ui.people_search import PeopleSearch
from CI.version import SW_VERSION

config = configparser.ConfigParser()
config.read(f"{Path(__file__).stem}.ini")
config_dict = {s:dict(config.items(s)) for s in config.sections()}

program_name = Path(__file__).stem + "-" + SW_VERSION

top = ttk.Window(themename=config_dict.get('General',{}).get('theme', 'cosmo'))
top.title(program_name)
top.geometry("1280x720")
try:
    top.iconbitmap("images/linkedin.ico")
except:
    print("LinkedIn icon not found. Using default.")
this_file_name = os.path.splitext(os.path.basename(__file__))[0]

# Login frame
login_frame = ttk.Frame(top)
login_frame.pack(padx=10, pady=5, expand=False, fill="x")
label_usr = ttk.Label(login_frame, text="User")
label_usr.pack(side='left', expand=False)
entry_usr = ttk.Entry(login_frame)
entry_usr.insert(0, config_dict.get('General',{}).get('user', ''))
entry_usr.pack(side='left', expand=True, fill="x")
label_pwd = ttk.Label(login_frame, text="Pwd")
label_pwd.pack(side='left', expand=False)
entry_pwd = ttk.Entry(login_frame, show="*")
entry_pwd.pack(side='left', expand=True, fill="x")

separator = ttk.Separator(top, orient='horizontal')
separator.pack(side='top', pady=10, fill='x')

# Tabs
tab_control = ttk.Notebook(top)

people_search_tab = ttk.Frame(tab_control)
tab_control.add(people_search_tab, text='People Search')

tab_control.pack(expand=1, fill="both")
top.update()

people_search_instance = PeopleSearch(people_search_tab, entry_usr, entry_pwd)

top.mainloop()


