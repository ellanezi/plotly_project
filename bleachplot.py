from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
username="root"
password="Jesusislord22."
host="localhost"
database="crystal"
#connection string
conn_str=f"mysql+pymysql://{username}:{password}@{host}/{database}"
#create engine
engine=create_engine(conn_str) #create a connection sting to mysql database
#query your dividend table
query="SELECT * from dividend"
df=pd.read_sql(query,engine)
#preview
print(df.head())#prints first 5 rows by default
#--- BAR CHART ---
fig= px.bar(df,x='SECTOR',y='TotVolume',color='Year',title='Total volume  in a year paid by each sector')
fig.write_html("dividend_chart1.html")
print("chart saved open 'dividend_chart1.html' in browser")   

