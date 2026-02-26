import plotly.express as px
import pandas as pd
from dash import Dash,dcc,html
from dash import Input,Output
df=pd.read_csv("sales_update.csv")

print(df.head())

app=Dash(__name__)
app.layout=html.Div([# everything here appears on the web page
   html.H1("SALES BOARD PERFORMANCE",style={'text-align': 'center'}),
   dcc.Dropdown(
           id='region-dropdown',
        options=[{'label': r, 'value': r} for r in df['Region'].unique()],
       value=df['Region'].unique()[0],
       multi=True #allows multiple selections in drop-down
         ),
   dcc.Dropdown(
       id='month-dropdown',
       options=[{'label': m,'value' : m}for m in df['Month'].unique()],
       value=df['Month'].unique()[0],
       multi=True
        ), 
        html.Br(),#line break
   html.Label("Minimum Profit:"),#text label
   dcc.Slider(
       id='profit-slider',
       min=df['Profit'].min(),
       max=df['Profit'].max(),
       value=df['Profit'].min(),  # Start at minimum (show all)
       marks={int(df['Profit'].min()): f"₦{int(df['Profit'].min())}", 
              int(df['Profit'].max()): f"₦{int(df['Profit'].max())}"},
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
      [Output('bar-chart','figure'),
      Output('line-chart','figure'),
      Output('scatter-chart','figure'),
      Output('map-chart','figure')],
    #multiple outputs and input require brackets for seperations
      [Input('region-dropdown','value'),
      Input('month-dropdown','value'),
      Input('profit-slider','value')],#adding the slider to my call back
)
#keep rows where region and month matches selected regiona and month
   
def update_chart(selected_region,selected_month, min_profit):
       if isinstance(selected_region, str):
        selected_region = [selected_region]
       if isinstance(selected_month, str):
        selected_month = [selected_month]
       filtered_df=df[
        (df['Region'].isin(selected_region)) & #isin()checks if each row is in the list of selected values
        (df['Month'].isin(selected_month))&
        (df['Profit']>=min_profit) #only shows sales with profit above slider value
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
        title="Sales bar chart"
    )
    #for the line chart
       line_fig = px.line(
       data_frame=region_df,
        x='Month',
        y='Sales',
        title="Monthly sales trend"
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
    zoom=3,title="Sales map"
)
       map_fig.update_layout(mapbox_style="open-street-map")#sets map style so it works without API keys
 
       return bar_fig, line_fig, scatter_fig, map_fig
if __name__ == "__main__":
    app.run(debug=True)

