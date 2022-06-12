import sys
import os
from tkinter import filedialog
import pandas as pd
import xlsxwriter
from ttkbootstrap import Style
from pandastable import Table
from linkedin_api import linkedin

def show_exception(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    error_desc = "Error: " + repr(e) + " in " + str(fname) + " line " + str(exc_tb.tb_lineno) + "\n"
    print(error_desc)
    return error_desc

def listdir_recursive(directory):
    file_list = []
    for root, _, files in os.walk(directory):
        for f_name in files:
            file_list.append(os.path.relpath(os.path.join(root, f_name)))
    return file_list

def fit_table_style_to_theme(pdtable: Table, theme_style: Style):
    colors = theme_style.colors
    pdtable.__dict__.update({'cellbackgr':colors.bg,'grid_color':colors.secondary, 'textcolor':colors.inputfg,
                 'rowselectedcolor':colors.secondary, 'colselectedcolor':colors.selectbg})

def set_bools_from_list(bool_dict_list, list):
    for bool_var in bool_dict_list:
        if bool_var['name'] in list:
            bool_var['bool_val'].set(True)
        else:
            bool_var['bool_val'].set(False)

def save_dataframe_to_file(dataframe, keep_index=False, json_orient="records"):
    COLUMN_MAX_LENGTH = 200
    chosen_file = filedialog.asksaveasfile(mode='w', filetypes=[("Excel", ".xlsx"), ("HTML", ".html"),
                                                                ("CSV", ".csv"), ("JSON", ".json")], defaultextension=".xlsx")
    if chosen_file is None:
        return

    file_ext = os.path.splitext(chosen_file.name)[1]
    # create excel writer object
    if file_ext == ".xlsx":
        with pd.ExcelWriter(chosen_file.name) as writer:

            # write dataframe to excel
            dataframe.to_excel(writer, index=keep_index)
            worksheet = writer.sheets['Sheet1']

            # Iterate through each column and set the width == the max length in that column. A padding length of 2 is also added.
            for i, col in enumerate(dataframe.columns):
                # find length of column i
                column_len = dataframe[col].astype(str).str.len().max()
                # Setting the length if the column header is larger than the max column value length
                column_len = max(column_len, len(col)) + 2
                column_len = min(column_len, COLUMN_MAX_LENGTH)
                # set the column length
                worksheet.set_column(i+keep_index, i+keep_index, column_len)

            # handling index separately
            if keep_index:
                index_len = dataframe.index.astype(str).str.len().max() + 2
                index_len = min(index_len, COLUMN_MAX_LENGTH)
                worksheet.set_column(0, 0, index_len)

            # save the excel
            writer.save()
            print('DataFrame was written successfully to Excel File: ' + chosen_file.name)
    
    elif file_ext == ".html":
        dataframe.to_html(chosen_file.name, index=keep_index)

    elif file_ext == ".csv":
        dataframe.to_csv(chosen_file.name, index=keep_index)

    elif file_ext == ".json":
        dataframe.to_json(chosen_file.name, index=keep_index, orient=json_orient, indent=4)

    return chosen_file.name

def extract_urn_dict_from_query_results(linkedin_meth, search_kw):
    res = linkedin_meth(search_kw)
    return {x.get('text', {}).get('text', '') : 
            x.get('targetUrn', '').rsplit(':', 1)[-1]
            for x in res}
