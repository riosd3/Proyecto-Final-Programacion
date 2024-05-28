import pandas as pd
from os import environ, listdir
from os.path import join
from re import search

# Define the directory containing the CSV files
filesdir = join(environ["USERPROFILE"], "Downloads/scraps/scraps")
files = listdir(filesdir)

# Function to extract the number from the filename
def extract_number(filename):
    match = search(r'\d+', filename)
    return int(match.group()) if match else 0

# Sort the files based on the numeric part
sorted_files = sorted(files, key=extract_number)

# Initialize an empty list to hold the DataFrames and a set for all columns
dataframes = []

# Read the first file to get the column names
first_file = sorted_files[0]
df = pd.read_csv(join(filesdir, first_file), dtype=str)
df = df.drop(df.columns[0], axis=1)
dataframes.append(df)
#print(df);input("PRESS ENTER")

# Get the column names from the first file
columns = df.columns
# Read the rest of the files without the header
for f in sorted_files[1:]:
    df = pd.read_csv(join(filesdir, f), header=None, skiprows=1, dtype=str, names=columns)
    #df = df.drop(df.columns[0], axis=1)
    dataframes.append(df)
    #print(df);input("PRESS ENTER")

# Concatenate all DataFrames into a single DataFrame
concatenated_df = pd.concat(dataframes, ignore_index=True)

# Set display options to show all rows and columns
#pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# Print the concatenated DataFrame
print(concatenated_df)
#concatenated_df.to_csv(join(environ["USERPROFILE"], "Desktop/concatenated_scraps.csv"))
