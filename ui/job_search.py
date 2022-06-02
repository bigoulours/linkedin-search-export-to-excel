from textwrap import fill
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.tooltip import ToolTip
try:
    from . import utils
    from .customWidgets import SearchFrame, PlaceholderEntry
except:
    import utils
    from customWidgets import SearchFrame, PlaceholderEntry
from tkinter import messagebox
import threading
import pandas as pd
from pandastable import Table, TableModel


class JobSearch:
    def __init__(self, tk_parent, linkedin_conn):

        self.parent = tk_parent
        self.linkedin_conn = linkedin_conn

        self.search_results_df = pd.DataFrame()
        self.search_thread = None
        self.quick_search = True

        # Paned Window
        self.search_paned_window = ttk.PanedWindow(tk_parent, orient='horizontal')
        self.search_paned_window.pack(side='top', fill="both", expand=True, padx=10)

        ## Search fields Canvas/ScrolledFrame
        search_fields_canvas = ttk.Canvas(self.search_paned_window)

        search_fields_frame = ScrolledFrame(search_fields_canvas)
        search_fields_frame.pack(side='top', fill='both', expand=True, padx=5)
        search_fields_frame.hide_scrollbars()

        ### KW-Frame
        kw_frame = ttk.Frame(search_fields_frame)
        kw_frame.pack(pady=5, side='top', fill="x")
        ttk.Label(kw_frame, text="Keywords").pack(side='left')
        self.entry_keywords = ttk.Entry(kw_frame)
        self.entry_keywords.pack(side='left', padx=10, fill='x', expand=True)

        ttk.Separator(search_fields_frame, orient='horizontal').pack(side='top', fill='x', pady=5)
        
        ### Radio Frame
        radio_frame = ttk.Frame(search_fields_frame)
        radio_frame.pack(side='top', fill="x", pady=5, expand=True)
        radio_frame.grid_columnconfigure(0,weight=0)
        radio_frame.grid_columnconfigure(1,weight=0)
        radio_frame.grid_columnconfigure(2,weight=1)

        #### Sort by
        ttk.Label(radio_frame, text="Sort by").grid(row=0, column=0, sticky='nwse')

        self.sort_by = ttk.StringVar()
        ttk.Radiobutton(radio_frame, text='Most recent', variable=self.sort_by, value="RECENT").grid(row=0, column=1, padx=10, sticky='nwse')
        ttk.Radiobutton(radio_frame, text='Most relevant', variable=self.sort_by, value="RELEVANT").grid(row=0, column=2, padx=10, sticky='nwse')

        ttk.Separator(radio_frame, orient='horizontal').grid(row=1, columnspan=3, pady=5, sticky='nwse')

        #### Date Posted
        ttk.Label(radio_frame, text="Date Posted").grid(row=2, column=0, sticky='nwse', pady=5)

        self.date_posted = ttk.StringVar()
        ttk.Radiobutton(radio_frame, text='Past 24h', variable=self.date_posted,
                        value="DAY").grid(row=3, column=1, padx=10, pady=4, sticky='nwse')
        ttk.Radiobutton(radio_frame, text='Past Week', variable=self.date_posted,
                        value="WEEK").grid(row=3, column=2, padx=10, pady=4, sticky='nwse')
        ttk.Radiobutton(radio_frame, text='Past Month', variable=self.date_posted,
                        value="MONTH").grid(row=4, column=1, padx=10, pady=4, sticky='nwse')
        ttk.Radiobutton(radio_frame, text='Any Time', variable=self.date_posted,
                        value="ANY").grid(row=4, column=2, padx=10, pady=4, sticky='nwse')

        ttk.Separator(search_fields_frame, orient='horizontal').pack(side='top', fill='x', pady=5)

        ### Experience
        exp_frame = ttk.Frame(search_fields_frame)
        exp_frame.pack(side='top', fill="x")
        exp_frame.grid_columnconfigure(0,weight=0)
        exp_frame.grid_columnconfigure(1,weight=0)
        exp_frame.grid_columnconfigure(2,weight=1)
        ttk.Label(exp_frame, text="Experience").grid(row=0, column=0, pady=4, sticky='nwse')

        intern_lvl_bool = ttk.BooleanVar()
        entry_lvl_bool = ttk.BooleanVar()
        associate_bool = ttk.BooleanVar()
        mid_senior_bool = ttk.BooleanVar()
        director_bool = ttk.BooleanVar()
        executive_bool = ttk.BooleanVar()

        self.exp_dict_list = [
                {'bool_val': intern_lvl_bool, 'name': '1'},
                {'bool_val': entry_lvl_bool, 'name': '2'},
                {'bool_val': associate_bool, 'name': '3'},
                {'bool_val': mid_senior_bool, 'name': '4'},
                {'bool_val': director_bool, 'name': '5'},
                {'bool_val': executive_bool, 'name': '6'},
        ]

        ttk.Checkbutton(exp_frame, text="Internship",
                variable=intern_lvl_bool).grid(row=1, column=0, padx=5, pady=4, sticky='nwse')
        ttk.Checkbutton(exp_frame, text="Entry level",
                variable=entry_lvl_bool).grid(row=1, column=1, padx=5, pady=4, sticky='nwse')
        ttk.Checkbutton(exp_frame, text="Associate",
                variable=associate_bool).grid(row=1, column=2, padx=5, pady=4, sticky='nwse')
        ttk.Checkbutton(exp_frame, text="Mid-Senior level",
                variable=mid_senior_bool).grid(row=2, column=0, padx=5, pady=4, sticky='nwse')
        ttk.Checkbutton(exp_frame, text="Director",
                variable=director_bool).grid(row=2, column=1, padx=5, pady=4, sticky='nwse')
        ttk.Checkbutton(exp_frame, text="Executive",
                variable=executive_bool).grid(row=2, column=2, padx=5, pady=4, sticky='nwse')

        ttk.Separator(search_fields_frame, orient='horizontal').pack(side='top', fill='x', pady=5)

        ### Company frame
        self.comp_frame = SearchFrame(search_fields_frame, title='Company',
                    fetch_fct=lambda x: utils.extract_urn_dict_from_query_results(linkedin_conn[0].get_company_urn_ids, x))
        self.comp_frame.pack(side='top', fill="x")

        ttk.Separator(search_fields_frame, orient='horizontal').pack(side='top', fill='x', pady=5)

        ### Job Type
        job_type_frame = ttk.Frame(search_fields_frame)
        job_type_frame.pack(side='top', fill="x")
        job_type_frame.grid_columnconfigure(0,weight=0)
        job_type_frame.grid_columnconfigure(1,weight=0)
        job_type_frame.grid_columnconfigure(2,weight=1)
        ttk.Label(job_type_frame, text="Job Type").grid(row=0, column=0, pady=4, sticky='nwse')

        full_time_bool = ttk.BooleanVar()
        part_time_bool = ttk.BooleanVar()
        temporary_bool = ttk.BooleanVar()
        contract_bool = ttk.BooleanVar()
        volunteer_bool = ttk.BooleanVar()
        intern_type_bool = ttk.BooleanVar()
        other_type_bool = ttk.BooleanVar()

        self.job_type_dict_list = [
                {'bool_val': full_time_bool, 'name': 'F'},
                {'bool_val': part_time_bool, 'name': 'P'},
                {'bool_val': temporary_bool, 'name': 'T'},
                {'bool_val': contract_bool, 'name': 'C'},
                {'bool_val': volunteer_bool, 'name': 'V'},
                {'bool_val': intern_type_bool, 'name': 'I'},
                {'bool_val': other_type_bool, 'name': 'O'},
        ]

        ttk.Checkbutton(job_type_frame, text="Other",
                variable=other_type_bool).grid(row=0, column=2, padx=10, pady=4, sticky='nwse')
        ttk.Checkbutton(job_type_frame, text="Full-time",
                variable=full_time_bool).grid(row=1, column=0, padx=10, pady=4, sticky='nwse')
        ttk.Checkbutton(job_type_frame, text="Part-time",
                variable=part_time_bool).grid(row=1, column=1, padx=10, pady=4, sticky='nwse')
        ttk.Checkbutton(job_type_frame, text="Temporary",
                variable=temporary_bool).grid(row=1, column=2, padx=10, pady=4, sticky='nwse')
        ttk.Checkbutton(job_type_frame, text="Contract",
                variable=contract_bool).grid(row=2, column=0, padx=10, pady=4, sticky='nwse')
        ttk.Checkbutton(job_type_frame, text="Volunteer",
                variable=volunteer_bool).grid(row=2, column=1, padx=10, pady=4, sticky='nwse')
        ttk.Checkbutton(job_type_frame, text="Internship",
                variable=intern_type_bool).grid(row=2, column=2, padx=10, pady=4, sticky='nwse')
        
        ttk.Separator(search_fields_frame, orient='horizontal').pack(side='top', fill='x', pady=5)

        ### Location Frame
        self.loc_frame = SearchFrame(search_fields_frame, title='Location',
                    fetch_fct=lambda x: utils.extract_urn_dict_from_query_results(linkedin_conn[0].get_geo_urn_ids, x))
        self.loc_frame.pack(side='top', fill="x")

        ttk.Separator(search_fields_frame, orient='horizontal').pack(side='top', fill='x', pady=5)

        ### Industry frame
        self.industry_frame = SearchFrame(search_fields_frame, title='Industry',
                    fetch_fct=lambda x: utils.extract_urn_dict_from_query_results(linkedin_conn[0].get_industry_urn_ids, x))
        self.industry_frame.pack(side='top', fill="x", pady=5)

        self.search_paned_window.add(search_fields_canvas)

        ## Table frame
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


        btn_sub_frame = ttk.Frame(btn_frame)
        btn_sub_frame.pack(side="left", fill="none", expand=True)

        start_search_btn = ttk.Button(btn_sub_frame, text="Deep Search", bootstyle='danger')
        start_search_btn.pack(side='left', padx=10)
        start_search_btn['command'] = self.start_deep_search
        ToolTip(start_search_btn, "Each search result will be fetched for additional information. \
            \nDepending on the number of results and search frequency, this can trigger the linkedin limit \
after which you'll only be able to get 3 results per search until the end of the month.")

        self.get_contact_info = ttk.BooleanVar()
        contact_info_chk_btn = ttk.Checkbutton(btn_sub_frame, text="Fetch contact info",
                                    variable=self.get_contact_info, bootstyle="danger")
        contact_info_chk_btn.pack(side='left', padx=10)
        ToolTip(contact_info_chk_btn, text=f"Fetch contact info by running one additional request per result.")

        self.export_to_file_btn = ttk.Button(btn_frame, text="Export to File", state="disabled")
        self.export_to_file_btn.pack(side='left', padx=10)
        self.export_to_file_btn['command'] = self.prepare_dataframe_and_save_to_xsl

        # Status frame
        self.status_frame = ttk.Frame(tk_parent)
        self.status_frame.pack(padx=10, pady=2, side='bottom', expand=False, fill="x")
        self.status_str = ttk.StringVar(value="")
        ttk.Label(self.status_frame, textvariable=self.status_str).pack(side='left', expand=False)

        ttk.Separator(tk_parent, orient='horizontal').pack(side='bottom', fill='x')

    def run_search(self):
        self.status_str.set("Running search...")
        self.parent.update()
        dbg = [x.lbl_name.get() for x in self.loc_frame.get_current_selection()]
        try:
            # see doc under https://linkedin-api.readthedocs.io/en/latest/api.html
            search_result = self.linkedin_conn[0].search_jobs(
                    keywords=self.entry_keywords.get(),
                    companies=[x.value for x in self.comp_frame.get_current_selection()],
                    experience=[x['name'] for x in self.exp_dict_list if x['bool_val'].get()],
                    job_type=[x['name'] for x in self.job_type_dict_list if x['bool_val'].get()],
                    industries=[x.value for x in self.industry_frame.get_current_selection()],
                    location_name=[x.lbl_name.get() for x in self.loc_frame.get_current_selection()],
                )

            if self.quick_search:
                self.search_results_df = pd.DataFrame(search_result)
                self.table.updateModel(TableModel(self.search_results_df))
                self.table.redraw()

            else:
                result_size = len(search_result)
                self.status_str.set("Found " + str(result_size) + " results! Searching contact details... This can take a while...")
                self.parent.update()

                if result_size > 999:
                    answer_is_yes = messagebox.askyesno("Too many results!",
                            "This search yields more than 1000 results (upper limit for this app).\nProceed anyway?",
                            icon="warning")
                    if not answer_is_yes:
                        self.status_str.set("Search cancelled.")
                        self.parent.update()
                        return

                row = 1

                for job in search_result:
                    profile = self.linkedin_conn[0].get_profile(urn_id=job['urn_id'])
                    if profile != {}:
                        if 'geoLocationName' in profile.keys():
                            geolocation = profile['geoLocationName']
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
                            skills_raw = self.linkedin_conn[0].get_profile_skills(urn_id=job['urn_id'])
                            skills = [dic['name'] for dic in skills_raw]
                            profile_dict.update({'Skills': [skills]})

                        if self.get_contact_info.get():
                            contact_info = self.linkedin_conn[0].get_profile_contact_info(urn_id=job['urn_id'])
                            contact_info = {k: [v] for k,v in contact_info.items()}
                            profile_dict.update(contact_info)
                        
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
            messagebox.showinfo("Error", "First log into Linkedin!", icon="error")
            return
        if self.search_thread and self.search_thread.is_alive():
            messagebox.showinfo("Search in progress",
                        "Another search is still running.\nWait until it finishes or restart the program.",
                        icon="warning")
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
    root.title("LinkedIn Job Search")
    root.geometry("1280x720")

    # Login frame
    login_frame = ttk.Frame(root)
    login_frame.pack(pady=10, expand=False, fill="x")

    ttk.Label(login_frame, text="User").pack(side='left', expand=False, padx=5)
    entry_usr = ttk.Entry(login_frame)
    entry_usr.pack(side='left', expand=True, fill="x", padx=5)

    ttk.Label(login_frame, text="Pwd").pack(side='left', expand=False, padx=5)
    entry_pwd = ttk.Entry(login_frame, show="*")
    entry_pwd.pack(side='left', expand=True, fill="x", padx=5)

    connect_btn = ttk.Button(login_frame, text="Connect")
    connect_btn.pack(side='left', padx=5)

    linkedin_conn = [None]

    def connect_linkedin():
        # Authenticate using any Linkedin account credentials
        try:
            linkedin_conn[0] = Linkedin(entry_usr.get(), entry_pwd.get())
            messagebox.showinfo("Success", "Successfully logged into LinkedIn.", icon="info")

        except Exception as e:
            messagebox.showinfo("Error",
                    "Login failed!\nCheck username and password.\n2FA must be disabled in LinkedIn settings.",
                    icon="error")
            return

    connect_btn['command'] = connect_linkedin

    people_search = JobSearch(root, linkedin_conn)
    root.mainloop()
