import tabula
import pandas as pd
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Parse GCash Transaction Statements from provided PDF files into usable data-centric CSV files')
parser.add_argument('--pdf_directory', '-d', required=True, help='Path directory to the input PDF file')
parser.add_argument('--output', '-o',required=True, help='Path directory to the output CSV file')
parser.add_argument('--password', '-p', help='(Optional) Password of enrcypted PDF file')
parser.add_argument('--debug', '-de', action='store_true', default=False, help='WARNING: Debug mode')
args = parser.parse_args()

def fixDF(o_table):
    table = o_table.copy()
    # table.to_csv(f"{args.output}/output_deb.csv", index=False)
    col_names = [col for col in table.columns if not col.startswith('Unnamed')] # Remove phantom columns with Unnamed
    if len(col_names) < len(table.columns): # temporary column
        col_names.append('temp')
    # print(col_names)
    table.columns = col_names # Rename columns
    for index, each in table.iterrows(): # Iterate each thru record
        # If Starting Balance / Ending Balanced is misaligned, shift values to correct column
        if (each.iloc[1] == 'STARTING BALANCE' or each.iloc[1] == 'ENDING BALANCE') and pd.notna(each.iloc[len(each)-1]):
            each.iloc[len(each)-2] = each.iloc[len(each)-1]
            each.iloc[len(each)-1] = np.nan
        # If ANY record if misaligned, shift values to correct column
        if pd.notna(each.iloc[0]) and pd.isna(each.iloc[2]):
            for i in range(2, len(each)-1):
                each.iloc[i] = each.iloc[i+1]
            each.iloc[6] = np.nan
        
        if pd.isna(each.iloc[0]) and pd.isna(each.iloc[2]) and not (each.iloc[1] == 'STARTING BALANCE' or each.iloc[1] == 'ENDING BALANCE'):
            # log = f'{index+2} empty record found'
            if pd.notna(table.iloc[index+2,1]) and pd.notna(table.iloc[index,1]):
                # log += f' | {table.iloc[index,1]} | {table.iloc[index+2,1]}'
                nextValueStr = table.iloc[index+2,1]
                # if type(table.iloc[index,1]) == float:
                #     print(nextValueStr)
                #     print(type(nextValueStr))
                #     print(table.iloc[index,1])
                #     print(type(table.iloc[index,1]))
                table.iloc[index,1] += nextValueStr
                # log += f' | {table.iloc[index,1]}'
                table.iloc[index+1,1] = each.iloc[1]
                table.iloc[index,1] = np.nan
                table.iloc[index+2,1] = np.nan
                # log += f' | {table.iloc[index,1]}'
            # print(log)
                
    table.dropna(how='all', inplace=True) # Remove empty rows
    table.drop(columns=['temp'], inplace=True) # Remove temporary column
    table = table[table['Date and Time'] != 'Date and Time'] # Remove header duplicates within the table
    return table

def main():
    # TODO: Total Debit and Total Credit missing from final output file 
    try:
        table = tabula.read_pdf(args.pdf_directory, pages='all', password=args.password, stream=True, multiple_tables=False)
        table = fixDF(table[0])
        
    except Exception as e:
        print(f'Error: {e}')
        exit()

    if args.debug: 
        print(table)

    if args.output:
        try:
            output_path = f"{args.output}/output.csv"
            table.to_csv(output_path, index=False)
            print('Output saved at {}'.format(output_path))
        except:
            print('Error: Invalid output path or File already exists')
            exit()

if __name__ == '__main__':
    main()