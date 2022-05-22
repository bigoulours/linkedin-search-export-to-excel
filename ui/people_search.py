import ttkbootstrap as ttk
from linkedin_api import Linkedin
try:
    from .autocompleteEntry import AutocompleteEntry
    from . import utils
except:
    from autocompleteEntry import AutocompleteEntry
    import utils
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
        public_ids = f.readlines()
        for id in public_ids:
            company_public_ids.append(id)

class PeopleSearch:
    def __init__(self, tk_parent, username_field, password_field):

        self.entry_usr = username_field
        self.entry_pwd = password_field

        self.parent = tk_parent

        self.search_results_df = pd.DataFrame()

        # Paned Window
        self.search_frame = ttk.PanedWindow(tk_parent, orient='horizontal')
        self.search_frame.pack(side='top', fill="both", expand=True, padx=10)

        search_fields_frame = ttk.Frame(self.search_frame)

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

        # Location Frame
        loc_frame = ttk.Frame(search_fields_frame)
        loc_frame.pack(pady=5, side='top', fill="x")
        label_locations = ttk.Label(loc_frame, text="Locations")
        label_locations.pack(side='left', expand=False)
        self.entry_locations = AutocompleteEntry(geo_urn_ids.keys(), loc_frame, width=50)
        self.entry_locations.pack(side='left', expand=False, padx=10)

        # Companies frame
        comp_frame = ttk.Frame(search_fields_frame)
        comp_frame.pack(pady=5, side='top', fill="x")
        label_companies = ttk.Label(comp_frame, text="Company public ID(s)")
        label_companies.pack(side='left', expand=False)
        self.entry_companies = AutocompleteEntry(company_public_ids, comp_frame)
        self.entry_companies.pack(side='left', expand=True, fill="x", padx=10)

        self.search_frame.add(search_fields_frame)

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

        self.search_frame.add(self.table_main_frame)

        # Buttons frame
        btn_frame = ttk.Frame(tk_parent)
        btn_frame.pack(padx=10, pady=10, side='top', fill="x")

        start_search_btn = ttk.Button(btn_frame, text="Search Now!")
        start_search_btn.pack(side='left')
        start_search_btn['command'] = self.create_start_search_thread

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

        separator = ttk.Separator(tk_parent, orient='horizontal')
        separator.pack(side='bottom', fill='x')

    def start_search(self):
        keywords = self.entry_keywords.get()
        company_names = self.entry_companies.get()
        keywords_title = self.entry_keywords_title.get()
        locations = [geo_urn_ids[x] for x in self.entry_locations.get().split() if x in geo_urn_ids.keys()]
        network_depths = []
        if self.first_con.get():
            network_depths.append('F')
        if self.second_con.get():
            network_depths.append('S')
        if self.third_con.get():
            network_depths.append('O')
        try:
            # Authenticate using any Linkedin account credentials
            try:
                api = Linkedin(self.entry_usr.get(), self.entry_pwd.get())
                self.status_str.set("Login successful!")
                self.parent.update()
                self.search_results_df = pd.DataFrame()
                self.export_to_file_btn.configure(state="disabled")
            except Exception as e:
                utils.show_exception(e)
                messagebox.showinfo("Error", "Login failed!\nCheck username and password.\n2FA must be disabled in LinkedIn settings.")
                return

            if company_names != "":
                companyIDs = []
                for company_name in company_names.split():
                    try:
                        company = api.get_company(company_name)
                        companyIDs.append(company['entityUrn'].split(":")[-1])
                    except Exception as e:
                        answer_is_yes = messagebox.askyesno("Warning", "No company found with public ID " + company_name +
                                                            "\nLook for the public ID of the company on LinkedIn:\n"
                                                            "https://www.linkedin.com/company/<public ID>\n\n Ignore and proceed anyway?")
                        if not answer_is_yes:
                            self.status_str.set("Search cancelled.")
                            self.parent.update()
                            return
            else:
                companyIDs = None

            # see doc under https://linkedin-api.readthedocs.io/en/latest/api.html
            # todo: don't hard code network depth
            search_result = api.search_people(keywords=keywords, network_depths=network_depths, current_company=companyIDs, regions=locations,
                                            keyword_title=keywords_title, include_private_profiles=False)
            result_size = len(search_result)
            print("Found " + str(result_size) + " results! Searching contact details... This can take a while...")
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
                profile = api.get_profile(urn_id=people['urn_id'])
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
                        skills_raw = api.get_profile_skills(urn_id=people['urn_id'])
                        skills = [dic['name'] for dic in skills_raw]
                        profile_dict.update({'Skills': [skills]})

                    self.search_results_df = pd.concat([self.search_results_df,
                                                pd.DataFrame(profile_dict)])

                    self.table.updateModel(TableModel(self.search_results_df))
                    self.table.redraw()
                    self.status_str.set("Scanned " + str(row) + " out of " + str(result_size) + " profiles")
                    self.parent.update()

                    row += 1

            print("Done")
            self.export_to_file_btn.configure(state="normal")
            self.status_str.set("Done")
            self.parent.update()
        except Exception as e:
            utils.show_exception(e)
            self.status_str.set("Something went wrong! Check console output for more details.")
            self.parent.update()


    def create_start_search_thread(self):
        global search_thread
        if 'search_thread' in globals() and search_thread.is_alive():
            messagebox.showinfo("Search in progress", "Another search is still running.\nWait until it finishes or restart the program.")
            return
        search_thread = threading.Thread(target=self.start_search)
        search_thread.daemon = True
        search_thread.start()


    def prepare_dataframe_and_save_to_xsl(self):
        self.status_str.set("Exporting to File...")
        export_file = utils.save_dataframe_to_file(self.search_results_df)

        if export_file is not None:
            self.status_str.set("Table saved under " + export_file)
        else:
            self.status_str.set("Table could not be saved!")


if __name__ == "__main__":
    root = ttk.Window()
    root.title("SWFEAT vs Epics")
    root.geometry("1280x720")

    # Login frame
    login_frame = ttk.Frame(root)
    login_frame.pack(padx=10, pady=5, expand=False, fill="x")
    label_usr = ttk.Label(login_frame, text="User")
    label_usr.pack(side='left', expand=False)
    entry_usr = ttk.Entry(login_frame)
    entry_usr.pack(side='left', expand=True, fill="x")
    label_pwd = ttk.Label(login_frame, text="Pwd")
    label_pwd.pack(side='left', expand=False)
    entry_pwd = ttk.Entry(login_frame, show="*")
    entry_pwd.pack(side='left', expand=True, fill="x")

    separator = ttk.Separator(root, orient='horizontal')
    separator.pack(side='top', pady=10, fill='x')

    people_search = PeopleSearch(root, entry_usr, entry_pwd)
    root.mainloop()
