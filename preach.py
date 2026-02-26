import pandas as pd
import matplotlib.pyplot as plt
df= pd.read_csv("BOOK.csv")
print(df)
plt.pie(df['SALES'],labels=df['MONTH'],autopct='%1.1f%%')
plt.title("yearly sales distribution")
plt.show()