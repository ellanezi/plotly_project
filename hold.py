import pandas as pd
import glob

files = glob.glob(r'C:\Users\CHISQUARE\Desktop\performance\*.xlsx')
for file in files:
    df = pd.read_excel(file)
    df.to_csv(file.replace('.xlsx', '.csv'), index=False)
    print(f"Converted: {file}")
     