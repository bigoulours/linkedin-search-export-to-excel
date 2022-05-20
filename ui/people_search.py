import ttkbootstrap as ttk
from linkedin_api import Linkedin
try:
    from .autocompleteEntry import AutocompleteEntry
    from . import utils
except:
    from autocompleteEntry import AutocompleteEntry
    import utils
from tkinter import Scrollbar
from tkinter import messagebox
import os
import sys
import threading
import pandas as pd
import pandastable

profile_list_w_skills = []

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

        # Search filters 1
        search_frame1 = ttk.Frame(tk_parent)
        search_frame1.pack(padx=10, pady=5, side='top', fill="x")
        label_keywords = ttk.Label(search_frame1, text="Keywords")
        label_keywords.pack(side='left', expand=False)
        entry_keywords = ttk.Entry(search_frame1)
        entry_keywords.pack(side='left', expand=True, fill="x")

        label_locations = ttk.Label(search_frame1, text="Locations")
        label_locations.pack(side='left', expand=False)
        entry_locations = AutocompleteEntry(geo_urn_ids.keys(), search_frame1, width=50)
        entry_locations.pack(side='left', expand=False)

        # Search filters 2
        search_frame2 = ttk.Frame(tk_parent)
        search_frame2.pack(padx=10, pady=5, side='top', fill="x")
        label_keywords_title = ttk.Label(search_frame2, text="Keywords Title")
        label_keywords_title.pack(side='left', expand=False)
        entry_keywords_title = ttk.Entry(search_frame2)
        entry_keywords_title.pack(side='left', expand=True, fill="x")

        label_companies = ttk.Label(search_frame2, text="Company public ID(s)")
        label_companies.pack(side='left', expand=False)
        entry_companies = AutocompleteEntry(company_public_ids, search_frame2)
        entry_companies.pack(side='left', expand=True, fill="x")

        # Buttons frame
        btn_frame = ttk.Frame(tk_parent)
        btn_frame.pack(padx=10, pady=10, side='top', fill="x")
        start_search_btn = ttk.Button(btn_frame, text="Search Now!")
        start_search_btn.pack(side='left')
        start_search_btn['command'] = lambda: self.create_start_search_thread(entry_keywords.get(), entry_companies.get(), entry_keywords_title.get(),
                                                        [geo_urn_ids[x] for x in entry_locations.get().split() if x in geo_urn_ids.keys()])
        self.export_to_file_btn = ttk.Button(btn_frame, text="Export to File", state="disabled")
        self.export_to_file_btn.pack(side='right')
        self.export_to_file_btn['command'] = self.prepare_dataframe_and_save_to_xsl

        # Table frame and canvas
        table_main_frame = ttk.Frame(tk_parent)
        table_main_frame.pack(padx=10, pady=10, side='top', fill="both", expand=True)

        table_canvas = ttk.Canvas(table_main_frame)
        self.table_frame = ttk.Frame(table_canvas)
        scrollbar = Scrollbar(table_main_frame, orient="vertical", command=table_canvas.yview)
        table_canvas.configure(yscrollcommand=scrollbar.set)

        self.table_frame.bind("<Configure>", lambda e: table_canvas.configure(scrollregion=table_canvas.bbox("all")))

        table_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        table_canvas.create_window((0, 0), window=self.table_frame, anchor='nw')

        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(1, weight=1)
        self.table_frame.grid_columnconfigure(2, weight=1)
        self.table_frame.grid_columnconfigure(3, weight=1)
        self.table_frame.grid_columnconfigure(4, weight=1)

        # Table headers
        table_header_company=ttk.Label(self.table_frame, relief='groove', text="Company", font="Helvetica 9 bold")
        table_header_company.grid(row=0, column=0, sticky='ew')
        table_header_location=ttk.Label(self.table_frame, relief='groove', text="Location", font="Helvetica 9 bold")
        table_header_location.grid(row=0, column=1, sticky='ew')
        table_header_last_name=ttk.Label(self.table_frame, relief='groove', text="Last Name", font="Helvetica 9 bold")
        table_header_last_name.grid(row=0, column=2, sticky='ew')
        table_header_first_name=ttk.Label(self.table_frame, relief='groove', text="First Name", font="Helvetica 9 bold")
        table_header_first_name.grid(row=0, column=3, sticky='ew')
        table_header_first_name=ttk.Label(self.table_frame, relief='groove', text="Headline", font="Helvetica 9 bold")
        table_header_first_name.grid(row=0, column=4, sticky='ew')

        # Status frame
        self.status_frame = ttk.Frame(tk_parent)
        self.status_frame.pack(padx=10, pady=2, side='bottom', expand=False, fill="x")
        self.status_str = ttk.StringVar(value="")
        self.label_status = ttk.Label(self.status_frame, textvariable=self.status_str)
        self.label_status.pack(side='left', expand=False)

        separator = ttk.Separator(tk_parent, orient='horizontal')
        separator.pack(side='bottom', fill='x')

    def start_search(self, keywords, company_names, keywords_title, locations):
        try:
            nb_columns = self.table_frame.grid_size()[0]
            # removing all cells from table (except headers)
            for cell in self.table_frame.grid_slaves()[:-nb_columns]:
                cell.grid_forget()

            # Authenticate using any Linkedin account credentials
            try:
                api = Linkedin(self.entry_usr.get(), self.entry_pwd.get())
                self.status_str.set("Login successful!")
                self.parent.update()
                profile_list_w_skills.clear()
                self.export_to_file_btn.configure(state="disabled")
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print("Error: " + repr(e) + " in " + str(fname) + " line " + str(exc_tb.tb_lineno) + "\n")
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
            search_result = api.search_people(keywords=keywords, current_company=companyIDs, regions=locations,
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
                    skills_raw = api.get_profile_skills(urn_id=people['urn_id'])
                    skills = []
                    for dict in skills_raw:
                        skills.append(dict['name'])
                    if 'geoLocationName' in profile.keys():
                        geolocation = profile['geoLocationName']
                    else:
                        geolocation = company['confirmedLocations'][0]['city']

                    ttk.Label(self.table_frame, text=profile['experience'][0]['companyName'], bg="white", relief='groove', borderwidth=1).grid(row=row, column=0, sticky='ew')
                    ttk.Label(self.table_frame, text=geolocation, bg="white", relief='groove', borderwidth=1).grid(row=row, column=1, sticky='ew')
                    ttk.Label(self.table_frame, text=profile['lastName'], bg="white", relief='groove', borderwidth=1).grid(row=row, column=2, sticky='ew')
                    ttk.Label(self.table_frame, text=profile['firstName'], bg="white", relief='groove', borderwidth=1).grid(row=row, column=3, sticky='ew')
                    ttk.Label(self.table_frame, text=profile['headline'], bg="white", relief='groove', borderwidth=1).grid(row=row, column=4, sticky='ew')
                    self.status_str.set("Scanned " + str(row) + " out of " + str(result_size) + " profiles")
                    self.parent.update()
                    row += 1
                    profile_list_w_skills.append((profile, skills))
            print("Done")
            self.export_to_file_btn.configure(state="normal")
            self.status_str.set("Done")
            self.parent.update()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: " + repr(e) + " in " + str(fname) + " line " + str(exc_tb.tb_lineno) + "\n")
            self.status_str.set("ASomething went wrong! Check console output for more details.")
            self.parent.update()


    def create_start_search_thread(self, keywords, company_names, keywords_title, locations):
        global search_thread
        if 'search_thread' in globals() and search_thread.is_alive():
            messagebox.showinfo("Search in progress", "Another search is still running.\nWait until it finishes or restart the program.")
            return
        search_thread = threading.Thread(target=self.start_search, args=(keywords, company_names, keywords_title, locations))
        search_thread.daemon = True
        search_thread.start()


    def prepare_dataframe_and_save_to_xsl(self):
        self.status_str.set("Exporting to File...")
        companies = []
        locations = []
        last_names = []
        first_names = []
        headlines = []
        titles = []
        linkedin_pages = []
        skills_list = []
        for (profile, skills) in profile_list_w_skills:
            if 'geoLocationName' in profile.keys():
                geolocation = profile['geoLocationName']
            else:
                geolocation = ""
            companies.append(profile['experience'][0]['companyName'])
            locations.append(geolocation)
            last_names.append(profile['lastName'])
            first_names.append(profile['firstName'])
            headlines.append(profile['headline'])
            titles.append(profile['experience'][0]['title'])
            linkedin_pages.append('https://www.linkedin.com/in/' + profile['profile_id'])
            skills_list.append(', '.join(skills))

        # create dataframe
        data_frame_for_export = pd.DataFrame({'Company': companies, 'Location': locations, 'Last Name': last_names,
                                            'First Name': first_names, 'Headline': headlines, 'Title': titles,
                                            'LinkedIn Page': linkedin_pages, 'Skills': skills_list})

        export_file = utils.save_dataframe_to_file(data_frame_for_export)

        if export_file is not None:
            self.status_str.set("Table saved under " + export_file)
        else:
            self.status_str.set("Table could not be saved!")


if __name__ == "__main__":
    root = ttk.Window()
    root.title("SWFEAT vs Epics")
    root.geometry("1280x720")
    root.resizable(width=True, height=True)

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
