import ttkbootstrap as ttk
from ttkbootstrap.tooltip import ToolTip
from tkinter import messagebox
import os
import configparser
from pathlib import Path
from ui.people_search import PeopleSearch
from linkedin_api import Linkedin
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
login_frame.pack(pady=10, expand=False, fill="x")

label_usr = ttk.Label(login_frame, text="User")
label_usr.pack(side='left', expand=False, padx=5)
ToolTip(label_usr, text="Pre-filled value can be edited in the .ini-file.\nBe sure to disable 2FA.")
entry_usr = ttk.Entry(login_frame)
entry_usr.insert(0, config_dict.get('General',{}).get('user', ''))
entry_usr.pack(side='left', expand=True, fill="x", padx=5)

label_pwd = ttk.Label(login_frame, text="Pwd")
label_pwd.pack(side='left', expand=False, padx=5)
entry_pwd = ttk.Entry(login_frame, show="*")
entry_pwd.pack(side='left', expand=True, fill="x", padx=5)

connect_btn = ttk.Button(login_frame, text="Connect")
connect_btn.pack(side='left', padx=5)

linkedin_conn = [None]

def connect_linkedin():
    # Authenticate using any Linkedin account credentials
    try:
        linkedin_conn[0] = Linkedin(entry_usr.get(), entry_pwd.get(),cookies_dir=config_dict.get('General',{}).get('cookies_dir', 'cookies/'))
        messagebox.showinfo("Success", "Successfully logged into LinkedIn.", icon='info')

    except Exception as e:
        messagebox.showinfo("Error",
                "Login failed!\nCheck username and password.\n2FA must be disabled in LinkedIn settings.",
                icon='error')
        return

connect_btn['command'] = connect_linkedin

# Tabs
tab_control = ttk.Notebook(top)

people_search_tab = ttk.Frame(tab_control)
tab_control.add(people_search_tab, text='People Search')

tab_control.pack(expand=1, fill="both")
top.update()

people_search_instance = PeopleSearch(people_search_tab, linkedin_conn)

top.mainloop()


