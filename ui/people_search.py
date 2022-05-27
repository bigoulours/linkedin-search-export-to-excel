import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.tooltip import ToolTip
try:
    from . import utils
    from .searchFrame import SearchFrame
except:
    import utils
    from searchFrame import SearchFrame
from tkinter import messagebox
import os
import threading
import pandas as pd
from pandastable import Table, TableModel


geo_urn_ids_filepath = 'resources/geo_urn_ids.txt'
geo_urn_ids = dict()
if os.path.isfile(geo_urn_ids_filepath):
    with open(geo_urn_ids_filepath, encoding='utf-8') as f:
        geo_kvpairs = f.readlines()
        for kvpair in geo_kvpairs:
            key, value = kvpair.split(':')
            key = key.strip()
            value = value.strip()
            geo_urn_ids[key] = value

company_public_ids_filepath = 'resources/Company_public_IDs.txt'
company_public_ids = []
if os.path.isfile(company_public_ids_filepath):
    with open(company_public_ids_filepath, encoding='utf-8') as f:
        company_public_ids = f.read().split('\n')


class PeopleSearch:
    def __init__(self, tk_parent, linkedin_conn):

        self.parent = tk_parent
        self.linkedin_conn = linkedin_conn

        self.search_results_df = pd.DataFrame()
        self.search_thread = None
        self.quick_search = True

        # Paned Window
        self.search_paned_window = ttk.PanedWindow(tk_parent, orient='horizontal')
        self.search_paned_window.pack(side='top', fill="both", expand=True, padx=10)

        search_fields_canvas = ttk.Canvas(self.search_paned_window)

        search_fields_frame = ScrolledFrame(search_fields_canvas)
        search_fields_frame.pack(side='top', fill='both', expand=True, padx=5)
        search_fields_frame.hide_scrollbars()

        # Connections
        conn_frame = ttk.Frame(search_fields_frame)
        conn_frame.pack(pady=5, side='top', fill='x')
        label_conn = ttk.Label(conn_frame, text="Connections")
        label_conn.pack(side='left', expand=False)
        self.first_con = ttk.BooleanVar()
        chckbox_first_con = ttk.Checkbutton(conn_frame, text="1st",
                                                    variable=self.first_con, bootstyle="primary")                                
        chckbox_first_con.pack(side='left', padx=10)

        self.second_con = ttk.BooleanVar()
        chckbox_second_con = ttk.Checkbutton(conn_frame, text="2nd",
                                                    variable=self.second_con, bootstyle="primary")                                
        chckbox_second_con.pack(side='left', padx=10)

        self.third_con = ttk.BooleanVar()
        chckbox_third_con = ttk.Checkbutton(conn_frame, text="3rd+",
                                                    variable=self.third_con, bootstyle="primary")                                
        chckbox_third_con.pack(side='left', padx=10)

        # KW-Frame
        kw_frame = ttk.Frame(search_fields_frame)
        kw_frame.pack(pady=5, side='top', fill="x")
        label_keywords = ttk.Label(kw_frame, text="Keywords")
        label_keywords.pack(side='left', expand=False)
        self.entry_keywords = ttk.Entry(kw_frame)
        self.entry_keywords.pack(side='left', expand=True, fill="x", padx=10)

        # KW-Title-Frame
        kw_title_frame = ttk.Frame(search_fields_frame)
        kw_title_frame.pack(pady=5, side='top', fill="x")
        label_keywords_title = ttk.Label(kw_title_frame, text="Keywords Title")
        label_keywords_title.pack(side='left', expand=False)
        self.entry_keywords_title = ttk.Entry(kw_title_frame)
        self.entry_keywords_title.pack(side='left', expand=True, fill="x", padx=10)

        ttk.Separator(search_fields_frame, orient='horizontal').pack(side='top', fill='x', pady=5)

        # Location Frame
        self.loc_frame = SearchFrame(search_fields_frame, title='Location', completion_list=geo_urn_ids.keys())
        self.loc_frame.pack(side='top', fill="x")

        ttk.Separator(search_fields_frame, orient='horizontal').pack(side='top', fill='x', pady=5)

        # Companies frame
        self.comp_frame = SearchFrame(search_fields_frame, title='Company', completion_list=company_public_ids)
        self.comp_frame.pack(side='top', fill="x")

        # for i in range(6):
        #     rm_lbl = RemovableLabel(self.company_labels_frame, f'foo-{i}')
        #     self.company_labels_frame.window_create("insert", window=rm_lbl, padx=3, pady=2)

        ttk.Separator(search_fields_frame, orient='horizontal').pack(side='top', fill='x', pady=5)

        self.search_paned_window.add(search_fields_canvas)

        # Table frame
        self.table_main_frame = ttk.Frame(tk_parent)
        # pandastable
        self.table_frame = ttk.Frame(self.table_main_frame, bootstyle="secondary", borderwidth=2)
        self.table_frame.pack(side="top", fill="both", expand=True)
        self.table = Table(self.table_frame, dataframe=pd.DataFrame(), showtoolbar=False, showstatusbar=True)
        utils.fit_table_style_to_theme(self.table, ttk.Style())
        self.table.unbind_all("<Tab>")
        self.table.unbind_all("<Return>")
        self.table.show()

        self.search_paned_window.add(self.table_main_frame)

        # Buttons frame
        btn_frame = ttk.Frame(tk_parent)
        btn_frame.pack(padx=10, pady=10, side='top', fill="x")

        quick_search_btn = ttk.Button(btn_frame, text="Quick search")
        quick_search_btn.pack(side='left', padx=10)
        quick_search_btn['command'] = self.start_quick_search
        ToolTip(quick_search_btn, "This is a single request that will yield the same results as in the linkedin search bar. \
\nIt doesn't contain any personal details (only public IDs) \
\nYou're not likely to reach any search limit using this mode.")

        start_search_btn = ttk.Button(btn_frame, text="Deep Search", bootstyle='danger')
        start_search_btn.pack(side='left')
        start_search_btn['command'] = self.start_deep_search
        ToolTip(start_search_btn, "Each search result will be fetched for additional information. \
            \nDepending on the number of results and search frequency, this can trigger the linkedin limit \
after which you'll only be able to get 3 results per search until the end of the month.")

        btn_sub_frame = ttk.Frame(btn_frame)
        btn_sub_frame.pack(side="left", fill="none", expand=True)
        self.get_skills = ttk.BooleanVar()
        chckbox_get_skills = ttk.Checkbutton(btn_sub_frame, text="Get skills",
                                                    variable=self.get_skills, bootstyle="primary")                                
        chckbox_get_skills.pack(side='top')

        self.export_to_file_btn = ttk.Button(btn_frame, text="Export to File", state="disabled")
        self.export_to_file_btn.pack(side='left')
        self.export_to_file_btn['command'] = self.prepare_dataframe_and_save_to_xsl

        # Status frame
        self.status_frame = ttk.Frame(tk_parent)
        self.status_frame.pack(padx=10, pady=2, side='bottom', expand=False, fill="x")
        self.status_str = ttk.StringVar(value="")
        self.label_status = ttk.Label(self.status_frame, textvariable=self.status_str)
        self.label_status.pack(side='left', expand=False)

        ttk.Separator(tk_parent, orient='horizontal').pack(side='bottom', fill='x')

    def run_search(self):
        keywords = self.entry_keywords.get()
        company_names = self.comp_frame.get_current_selection()
        keywords_title = self.entry_keywords_title.get()
        locations = self.loc_frame.get_current_selection()
        network_depths = []
        if self.first_con.get():
            network_depths.append('F')
        if self.second_con.get():
            network_depths.append('S')
        if self.third_con.get():
            network_depths.append('O')
        try:
            companyIDs = []
            for company_name in company_names:
                try:
                    company = self.linkedin_conn[0].get_company(company_name)
                    companyIDs.append(company['entityUrn'].split(":")[-1])
                except Exception as e:
                    answer_is_yes = messagebox.askyesno("Warning", "No company found with public ID " + company_name +
                                                        "\nLook for the public ID of the company on LinkedIn:\n"
                                                        "https://www.linkedin.com/company/<public ID>\n\n Ignore and proceed anyway?")
                    if not answer_is_yes:
                        self.status_str.set("Search cancelled.")
                        self.parent.update()
                        return

            # see doc under https://linkedin-api.readthedocs.io/en/latest/api.html
            search_result = self.linkedin_conn[0].search_people(keywords=keywords, network_depths=network_depths, current_company=companyIDs, regions=locations,
                                            keyword_title=keywords_title, include_private_profiles=False)

            if self.quick_search:
                self.search_results_df = pd.DataFrame(search_result)
                self.table.updateModel(TableModel(self.search_results_df))
                self.table.redraw()

            else:
                result_size = len(search_result)
                self.status_str.set("Found " + str(result_size) + " results! Searching contact details... This can take a while...")
                self.parent.update()

                if result_size > 999:
                    answer_is_yes = messagebox.askyesno("Too many results!", "This search yields more than 1000 results (upper limit for this app).\nProceed anyway?")
                    if not answer_is_yes:
                        self.status_str.set("Search cancelled.")
                        self.parent.update()
                        return

                row = 1

                for people in search_result:
                    profile = self.linkedin_conn[0].get_profile(urn_id=people['urn_id'])
                    if profile != {}:
                        if 'geoLocationName' in profile.keys():
                            geolocation = profile['geoLocationName']
                        elif 'confirmedLocations' in company:
                            geolocation = company['confirmedLocations'][0]['city']
                        else:
                            geolocation = ""

                        profile_dict = {
                            'First Name': [profile['firstName']],
                            'Last Name': [profile['lastName']],
                            'Title': [profile['experience'][0]['title']],
                            'Company': [profile['experience'][0]['companyName']],
                            'Location': [geolocation],
                            'Headline': [profile['headline']],
                            'Profile Link': ['https://www.linkedin.com/in/' + profile['profile_id']]
                        }

                        if self.get_skills.get():
                            skills_raw = self.linkedin_conn[0].get_profile_skills(urn_id=people['urn_id'])
                            skills = [dic['name'] for dic in skills_raw]
                            profile_dict.update({'Skills': [skills]})

                        self.search_results_df = pd.concat([self.search_results_df,
                                                    pd.DataFrame(profile_dict)])

                        self.table.updateModel(TableModel(self.search_results_df))
                        self.table.redraw()
                        self.status_str.set("Scanned " + str(row) + " out of " + str(result_size) + " profiles")
                        self.parent.update()

                        row += 1

            self.export_to_file_btn.configure(state="normal")
            self.status_str.set("Done")
            self.parent.update()
        except Exception as e:
            utils.show_exception(e)
            self.status_str.set("Something went wrong! Check console output for more details.")
            self.parent.update()


    def create_search_thread(self):
        if not self.linkedin_conn[0]:
            messagebox.showinfo("Error", "First log into Linkedin!")
            return
        if self.search_thread and self.search_thread.is_alive():
            messagebox.showinfo("Search in progress", "Another search is still running.\nWait until it finishes or restart the program.")
            return
        self.search_thread = threading.Thread(target=self.run_search)
        self.search_thread.daemon = True
        self.search_thread.start()

    def start_quick_search(self):
        self.quick_search = True
        self.create_search_thread()

    def start_deep_search(self):
        self.quick_search = False
        self.create_search_thread()

    def prepare_dataframe_and_save_to_xsl(self):
        self.status_str.set("Exporting to File...")
        export_file = utils.save_dataframe_to_file(self.search_results_df)

        if export_file is not None:
            self.status_str.set("Table saved under " + export_file)
        else:
            self.status_str.set("Table could not be saved!")


if __name__ == "__main__":
    from linkedin_api import Linkedin

    root = ttk.Window()
    root.title("LinkedIn People Search")
    root.geometry("1280x720")

    # Login frame
    login_frame = ttk.Frame(root)
    login_frame.pack(pady=10, expand=False, fill="x")

    label_usr = ttk.Label(login_frame, text="User")
    label_usr.pack(side='left', expand=False, padx=5)
    entry_usr = ttk.Entry(login_frame)
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
            linkedin_conn[0] = Linkedin(entry_usr.get(), entry_pwd.get())
            messagebox.showinfo("Success", "Successfully logged into LinkedIn.")

        except Exception as e:
            messagebox.showinfo("Error", "Login failed!\nCheck username and password.\n2FA must be disabled in LinkedIn settings.")
            return

    connect_btn['command'] = connect_linkedin

    people_search = PeopleSearch(root, linkedin_conn)
    root.mainloop()
