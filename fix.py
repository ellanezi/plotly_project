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
            (filtered['Buy Broker Name'] == selected_broker) |
            (filtered['Sell Broker Name'] == selected_broker)
        ]

    # =========================
    # FIX: MELT EACH ROW INTO TWO BROKER ENTRIES (BUY + SELL)
    # This gives each broker credit for their side of every trade
    # without double-counting the trade itself.
    # =========================

    buy_side = filtered[['Buy Broker Name', 'TotQty', 'TotValue', 'TRADE_DATE', 'Year', 'MonthNum']].copy()
    buy_side = buy_side.rename(columns={'Buy Broker Name': 'Broker'})
    buy_side['Side'] = 'Buy'

    sell_side = filtered[['Sell Broker Name', 'TotQty', 'TotValue', 'TRADE_DATE', 'Year', 'MonthNum']].copy()
    sell_side = sell_side.rename(columns={'Sell Broker Name': 'Broker'})
    sell_side['Side'] = 'Sell'

    long_df = pd.concat([buy_side, sell_side], ignore_index=True)

    # =========================
    # SUMMARY: aggregate by broker across both sides
    # =========================

    buy_stats = long_df[long_df['Side'] == 'Buy'].groupby('Broker').agg(
        BuyQty=('TotQty', 'sum'),
        BuyValue=('TotValue', 'sum'),
        BuyTrades=('TotQty', 'count')
    ).reset_index()

    sell_stats = long_df[long_df['Side'] == 'Sell'].groupby('Broker').agg(
        SellQty=('TotQty', 'sum'),
        SellValue=('TotValue', 'sum'),
        SellTrades=('TotQty', 'count')
    ).reset_index()

    summary = buy_stats.merge(sell_stats, on='Broker', how='outer').fillna(0)

    # TotalQty = volume handled on buy side + volume handled on sell side
    summary['TotalQty']    = summary['BuyQty'] + summary['SellQty']
    summary['TotalValue']  = summary['BuyValue'] + summary['SellValue']
    summary['TotalTrades'] = summary['BuyTrades'].astype(int) + summary['SellTrades'].astype(int)

    # =========================
    # BEST DATE — day with highest single-side volume for each broker
    # =========================

    best_dates = long_df.groupby(['Broker', 'TRADE_DATE'])['TotQty'].sum().reset_index()
    best_dates = best_dates.loc[
        best_dates.groupby('Broker')['TotQty'].idxmax()
    ][['Broker', 'TRADE_DATE']].rename(columns={'TRADE_DATE': 'BestDate'})

    summary = summary.merge(best_dates, on='Broker', how='left')
    summary['BestDate'] = pd.to_datetime(summary['BestDate']).dt.strftime('%d %b %Y')

    # Sort by total volume, take top 20
    summary = summary.sort_values('TotalQty', ascending=False).head(20)

    # =========================
    # HTML TABLE (original styling preserved)
    # =========================

    table = html.Table([
        html.Thead(html.Tr([
            html.Th("Broker",        style={'padding': '10px', 'textAlign': 'left',   'backgroundColor': '#1a1a2e', 'color': 'white', 'fontFamily': 'Arial'}),
            html.Th("Best Date",     style={'padding': '10px', 'textAlign': 'center', 'backgroundColor': '#1a1a2e', 'color': 'white', 'fontFamily': 'Arial'}),
            html.Th("Buy Volume",    style={'padding': '10px', 'textAlign': 'center', 'backgroundColor': '#1a1a2e', 'color': 'white', 'fontFamily': 'Arial'}),
            html.Th("Sell Volume",   style={'padding': '10px', 'textAlign': 'center', 'backgroundColor': '#1a1a2e', 'color': 'white', 'fontFamily': 'Arial'}),
            html.Th("Total Trades",  style={'padding': '10px', 'textAlign': 'center', 'backgroundColor': '#1a1a2e', 'color': 'white', 'fontFamily': 'Arial'}),
            html.Th("Total Qty",     style={'padding': '10px', 'textAlign': 'center', 'backgroundColor': '#1a1a2e', 'color': 'white', 'fontFamily': 'Arial'}),
            html.Th("Total Value (₦)", style={'padding': '10px', 'textAlign': 'center', 'backgroundColor': '#1a1a2e', 'color': 'white', 'fontFamily': 'Arial'}),
        ])),
        html.Tbody([
            html.Tr([
                html.Td(row['Broker'],                          style={'padding': '8px 10px', 'fontFamily': 'Arial', 'borderBottom': '1px solid #eee'}),
                html.Td(row['BestDate'],                        style={'padding': '8px 10px', 'fontFamily': 'Arial', 'borderBottom': '1px solid #eee', 'textAlign': 'center'}),
                html.Td(f"{int(row['BuyQty']):,}",             style={'padding': '8px 10px', 'fontFamily': 'Arial', 'textAlign': 'center'}),
                html.Td(f"{int(row['SellQty']):,}",            style={'padding': '8px 10px', 'fontFamily': 'Arial', 'textAlign': 'center'}),
                html.Td(f"{int(row['TotalTrades']):,}",        style={'padding': '8px 10px', 'fontFamily': 'Arial', 'textAlign': 'center', 'fontWeight': 'bold'}),
                html.Td(f"{int(row['TotalQty']):,}",           style={'padding': '8px 10px', 'fontFamily': 'Arial', 'textAlign': 'center'}),
                html.Td(f"₦{row['TotalValue']:,.0f}",          style={'padding': '8px 10px', 'fontFamily': 'Arial', 'textAlign': 'center'}),
            ], style={'backgroundColor': 'white' if i % 2 == 0 else '#f8f9fa'})
            for i, (_, row) in enumerate(summary.iterrows())
        ])
    ], style={'width': '100%', 'borderCollapse': 'collapse',
              'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
              'borderRadius': '8px', 'overflow': 'hidden'})

    # =========================
    # BAR CHART (original styling preserved)
    # =========================

    top20_bar = summary.sort_values('TotalQty', ascending=True)

    fig1 = px.bar(
        top20_bar,
        x='TotalQty',
        y='Broker',
        orientation='h',
        title='<b>Top 20 Brokers by Total Trade Volume</b>',
        color='TotalQty',
        color_continuous_scale='Teal',
        text_auto='.3s',
        labels={'TotalQty': 'Total Volume (Qty)', 'Broker': ''}
    )

    fig1.update_traces(
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Total Volume: %{x:,.0f}<extra></extra>'
    )

    fig1.update_layout(
        height=700,
        plot_bgcolor='white',
        paper_bgcolor='white',
        coloraxis_showscale=False,
        font=dict(family='Arial', size=12),
        margin=dict(l=280, r=80, t=80, b=60)
    )

    # =========================
    # GROUPED BAR — FIX: use long_df so each broker's yearly volume
    # is counted once per side, then summed — no double counting
    # =========================

    top10_brokers = summary['Broker'].head(10).tolist()

    yearly = long_df[long_df['Broker'].isin(top10_brokers)].groupby(
        ['Year', 'Broker']
    )['TotQty'].sum().reset_index().rename(columns={'TotQty': 'Volume'})

    fig2 = px.bar(
        yearly,
        x='Year',
        y='Volume',
        color='Broker',
        barmode='group',
        title='<b>Top 10 Brokers — Trade Volume by Year</b>',
        labels={'Volume': 'Total Volume (Qty)', 'Year': 'Year'}
    )

    fig2.update_layout(
        height=550,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Arial', size=12),
        legend=dict(title='Broker', orientation='v'),
        xaxis=dict(showgrid=False, type='category'),
        yaxis=dict(showgrid=True, gridcolor='#eeeeee'),
        margin=dict(l=80, r=80, t=80, b=60)
    )

    # =========================
    # HEATMAP (unchanged)
    # =========================

    month_labels = ['Jan','Feb','Mar','Apr','May','Jun',
                    'Jul','Aug','Sep','Oct','Nov','Dec']

    monthly = filtered.groupby(['Year', 'MonthNum']).size().reset_index()
    monthly.columns = ['Year', 'MonthNum', 'TradeCount']

    pivot = monthly.pivot(index='Year', columns='MonthNum', values='TradeCount').fillna(0)

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
        xaxis_title='Month',
        yaxis_title='Year',
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Arial', size=12),
        margin=dict(l=80, r=80, t=80, b=60)
    )

    return table, fig1, fig2, fig3

# STEP 7 — RUN THE APP
if __name__ == '__main__':
    app.run(debug=True)