import pandas as pd
import plotly.express as px
from dash import Dash,dcc,html
from dash.dependencies import Input,Output
df=pd.read_csv("sales.csv")
print(df.head())
fig=px.bar(df, x='Month',y='Sales',color='Region')
app=Dash(__name__)
app.layout = html.Div([
    html.H1("Interactive Sales Dashboard"),
    dcc.Graph(id='sales-chart', figure=fig),
    dcc.Dropdown(
        id='Region-dropdown',
        options=[
            {'label': 'West','value':'West'},
            {'label':'East','value':'East'},
            {}
        ],
        value='West'),
           ])
#callback comes after layout
@app.callback(
    Output('sales-chart','figure'),
    Input('Region-dropdown','value'),

)
def update_chart(selected_region):
    filtered_df = df[df['Region'] == selected_region]
    fig = px.line(filtered_df, x='Month', y='Sales',
                 title=f"Sales in {selected_region}")
    return fig

app.run(debug=True)