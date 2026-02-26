import pandas as pd
import matplotlib.pyplot as plt
df= pd.read_csv("BOOK.csv")
print(df)
plt.bar(df['MONTH'],df['SALES'], color='darkblue')
plt.title("SALES MADE IN A YEAR")
plt.xlabel("MONTH")
plt.ylabel("SALES")
plt.xticks(rotation=45, ha='right')#to create space for longer names 
plt.show()