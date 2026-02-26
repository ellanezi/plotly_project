import pandas as pd
import matplotlib.pyplot as plt
df= pd.read_csv("BOOK.csv")
print(df)
plt.plot(df['MONTH'],df['SALES'],marker=".",markersize=10,markerfacecolor="black",mec="black")
plt.xlabel("MONTH")
plt.ylabel("SALES")
plt.title("yearly sales distribution")
plt.xticks(rotation=45,ha='right')
plt.show()

 