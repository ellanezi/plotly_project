import plotly.express as px
import pandas as pd
from dash import Dash,dcc,html
from dash import Input,Output

df=pd.read_csv("sales_update.csv")

print(df.head())

app=Dash(__name__)#creates webapplication and manages routing,callbacks,server
app.layout=html.Div([#allows customizing of how app displays on webpage
   html.H1("SALES BOARD PERFORMANCE",style={'text-align': 'center'}),
   dcc.Dropdown(
           id='region-dropdown',
        options=[{'label': r, 'value': r} for r in df['Region'].unique()],
#option loops through every unique region in the data and creates a selectable option for each
    value=df['Region'].unique()[0],
#value sets default region to first region in dataset on dropdown
       multi=True 
#multi allows multiple selections in drop-down
         ),
   dcc.Dropdown(
       id='month-dropdown',
       options=[{'label': m,'value' : m}for m in df['Month'].unique()],
    #option loops through every unique month in the data and creates a selectable option for each
       value=df['Month'].unique()[0],
    #value sets default month to first month in dataset on dropdown
       multi=True
        ), 
        html.Br(),#line break
   html.Label("Minimum Profit:"),#text label
   dcc.Slider(
       id='profit-slider',
       #min/max — slider range is set automatically from the actual data
       min=df['Profit'].min(),
       max=df['Profit'].max(),
       value=df['Profit'].min(),#value starts at the minimum so all data is visible by default
       #marks — only labels the two ends of the slider (min and max) with a ₦ symbol
       marks={int(df['Profit'].min()): f"₦{int(df['Profit'].min())}", 
              int(df['Profit'].max()): f"₦{int(df['Profit'].max())}"},
    #tooltip — shows the current selected value beneath the slider as you drag it
       tooltip={"placement": "bottom", "always_visible": True}
   ),
   html.Br(),

   #these are empty containers which will be filled in the callback by dash
   dcc.Graph(id='bar-chart'),
   dcc.Graph(id='line-chart'),
   dcc.Graph(id='scatter-chart'),
   dcc.Graph(id='map-chart') 
   
   ])
#this means when region or month drop-down changes it'll change 4 charts
@app.callback(
      [Output('bar-chart','figure'),#output is the 4 charts thatll update
      Output('line-chart','figure'),
      Output('scatter-chart','figure'),
      Output('map-chart','figure')],
    #multiple outputs and input require brackets for seperations
      [Input('region-dropdown','value'),#controls that triggers the update
      Input('month-dropdown','value'),
      Input('profit-slider','value')], 
)
#keep rows where region and month matches selected region and month 
def update_chart(selected_region,selected_month, min_profit):
       if isinstance(selected_region, str):
        selected_region = [selected_region]
       if isinstance(selected_month, str):
        selected_month = [selected_month]
       filtered_df=df[
        (df['Region'].isin(selected_region))& #isin()checks if each row is in the list of selected values
        (df['Month'].isin(selected_month))&#keeps rows matching user selection
        (df['Profit']>=min_profit) #only shows sales with profit above slider value and user selection
    ]
    
    
       region_df = df[df['Region'].isin(selected_region)&
            (df['Profit']>=min_profit)
            ]
        
    #bar chart
       bar_fig=px.bar(
        filtered_df,
        x='Region',
        y='Sales',
        color='Sales',
        title="Sales bar chart",
        hover_data=['Month']#adds month to the hover tooltip
    )
    #for the line chart
       line_fig = px.line(
       data_frame=region_df,
        x='Month',
        y='Sales',
        title="Monthly sales trend",
        markers=True
    )
    #for scattered chart
       scatter_fig = px.scatter(
      filtered_df,
      x= 'Sales',
      y= 'Profit',
      size='Sales',
      color='Sales',
       title="Sales vs Profit"
)
    #for the map chart
       map_fig = px.scatter_mapbox(
    filtered_df,
    lat='Latitude',
    lon='Longitude',
    size='Sales',
    zoom=3,title="Sales map",
    hover_data=['Region']
)
       map_fig.update_layout(mapbox_style="open-street-map")
#open-street-map sets map style so it works without API keys unlike google map
 
       return bar_fig, line_fig, scatter_fig, map_fig
if __name__ == "__main__":#standard dash app launcher
    app.run(debug=True)

