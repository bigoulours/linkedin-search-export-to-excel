import json
from textwrap import fill
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.tooltip import ToolTip
from tkinter import filedialog
try:
    from . import utils
    from .customWidgets import *
except:
    import utils
    from customWidgets import *
from tkinter import messagebox
import threading
import pandas as pd
from pandastable import Table, TableModel
from datetime import datetime


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

        ### Load/Save search
        load_save_btn_frame = ttk.Frame(search_fields_frame)
        load_save_btn_frame.pack(pady=5, side='top', fill="x")

        load_search_btn = ttk.Button(load_save_btn_frame, text="Load param.")
        load_search_btn.pack(side='left')
        load_search_btn['command'] = self.load_search_config

        save_search_btn = ttk.Button(load_save_btn_frame, text="Save param.")
        save_search_btn.pack(side='right', padx=10)
        save_search_btn['command'] = self.save_search_config

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

        self.sort_by = ttk.StringVar(value="R")
        ttk.Radiobutton(radio_frame, text='Most recent', variable=self.sort_by, value="DD").grid(row=0, column=1, padx=10, sticky='nwse')
        ttk.Radiobutton(radio_frame, text='Most relevant', variable=self.sort_by, value="R").grid(row=0, column=2, padx=10, sticky='nwse')

        ttk.Separator(radio_frame, orient='horizontal').grid(row=1, columnspan=3, pady=5, sticky='nwse')

        #### Date Posted
        ttk.Label(radio_frame, text="Date Posted").grid(row=2, column=0, sticky='nwse', pady=5)

        self.date_posted = ttk.IntVar(value=365) # Days since job was posted
        ttk.Radiobutton(radio_frame, text='Past 24h', variable=self.date_posted,
                        value=1).grid(row=3, column=1, padx=10, pady=4, sticky='nwse')
        ttk.Radiobutton(radio_frame, text='Past Week', variable=self.date_posted,
                        value=7).grid(row=3, column=2, padx=10, pady=4, sticky='nwse')
        ttk.Radiobutton(radio_frame, text='Past Month', variable=self.date_posted,
                        value=30).grid(row=4, column=1, padx=10, pady=4, sticky='nwse')
        ttk.Radiobutton(radio_frame, text='Any Time', variable=self.date_posted,
                        value=365).grid(row=4, column=2, padx=10, pady=4, sticky='nwse')

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

        ### Location Fallback
        self.loc_fallback_frame = SearchFrame(search_fields_frame, title='General Location', single_choice=True,
                    fetch_fct=lambda x: utils.extract_urn_dict_from_query_results(linkedin_conn[0].get_geo_urn_ids, x),
                    tooltip="Restrict the geographical area of the results. In the browser, your location will be recognized automatically and shown at the top of the search page close to the keyword field.")
        self.loc_fallback_frame.pack(side='top', fill="x")

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

        # self.get_contact_info = ttk.BooleanVar()
        # contact_info_chk_btn = ttk.Checkbutton(btn_sub_frame, text="Fetch contact info",
        #                             variable=self.get_contact_info, bootstyle="danger")
        # contact_info_chk_btn.pack(side='left', padx=10)
        # ToolTip(contact_info_chk_btn, text=f"Fetch contact info by running one additional request per result.")

        self.export_to_file_btn = ttk.Button(btn_frame, text="Export to File", state="disabled")
        self.export_to_file_btn.pack(side='left', padx=10)
        self.export_to_file_btn['command'] = self.prepare_dataframe_and_save_to_xsl

        # Status frame
        self.status_frame = ttk.Frame(tk_parent)
        self.status_frame.pack(padx=10, pady=2, side='bottom', expand=False, fill="x")
        self.status_str = ttk.StringVar(value="")
        ttk.Label(self.status_frame, textvariable=self.status_str).pack(side='left', expand=False)

        ttk.Separator(tk_parent, orient='horizontal').pack(side='bottom', fill='x')

    def save_search_config(self):
        chosen_file = filedialog.asksaveasfile(mode='w', filetypes=[("JSON", ".json")], defaultextension=".json")
        if chosen_file is None:
            return
        config_dict = {
            'job_search' : {
                'keywords': self.entry_keywords.get(),
                'sort_by' : self.sort_by.get(),
                'listed_at' : 24 * 3600 * self.date_posted.get(),
                'experience' : [x['name'] for x in self.exp_dict_list if x['bool_val'].get()],
                'companies' : [[x.lbl_name.get(), x.value] for x in self.comp_frame.get_current_selection()],
                'job_type' : [x['name'] for x in self.job_type_dict_list if x['bool_val'].get()],
                'location' : [[x.lbl_name.get(), x.value] for x in self.loc_frame.get_current_selection()],
                'industries' : [[x.lbl_name.get(), x.value] for x in self.industry_frame.get_current_selection()]
            }
        }
        with open(chosen_file.name, 'w') as f:
            json.dump(config_dict, f, indent=4)
        
        self.status_str.set(f"Search config successfully saved at {chosen_file.name}!")

    def load_search_config(self):
        chosen_file = filedialog.askopenfile(mode='r', filetypes=[("JSON", ".json")], defaultextension=".json")
        if chosen_file is None:
            return
        try:
            with open(chosen_file.name, 'r') as f:
                config_dict = json.load(f)
            config = config_dict['job_search']
        except:
            self.status_str.set(f"Please select a valid job search configuration!")

        self.entry_keywords.delete(0,'end')
        self.entry_keywords.insert(0, config['keywords'])
        self.sort_by.set(config['sort_by'])
        self.date_posted.set(config['listed_at']//(24 * 3600))

        utils.set_bools_from_list(self.exp_dict_list, config['experience'])
        self.comp_frame.load_name_val_from_list(config['companies'])
        utils.set_bools_from_list(self.job_type_dict_list, config['job_type'])
        self.loc_frame.load_name_val_from_list(config['location'])
        self.industry_frame.load_name_val_from_list(config['industries'])

        self.status_str.set(f"Config loaded succesfully!")        


    def run_search(self):
        self.search_results_df = pd.DataFrame()
        self.table.updateModel(TableModel(self.search_results_df))
        self.table.redraw()
        self.status_str.set("Running search...")
        self.parent.update()
        loc_fallback = None
        if self.loc_fallback_frame.get_current_selection():
            loc_fallback = self.loc_fallback_frame.get_current_selection()[0].lbl_name.get()
        
        try:
            # see doc under https://linkedin-api.readthedocs.io/en/latest/api.html
            search_result = self.linkedin_conn[0].search_jobs(
                    keywords=self.entry_keywords.get(),
                    sort_by=self.sort_by.get(),
                    listed_at=24 * 3600 * self.date_posted.get(),
                    companies=[x.value for x in self.comp_frame.get_current_selection()],
                    experience=[x['name'] for x in self.exp_dict_list if x['bool_val'].get()],
                    job_type=[x['name'] for x in self.job_type_dict_list if x['bool_val'].get()],
                    location_name = loc_fallback,
                    geo_urn_ids=[x.value for x in self.loc_frame.get_current_selection()],
                    industries=[x.value for x in self.industry_frame.get_current_selection()],
                )

            if self.quick_search:
                self.search_results_df = pd.DataFrame(search_result)
                try:
                    self.search_results_df.drop(['dashEntityUrn', '$recipeTypes', '$type'],
                                 axis=1, inplace=True)
                    self.search_results_df['companyDetails'] = self.search_results_df['companyDetails'].apply(
                            lambda x: x.get('company', '').rsplit(':', 1)[-1]
                    )
                    self.search_results_df.rename(columns={'companyDetails': 'companyUrn'}, inplace=True)
                    self.search_results_df['entityUrn'] = self.search_results_df['entityUrn'].str.rsplit(':', 1, expand=True)[1]
                    self.search_results_df['listedAt'] = self.search_results_df['listedAt'].apply(
                                                            lambda x : datetime.fromtimestamp(x/1000).date()
                    )
                except Exception as e:
                    print(repr(e))
                self.table.updateModel(TableModel(self.search_results_df))
                self.table.redraw()

            else:
                result_size = len(search_result)
                self.status_str.set("Found " + str(result_size) + " results! Searching jobs details... This can take a while...")
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
                    job_obj = self.linkedin_conn[0].get_job(job['dashEntityUrn'].rsplit(':',1)[1])
                    if job_obj != {}:

                        job_dict = {
                            'Title': job_obj['title'],
                            'Company': job_obj['companyDetails']
                                             .get('com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany', {},
                                            ).get('companyResolutionResult', {}
                                            ).get('name', ''),
                            'Location': job_obj['formattedLocation'],
                            'Description': job_obj.get('description', {}).get('text', ''),
                            #'Remote': job_obj['workRemoteAllowed'],
                            'Work Place': job_obj.get('workplaceTypesResolutionResults', {})
                                            .get('urn:li:fs_workplaceType:1', {})
                                            .get('localizedName', ''),
                            'Posted On': datetime.fromtimestamp(job_obj['listedAt']/1000).date(),
                            'LinkedIn Link': f"https://www.linkedin.com/jobs/view/{job_obj['jobPostingId']}",
                            'Direct Link': job_obj.get('applyMethod',{})
                                                 .get('com.linkedin.voyager.jobs.OffsiteApply', {}
                                                ).get('companyApplyUrl', '').split('?', 1)[0]
                        }

                        # if self.get_contact_info.get():
                        #     contact_info = self.linkedin_conn[0].get_profile_contact_info(urn_id=job['urn_id'])
                        #     contact_info = {k: [v] for k,v in contact_info.items()}
                        #     job_dict.update(contact_info)
                        
                        self.search_results_df = pd.concat([self.search_results_df,
                                                pd.DataFrame([job_dict.values()], columns=job_dict.keys())])

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
