from linkedin_api import Linkedin
from tkinter import *
from tkinter import messagebox, ttk
import os
import threading
from lib.autocompleteEntry import AutocompleteEntry
from lib.exportToExcel import *


geo_urn_ids = {'Bavaria': '100545973', 'Baden-Württemberg': '100165017',
               'North Rhine-Westphalia': '103480659',
               'France': '105015875', 'Germany': '101282230',
               'Berlin': '103035651', 'Berlin Region': '90009712',
               'Bremen': '104836009', 'Bremen Region': '90009717',
               'Düsseldorf': '104008204', 'Düsseldorf Region': '90009721',
               'Frankfurt': '106150090', 'Frankfurt Region': '90009714',
               'Hamburg': '101949806', 'Hamburg Region': '90009725',
               'Munich': '100477049', 'Munich Region': '90009735',
               'Stuttgart': '102473731', 'Stuttgart Region': '90009750'}

company_public_ids_filepath = 'resources/Company_public_IDs.txt'

top = Tk()
top.title("Linkedin Search")
window_width = 1200
window_height = 675
top.geometry(str(window_width) + "x" + str(window_height))
try:
    top.iconbitmap("images/linkedin.ico")
except:
    print("LinkedIn icon not found. Using default.")
top.resizable(width=False, height=True)
status_str = StringVar(value="")
profile_list_w_skills = []
this_file_name = os.path.splitext(os.path.basename(__file__))[0]


def start_search(username, password, table_object, keywords, company_names, keywords_title, locations):
    nb_columns = table_object.grid_size()[0]
    # removing all cells from table (except headers)
    for cell in table_object.grid_slaves()[:-nb_columns]:
        cell.grid_forget()

    # Authenticate using any Linkedin account credentials
    try:
        api = Linkedin(username, password)
        with open(this_file_name + '_login', 'w') as f:
            f.write(username)
        status_str.set("Login successful!")
        top.update()
        profile_list_w_skills.clear()
        export_to_xsl_btn.configure(state="disabled")
    except Exception as e:
        print("Error: " + repr(e))
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
                    status_str.set("Search cancelled.")
                    top.update()
                    return
    else:
        companyIDs = None

    # see doc under https://linkedin-api.readthedocs.io/en/latest/api.html
    search_result = api.search_people(keywords=keywords, current_company=companyIDs, regions=locations,
                                      keyword_title=keywords_title, include_private_profiles=False)
    result_size = len(search_result)
    print("Found " + str(result_size) + " results! Searching contact details... This can take a while...")
    status_str.set("Found " + str(result_size) + " results! Searching contact details... This can take a while...")
    top.update()

    if result_size > 999:
        answer_is_yes = messagebox.askyesno("Too many results!", "This search yields more than 1000 results (upper limit for this app).\nProceed anyway?")
        if not answer_is_yes:
            status_str.set("Search cancelled.")
            top.update()
            return

    row = 1
    try:
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

                Label(table_object, text=profile['experience'][0]['companyName'], bg="white", relief=GROOVE, borderwidth=1).grid(row=row, column=0, sticky=EW)
                Label(table_object, text=geolocation, bg="white", relief=GROOVE, borderwidth=1).grid(row=row, column=1, sticky=EW)
                Label(table_object, text=profile['lastName'], bg="white", relief=GROOVE, borderwidth=1).grid(row=row, column=2, sticky=EW)
                Label(table_object, text=profile['firstName'], bg="white", relief=GROOVE, borderwidth=1).grid(row=row, column=3, sticky=EW)
                Label(table_object, text=profile['headline'], bg="white", relief=GROOVE, borderwidth=1).grid(row=row, column=4, sticky=EW)
                status_str.set("Scanned " + str(row) + " out of " + str(result_size) + " profiles")
                top.update()
                row += 1
                profile_list_w_skills.append((profile, skills))
        print("Done")
        export_to_xsl_btn.configure(state="normal")
        status_str.set("Done")
        top.update()
    except Exception as e:
        status_str.set("An error occurred! See console output for more details.")
        top.update()
        print("Error: " + repr(e))


def create_start_search_thread(username, password, table_object, keywords, company_names, keywords_title, locations):
    global search_thread
    if 'search_thread' in globals() and search_thread.is_alive():
        messagebox.showinfo("Search in progress", "Another search is still running.\nWait until it finishes or restart the program.")
        return
    search_thread = threading.Thread(target=start_search, args=(username, password, table_object, keywords, company_names, keywords_title, locations))
    search_thread.daemon = True
    search_thread.start()


def prepare_dataframe_and_save_to_xsl(profile_skills_list):
    status_str.set("Exporting to Excel...")
    companies = []
    locations = []
    last_names = []
    first_names = []
    headlines = []
    titles = []
    linkedin_pages = []
    skills_list = []
    for (profile, skills) in profile_skills_list:
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

    export_file = save_to_xsl(data_frame_for_export)

    if export_file is not None:
        status_str.set("Excel file saved under " + export_file)
    else:
        status_str.set("Excel file could not be saved!")


# Login frame
login_frame = Frame(top)
login_frame.pack(padx=10, pady=5, expand=False, fill="x")
label_usr = Label(login_frame, text="User")
label_usr.pack(side=LEFT, expand=False)
entry_usr = Entry(login_frame, bd=5)
last_login = ''
if os.path.isfile(this_file_name + '_login'):
    with open(this_file_name + '_login') as f:
        last_login = f.readlines()
entry_usr.insert(0, last_login)
entry_usr.pack(side=LEFT, expand=True, fill="x")
label_pwd = Label(login_frame, text="Pwd")
label_pwd.pack(side=LEFT, expand=False)
entry_pwd = Entry(login_frame, show="*", bd=5)
entry_pwd.pack(side=LEFT, expand=True, fill="x")

separator = ttk.Separator(top, orient='horizontal')
separator.pack(side=TOP, pady=10, fill='x')

# Search filters 1
search_frame1 = Frame(top)
search_frame1.pack(padx=10, pady=5, side=TOP, fill="x")
label_keywords = Label(search_frame1, text="Keywords")
label_keywords.pack(side=LEFT, expand=False)
entry_keywords = Entry(search_frame1, bd=5)
entry_keywords.pack(side=LEFT, expand=True, fill="x")

label_locations = Label(search_frame1, text="Locations")
label_locations.pack(side=LEFT, expand=False)
entry_locations = AutocompleteEntry(geo_urn_ids.keys(), search_frame1, bd=5, text="Germany ", width=50)
entry_locations.pack(side=LEFT, expand=False)

# Search filters 2
search_frame2 = Frame(top)
search_frame2.pack(padx=10, pady=5, side=TOP, fill="x")
label_keywords_title = Label(search_frame2, text="Keywords Title")
label_keywords_title.pack(side=LEFT, expand=False)
entry_keywords_title = Entry(search_frame2, bd=5)
entry_keywords_title.pack(side=LEFT, expand=True, fill="x")

label_companies = Label(search_frame2, text="Company public ID(s)")
label_companies.pack(side=LEFT, expand=False)
company_public_ids = []
if os.path.isfile(company_public_ids_filepath):
    with open(company_public_ids_filepath, encoding='utf-8') as f:
        public_ids = f.readlines()
        for id in public_ids:
            company_public_ids.append(id)
entry_companies = AutocompleteEntry(company_public_ids, search_frame2, bd=5)
entry_companies.pack(side=LEFT, expand=True, fill="x")

# Buttons frame
btn_frame = Frame(top)
btn_frame.pack(padx=10, pady=10, side=TOP, fill="x")
start_search_btn = Button(btn_frame, text="Search Now!")
start_search_btn.pack(side=LEFT)
start_search_btn['command'] = lambda: create_start_search_thread(entry_usr.get(), entry_pwd.get(), table_frame,
                                                   entry_keywords.get(), entry_companies.get(), entry_keywords_title.get(),
                                                   [geo_urn_ids[x] for x in entry_locations.get().split() if x in geo_urn_ids.keys()])
export_to_xsl_btn = Button(btn_frame, text="Export to Excel", state="disabled")
export_to_xsl_btn.pack(side=RIGHT)
export_to_xsl_btn['command'] = lambda: prepare_dataframe_and_save_to_xsl(profile_list_w_skills)

# Table frame and canvas
table_main_frame = Frame(top)
table_main_frame.pack(padx=10, pady=10, side=TOP, fill="both", expand=True)

table_canvas = Canvas(table_main_frame)
table_frame = Frame(table_canvas)
scrollbar = Scrollbar(table_main_frame, orient="vertical", command=table_canvas.yview)
table_canvas.configure(yscrollcommand=scrollbar.set)

table_frame.bind("<Configure>", lambda e: table_canvas.configure(scrollregion=table_canvas.bbox("all")))

table_canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")
table_canvas.create_window((0, 0), window=table_frame, anchor='nw', width=window_width-40)

table_frame.grid_columnconfigure(0, weight=1)
table_frame.grid_columnconfigure(1, weight=1)
table_frame.grid_columnconfigure(2, weight=1)
table_frame.grid_columnconfigure(3, weight=1)
table_frame.grid_columnconfigure(4, weight=1)

# Table headers
table_header_company=Label(table_frame, relief=GROOVE, text="Company", font="Helvetica 9 bold")
table_header_company.grid(row=0, column=0, sticky=EW)
table_header_location=Label(table_frame, relief=GROOVE, text="Location", font="Helvetica 9 bold")
table_header_location.grid(row=0, column=1, sticky=EW)
table_header_last_name=Label(table_frame, relief=GROOVE, text="Last Name", font="Helvetica 9 bold")
table_header_last_name.grid(row=0, column=2, sticky=EW)
table_header_first_name=Label(table_frame, relief=GROOVE, text="First Name", font="Helvetica 9 bold")
table_header_first_name.grid(row=0, column=3, sticky=EW)
table_header_first_name=Label(table_frame, relief=GROOVE, text="Headline", font="Helvetica 9 bold")
table_header_first_name.grid(row=0, column=4, sticky=EW)

# Status frame
status_frame = Frame(top)
status_frame.pack(padx=10, pady=2, side=BOTTOM, expand=False, fill="x")
label_status = Label(status_frame, textvariable=status_str)
label_status.pack(side=LEFT, expand=False)

separator = ttk.Separator(top, orient='horizontal')
separator.pack(side=BOTTOM, fill='x')

top.mainloop()


