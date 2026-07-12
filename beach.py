from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
load_dotenv()
username=os.getenv("DB_USERNAME")
password=os.getenv("DB_PASSWORD")
host=os.getenv("DB_HOST")
database=os.getenv("DB_DATABASE")
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
print("Bar chart saved: open 'dividend_chart1.html' in browser")   

#--PIE CHART--
sector_totals = df.groupby('SECTOR')['DividendPaid'].sum().reset_index()
fig_pie = px.pie(sector_totals, names='SECTOR', values='DividendPaid', 
                 title='Total Dividend Distribution by Sector (All Years)', hole=0.4)
fig_pie.write_html("dividend_pie_chart1.html")
print("Pie chart saved: open 'dividend_pie_chart1.html' in browser")

#--CANDLE STICK CHART---
#aggregating data by sectors
df=df.sort_values('Year')
#normalize dividends by sector
sector_mean= df.groupby('SECTOR')['DividendPaid'].mean()
#sector_mean groups sectors and calculates average dividend paid for each across all years
df['DividendNorm']=df['DividendPaid']/ df['SECTOR'].map(sector_mean)*100 
#dividendNorm expresses each company's dividend as a % of its sector's average(avrage dividend paid across all companies within thar sector).
ohlc=df.groupby('SECTOR').agg( #summarizes each sector into 4 values
#to collapse the rows with multiple sectors into one row per sector
    Open=('DividendNorm','first'),
    High=('DividendNorm','max'),
    Low=('DividendNorm','min'),
    Close=('DividendNorm','last')
).reset_index()
#to reset the rows in the dataframe after filtering  ie converts it back to normal so it can be read correctly
#making the candle stick figures
fig2=go.Figure(data=[go.Candlestick(
    x=ohlc['SECTOR'],#x axis each sector
    open=ohlc['Open'],
    high=ohlc['High'],
    low=ohlc['Low'],
    close=ohlc['Close'],
    increasing_line_color='green', #green when close>open
    decreasing_line_color='red' #red when close<open
)])
#styling the chart
fig2.update_layout(
    title='Sector Performance Candle Stick view',
    xaxis_title='Sector',
    yaxis_title='Relative Performance(% of sector mean)',
    xaxis_rangeslider_visible=False,#to remove default slider for time chart series 
    template='plotly_dark'#customise theme
)
fig2.write_html("dividend_candle.html")
print("Candlestick chart saved: open dividend_candle.html in browser")

print(df['Year'].dtype)
