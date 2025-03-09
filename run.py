import re
import tabula
import pandas as pd
import glob
import argparse

parser = argparse.ArgumentParser(description='Extract tables from PDF files')
parser.add_argument('--pdf_directory', '-d', required=True, help='Path to the PDF file')
parser.add_argument('--password', '-p', help='Password of enrcypted PDF file')
parser.add_argument('--output', '-o', help='Path to the output file')
args = parser.parse_args()

try:
    table = tabula.read_pdf(args.pdf_directory, pages='all', password=args.password, stream=True, multiple_tables=False)[0]
    table = table[table['Date and Time'] != 'Date and Time']
    print(table)
except:
    print('Error: PDF file not found or password is incorrect')
    exit()

if args.output:
    try:
        output_path = f"{args.output}/output.csv"
        table.to_csv(output_path, index=False)
        print('Output saved at {}'.format(output_path))
    except:
        print('Error: Invalid output path or File already exists')
        exit()
