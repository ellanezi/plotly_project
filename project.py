import pandas as pd
import glob
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc

# STEP 1 — LOADING AND COMBINING FILES
files = glob.glob(r'C:\Users\CHISQUARE\Desktop\performance\*.csv')

dfs = []
for file in files:
    temp = pd.read_csv(file)
    dfs.append(temp)

df = pd.concat(dfs, ignore_index=True)
print(f"Loaded {len(files)} files | Total records: {len(df):,}")

# STEP 2 — CLEAN AND PREPARE DATA
df['TRADE_DATE'] = pd.to_datetime(df['TRADE_DATE'])

df['Year']     = df['TRADE_DATE'].dt.year
df['MonthNum'] = df['TRADE_DATE'].dt.month
df['Month']    = df['TRADE_DATE'].dt.strftime('%b')

df['Buy Broker Name']  = df['Buy Broker Name'].str.strip()
df['Sell Broker Name'] = df['Sell Broker Name'].str.strip()

df = df.dropna(subset=['TotQty', 'TotValue'])

# STEP 3 — BUILD DROPDOWN OPTIONS
all_brokers = sorted(set(df['Buy Broker Name'].unique()) |
                     set(df['Sell Broker Name'].unique()))
broker_options = [{'label': b, 'value': b} for b in all_brokers]
year_options   = [{'label': str(y), 'value': y}
                  for y in sorted(df['Year'].unique())]

# STEP 4 — BUILD APP LAYOUT
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

app.layout = html.Div([

    # Header
    html.H1("BROKER PERFORMANCE DASHBOARD",
            style={'textAlign': 'center', 'color': '#1a1a2e',
                   'fontFamily': 'Arial', 'padding': '30px 0 10px 0',
                   'fontSize': '36px', 'fontWeight': 'bold'}),

    html.P("Broker Trade Analysis — Volume, Value, Trades & Date",
           style={'textAlign': 'center', 'color': '#666',
                  'fontFamily': 'Arial', 'marginBottom': '30px'}),

    # Filter Row
    html.Div([

        html.Div([
            html.Label("Filter by Broker",
                       style={'fontWeight': 'bold', 'fontFamily': 'Arial'}),
            dcc.Dropdown(id='broker-dropdown', options=broker_options,
                         placeholder='All Brokers', clearable=True,
                         searchable=True, style={'fontFamily': 'Arial'})
        ], style={'flex': '2', 'marginRight': '15px'}),

        html.Div([
            html.Label("Filter by Year",
                       style={'fontWeight': 'bold', 'fontFamily': 'Arial'}),
            dcc.Dropdown(id='year-dropdown', options=year_options,
                         placeholder='All Years', clearable=True,
                         style={'fontFamily': 'Arial'})
        ], style={'flex': '1', 'marginRight': '15px'}),

        html.Div([
            html.Label("\u00a0", style={'display': 'block'}),
            html.Button("Reset Filters", id='reset-button', n_clicks=0,
                        style={'backgroundColor': '#e74c3c', 'color': 'white',
                               'border': 'none', 'padding': '10px 20px',
                               'borderRadius': '5px', 'cursor': 'pointer',
                               'fontFamily': 'Arial', 'fontWeight': 'bold',
                               'width': '100%'})
        ], style={'flex': '0.5'})

    ], style={'display': 'flex', 'alignItems': 'flex-end',
              'padding': '0 40px', 'marginBottom': '20px'}),

    # Summary Table
    html.Div([
        html.H3("Broker Summary Stats",
                style={'fontFamily': 'Arial', 'color': '#1a1a2e',
                       'marginBottom': '15px'}),
        html.Div(id='summary-table')
    ], style={'padding': '0 40px', 'marginBottom': '40px'}),

    # Charts
    html.Div([
        dcc.Graph(id='bar-chart',   style={'marginBottom': '40px'}),
        dcc.Graph(id='grouped-bar', style={'marginBottom': '40px'}),
        dcc.Graph(id='heatmap',     style={'marginBottom': '40px'}),
    ], style={'padding': '0 40px'})

], style={'backgroundColor': '#f8f9fa', 'minHeight': '100vh'})

# STEP 5 — RESET BUTTON CALLBACK
@callback(
    Output('broker-dropdown', 'value'),
    Output('year-dropdown',   'value'),
    Input('reset-button',     'n_clicks')
)
def reset_filter(n_clicks):
    return None, None

# STEP 6 — MAIN DASHBOARD CALLBACK
@callback(
    Output('summary-table', 'children'),
    Output('bar-chart',     'figure'),
    Output('grouped-bar',   'figure'),
    Output('heatmap',       'figure'),
    Input('broker-dropdown', 'value'),
    Input('year-dropdown',   'value')
)
def update_dashboard(selected_broker, selected_year):

    filtered = df.copy()

    if selected_year:
        filtered = filtered[filtered['Year'] == selected_year]

    if selected_broker:
        filtered = filtered[
            (filtered['Buy Broker Name']  == selected_broker) |
            (filtered['Sell Broker Name'] == selected_broker)
        ]

     
    # Summary stats per broker
    buy_summary = filtered.groupby('Buy Broker Name').agg(
        BuyTrades=('TotQty', 'count'),      
        BuyQty=('TotQty', 'sum'),
        BuyValue=('TotValue', 'sum')
    ).reset_index().rename(columns={'Buy Broker Name': 'Broker'})
    sell_summary = filtered.groupby('Sell Broker Name').agg(
        SellTrades=('TotQty', 'count'),
        SellQty=('TotQty', 'sum'),
        SellValue=('TotValue', 'sum')
    ).reset_index().rename(columns={'Sell Broker Name': 'Broker'})
    summary = pd.merge(buy_summary, sell_summary, on='Broker', how='outer').fillna(0)
    summary['TotalTrades'] = summary['BuyTrades'] + summary['SellTrades']
    summary['TotalQty']    = summary['BuyQty'] + summary['SellQty']
    summary['TotalValue']  = summary['BuyValue'] + summary['SellValue']

    # Best date per broker
    best_dates = filtered.groupby(
        ['Buy Broker Name', 'TRADE_DATE'])['TotQty'].sum().reset_index()
    best_dates = best_dates.loc[
        best_dates.groupby('Buy Broker Name')['TotQty'].idxmax()
    ].rename(columns={'Buy Broker Name': 'Broker',
                      'TRADE_DATE': 'BestDate',
                      'TotQty': 'PeakQty'})

    summary = summary.merge(best_dates[['Broker', 'BestDate']],
                             on='Broker', how='left')
    summary['BestDate'] = pd.to_datetime(summary['BestDate'])\
                            .dt.strftime('%d %b %Y')
    summary = summary.sort_values('TotalQty', ascending=False).head(20)

    # Build HTML table
    table = html.Table([
        html.Thead(html.Tr([
            html.Th("Broker",          style={'padding': '10px', 'textAlign': 'left',   'backgroundColor': '#1a1a2e', 'color': 'white', 'fontFamily': 'Arial'}),
            html.Th("Best Date",       style={'padding': '10px', 'textAlign': 'center', 'backgroundColor': '#1a1a2e', 'color': 'white', 'fontFamily': 'Arial'}),
            html.Th("Buy Trades",      style={'padding': '10px', 'textAlign': 'center', 'backgroundColor': '#1a1a2e', 'color': 'white', 'fontFamily': 'Arial'}),
            html.Th("Sell Trades",     style={'padding': '10px', 'textAlign': 'center', 'backgroundColor': '#1a1a2e', 'color': 'white', 'fontFamily': 'Arial'}),
            html.Th("Total Trades",    style={'padding': '10px', 'textAlign': 'center', 'backgroundColor': '#1a1a2e', 'color': 'white', 'fontFamily': 'Arial'}),
            html.Th("Total Qty",       style={'padding': '10px', 'textAlign': 'center', 'backgroundColor': '#1a1a2e', 'color': 'white', 'fontFamily': 'Arial'}),
            html.Th("Total Value (₦)", style={'padding': '10px', 'textAlign': 'center', 'backgroundColor': '#1a1a2e', 'color': 'white', 'fontFamily': 'Arial'}),
        ])),
        html.Tbody([
            html.Tr([
                html.Td(row['Broker'],                style={'padding': '8px 10px', 'fontFamily': 'Arial', 'borderBottom': '1px solid #eee'}),
                html.Td(row['BestDate'],               style={'padding': '8px 10px', 'fontFamily': 'Arial', 'borderBottom': '1px solid #eee', 'textAlign': 'center'}),
                html.Td(f"{int(row['BuyTrades']):,}",  style={'padding': '8px 10px', 'fontFamily': 'Arial', 'borderBottom': '1px solid #eee', 'textAlign': 'center'}),
                html.Td(f"{int(row['SellTrades']):,}", style={'padding': '8px 10px', 'fontFamily': 'Arial', 'borderBottom': '1px solid #eee', 'textAlign': 'center'}),
                html.Td(f"{int(row['TotalTrades']):,}",style={'padding': '8px 10px', 'fontFamily': 'Arial', 'borderBottom': '1px solid #eee', 'textAlign': 'center', 'fontWeight': 'bold'}),
                html.Td(f"{int(row['TotalQty']):,}",   style={'padding': '8px 10px', 'fontFamily': 'Arial', 'borderBottom': '1px solid #eee', 'textAlign': 'center'}),
                html.Td(f"₦{row['TotalValue']:,.0f}",  style={'padding': '8px 10px', 'fontFamily': 'Arial', 'borderBottom': '1px solid #eee', 'textAlign': 'center'}),
            ], style={'backgroundColor': 'white' if i % 2 == 0 else '#f8f9fa'})
            for i, (_, row) in enumerate(summary.iterrows())
        ])
    ], style={'width': '100%', 'borderCollapse': 'collapse',
              'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
              'borderRadius': '8px', 'overflow': 'hidden'})

    # Chart 1 — Horizontal Bar
    top20_bar = summary.sort_values('TotalTrades', ascending=True)
    fig1 = px.bar(
        top20_bar,
        x='TotalTrades', y='Broker', orientation='h',
        title='<b>Top 20 Brokers by Total Number of Trades</b>',
        color='TotalTrades', color_continuous_scale='Teal',
        text_auto='.3s',
        labels={'TotalTrades': 'Total Trades', 'Broker': ''}
    )
    fig1.update_traces(textposition='outside',
                       hovertemplate='<b>%{y}</b><br>Total Trades: %{x:,.0f}<extra></extra>')
    fig1.update_layout(height=700, plot_bgcolor='white', paper_bgcolor='white',
                       coloraxis_showscale=False, font=dict(family='Arial', size=12),
                       margin=dict(l=280, r=80, t=80, b=60))

    # Chart 2 — Grouped Bar
    yearly = filtered.copy()
    grouped = yearly.groupby(['Year', 'Buy Broker Name']).size().reset_index()
    grouped.columns = ['Year', 'Broker', 'Trades']
    top10_brokers = summary.head(10)['Broker'].tolist()
    yearly = yearly[yearly['Broker'].isin(top10_brokers)]

    fig2 = px.bar(
        yearly,
        x='Year', y='Trades', color='Broker', barmode='group',
        title='<b>Top 10 Brokers — Performance by Year</b>',
        labels={'Trades': 'Number of Trades', 'Year': 'Year'}
    )
    fig2.update_traces(
        hovertemplate='<b>%{fullData.name}</b><br>Year: %{x}<br>Trades: %{y:,.0f}<extra></extra>')
    fig2.update_layout(
        height=550, plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Arial', size=12),
        legend=dict(title='Broker', orientation='v'),
        xaxis=dict(showgrid=False, type='category'),
        yaxis=dict(showgrid=True, gridcolor='#eeeeee'),
        margin=dict(l=80, r=80, t=80, b=60))

    # Chart 3 — Heatmap
    month_labels = ['Jan','Feb','Mar','Apr','May','Jun',
                    'Jul','Aug','Sep','Oct','Nov','Dec']

    monthly = filtered.groupby(['Year', 'MonthNum']).size().reset_index()
    monthly.columns = ['Year', 'MonthNum', 'TradeCount']
    pivot = monthly.pivot(index='Year', columns='MonthNum',
                          values='TradeCount').fillna(0)
    for m in range(1, 13):
        if m not in pivot.columns:
            pivot[m] = 0
    pivot = pivot[sorted(pivot.columns)]

    fig3 = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=month_labels,
        y=pivot.index.astype(str),
        colorscale='YlOrRd',
        hovertemplate='Year: %{y}<br>Month: %{x}<br>Trades: %{z:,.0f}<extra></extra>',
        colorbar=dict(title='Number of Trades')
    ))
    fig3.update_layout(
        title='<b>Trading Activity Heatmap — Month vs Year</b>',
        xaxis_title='Month', yaxis_title='Year',
        height=400, plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Arial', size=12),
        margin=dict(l=80, r=80, t=80, b=60))

    return table, fig1, fig2, fig3

# STEP 7 — RUN THE APP
if __name__ == '__main__':
    app.run(debug=True)