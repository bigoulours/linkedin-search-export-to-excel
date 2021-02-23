from tkinter import filedialog
import pandas as pd
import xlsxwriter

COLUMN_MAX_LENGTH = 200

def save_to_xsl(dataframe):
    chosen_file = filedialog.asksaveasfile(mode='w', filetypes=[("Excel files", ".xlsx")], defaultextension=".xlsx")
    if chosen_file is None:
        return

    # create excel writer object
    writer = pd.ExcelWriter(chosen_file.name)

    # write dataframe to excel
    dataframe.to_excel(writer, index=False)
    worksheet = writer.sheets['Sheet1']

    # Iterate through each column and set the width == the max length in that column. A padding length of 2 is also added.
    for i, col in enumerate(dataframe.columns):
        # find length of column i
        column_len = dataframe[col].astype(str).str.len().max()
        # Setting the length if the column header is larger than the max column value length
        column_len = max(column_len, len(col)) + 2
        column_len = min(column_len, COLUMN_MAX_LENGTH)
        # set the column length
        worksheet.set_column(i, i, column_len)

    # save the excel
    writer.save()
    chosen_file.close()
    print('DataFrame was written successfully to Excel File: ' + chosen_file.name)
    return chosen_file.name