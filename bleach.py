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
fig= px.bar(df,x='Year',y='DividendPaid',color='SECTOR',title='Dividend paid per year')
fig.write_html("dividend_chart.html")
print("chart saved open 'dividend_chart.html' in browser")    
#--PIE CHART--
sector_totals = df.groupby('SECTOR')['DividendPaid'].sum().reset_index()
fig_pie = px.pie(sector_totals, names='SECTOR', values='DividendPaid', 
                 title='Total Dividend Distribution by Sector (All Years)', hole=0.4)
fig_pie.write_html("dividend_pie_chart1.html")
print("Pie chart saved: open 'dividend_pie_chart1.html' in browser")