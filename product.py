import zipfile
import pandas as pd
import plotly.graph_objects as go
from dash import Dash,html,dcc,Input,Output,dash_table
import warnings
warnings.filterwarnings('ignore')
#warnings is to control the display of warning messages in Python. 
#By using warnings.filterwarnings('ignore'), you can suppress the display of warning messages in your code. 
# This can be useful when you want to prevent certain warnings from cluttering your output.

#-STEP 1: Load the data--#
ZIP_PATH="product.zip.zip"
print("loading data from zip file... ")
dfs = []
with zipfile.ZipFile(ZIP_PATH) as z:#opens zipfile safely using a context manager (with statement).
    for name in sorted(z.namelist()):#arranges files to be processed in order
        if name.endswith(".xlsx"):
            with z.open(name) as f:#opens each excel file
                df_part = pd.read_excel(f)
                dfs.append(df_part)#adds dataframe to the list of dataframes
master = pd.concat(dfs,ignore_index=True)#combines all dataframe into one dataframe
print(f"loaded {len(master):,} total rows")

#--STEP 2: Clean and prepare data--#
#map raw asset codes to readable labels
ASSET_MAP = {
    "ETF": "ETF",
    "DEBT": "Fixed Income",
    "SUBSOV_DEBT": "Fixed Income"
}
df = master[master["ASSET"].isin(ASSET_MAP.keys())].copy() 
df["AssetClass"] = df["ASSET"].map(ASSET_MAP)
#filters the master dataframe to include only rows where the "ASSET" column contains values that are keys in the ASSET_MAP dictionary.
df["Trade_Date"] = pd.to_datetime(df["Trade_Date"])
df["Year"]  = df["Trade_Date"].dt.year
df["Month"] = df["Trade_Date"].dt.to_period("M").astype(str)

print(f"Filtered to {len(df):,} ETF +  Fixed Income rows") 

#-COLOR PALETTE-- dictionary for color assignment#
Color = {
     "ETF":          "#7C6FF7",
    "Fixed Income": "#38BFA1",
    "bg":           "#F8F7FF",
    "card":         "#FFFFFF",
    "grad_start":   "#6A5ACD",
    "grad_end":     "#38BFA1",
    "text_dark":    "#2D2B55",
    "text_muted":   "#7B7B9A",
    "border":       "#E2E0F0",
    "row_even":     "#F3F0FF",
    "row_odd":      "#FFFFFF"
}

#Helpers 
def filter_df(years, assets):
    d=df.copy()
    if years:
        d = d[d["Year"].isin(years)]#keeps rows where selected year is in the hyear column of the dataframe
    if assets:
        d = d[d["AssetClass"].isin(assets)]#keeps rows where selected asset class is in the asset column of the dataframe
    return d

def base_layout(title):
    return dict(
        title=dict(text=title,font=dict(size=15,color=Color["text_dark"],family="Segoe UI, sans-serif"),x=0.01),
        paper_bgcolor=Color["card"],
        plot_bgcolor=Color["bg"],
        font=dict(family="Segoe UI, sans-serif",color=Color["text_muted"],size=11),
        legend=dict(orientation="h",y=-0.2,x=0.5,xanchor="center",
                    bgcolor="rgba(0,0,0,0)",font=dict(size=12)),
            margin=dict(l=50,r=20,t=50,b=70),
            xaxis=dict(showgrid=False, tickangle=-40, tickfont=dict(size=10)),
        yaxis=dict(gridcolor=Color["border"], gridwidth=1, tickformat=","),
        hovermode="x unified",
)
#this part of the code calculates monthly total for each asset class and draws a line chart using my custom theme
def volume_chart(d):#plotly line chart showing monthly trading volume for ETFs and Fixed Income products
    #grouping and summarizing the data,sum by trading volume then convert back to dataframe and sort by month
    monthly = (d.groupby(["Month", "AssetClass"])["Volume"]
                .sum().reset_index().sort_values("Month"))
    fig = go.Figure()#creates a blank plotly chart
    for asset in ["ETF", "Fixed Income"]:
        sub = monthly[monthly["AssetClass"] == asset]#filter data for each asset class
        if sub.empty:#skip empty rows to avoid errors when plotting
            continue
        color = Color[asset]
        fill = "rgba(124,111,247,0.08)" if asset == "ETF" else "rgba(56,191,161,0.08)"
        fig.add_trace(go.Scatter(#adds a line trace to the plotly figure
            x=sub["Month"], y=sub["Volume"],
            mode="lines+markers", name=asset,#shows both lines and markers on the line
            line=dict(color=color, width=2.5, shape="spline"),
            marker=dict(size=6, color=color),
            fill="tozeroy", fillcolor=fill,#same color with added transparency for area fill under the line
        ))
    fig.update_layout(**base_layout("Monthly Trading Volume"))
    return fig
#this part of the code calculates monthly total settlement value for each asset class and draws a bar chart using my custom theme
def settlement_chart(d):
    monthly = (d.groupby(["Month", "AssetClass"])["SettlementValue"]
                .sum().reset_index().sort_values("Month"))
    fig = go.Figure()
    for asset in ["ETF", "Fixed Income"]:
        sub = monthly[monthly["AssetClass"] == asset]
        if sub.empty:
            continue
        fig.add_trace(go.Bar(
            x=sub["Month"], y=sub["SettlementValue"],
            name=asset, marker_color=Color[asset], opacity=0.85,
        ))
    fig.update_layout(**base_layout("Monthly Settlement Value"), barmode="group")
    return fig
#this part of the code calculates yearly total for each asset class and draws a bar chart using my custom theme
def yearly_chart(d):
    yearly = (d.groupby(["Year", "AssetClass"])["Volume"]
               .sum().reset_index())
    fig = go.Figure()
    for asset in ["ETF", "Fixed Income"]:
        sub = yearly[yearly["AssetClass"] == asset]
        if sub.empty:
            continue
        fig.add_trace(go.Bar(
            x=sub["Year"].astype(str), y=sub["Volume"],
            name=asset, marker_color=Color[asset], opacity=0.85,
        ))
    fig.update_layout(**base_layout("Yearly Volume Comparison"), barmode="group")
    return fig
#this part of the code calculates total volume, total settlement value, trade count and average deal size for each asset class and formats the results into a summary table
def summary_table(d):
    grp = (d.groupby("AssetClass")
            .agg(Total_Volume=("Volume", "sum"),
                 Total_Settlement=("SettlementValue", "sum"),
                 Trade_Count=("Volume", "count"))
            .reset_index())
    grp["Avg_Deal"] = grp["Total_Settlement"] / grp["Trade_Count"]
    grp.columns = ["Asset Class", "Total Volume",
                   "Total Settlement (N)", "Trade Count", "Avg Deal Size (N)"]
    grp["Total Volume"]  = grp["Total Volume"].apply(lambda x: f"{x:,.0f}")
    grp["Trade Count"]   = grp["Trade Count"].apply(lambda x: f"{x:,.0f}")
    grp["Total Settlement (N)"] = grp["Total Settlement (N)"].apply(lambda x: f"N{x:,.2f}")
    grp["Avg Deal Size (N)"]    = grp["Avg Deal Size (N)"].apply(lambda x: f"N{x:,.2f}")
    return grp
#this function creates a styled card component for displaying content in a visually appealing way.
def card(children, style=None):
    base = {
        "background": Color["card"],
        "borderRadius": "16px",
        "padding": "24px",
        "boxShadow": "0 4px 20px rgba(106,90,205,0.10)",
        "border": f"1px solid {Color['border']}",
        "marginBottom": "20px",
    }
    if style:
        base.update(style)
    return html.Div(children, style=base)

#--STEP 3-LAYOUT--#
all_years  = sorted(df["Year"].unique())
all_assets = sorted(df["AssetClass"].unique())
 
app = Dash(__name__)
app.title = "Fixed Income & ETF Dashboard"
 
app.layout = html.Div(
    style={"background": Color["bg"], "minHeight": "100vh",
           "fontFamily": "Segoe UI, sans-serif"},
    children=[
    #HEADER
     html.Div(style={
            "background": f"linear-gradient(135deg, {Color['grad_start']} 0%, {Color['grad_end']} 100%)",
            "padding": "32px 40px 28px", "color": "white",
        }, children=[
            html.H1("Fixed Income & ETF Dashboard",
                    style={"margin": 0, "fontSize": "26px", "fontWeight": "700"}),
            html.P("Trade Volume & Settlement Value Analysis",
                   style={"margin": "6px 0 0", "opacity": "0.85", "fontSize": "14px"}),
        ]),
    #FILTERS
     html.Div(style={"padding": "24px 40px 0"}, children=[
            card([
                html.Div(style={"display": "flex", "gap": "32px", "flexWrap": "wrap",
                                "alignItems": "flex-end"}, children=[
                    html.Div([
                        html.Label("YEAR", style={
                            "fontSize": "11px", "fontWeight": "600",
                            "color": Color["text_muted"], "letterSpacing": "0.08em",
                            "marginBottom": "8px", "display": "block"}),
                        dcc.Dropdown(
                            id="year-filter",
                            options=[{"label": str(y), "value": y} for y in all_years],
                            value=all_years, multi=True,
                            style={"minWidth": "300px", "fontSize": "13px"},
                            placeholder="All years",
                        ),
                    ]),
                html.Div([
                        html.Label("ASSET CLASS", style={
                            "fontSize": "11px", "fontWeight": "600",
                            "color": Color["text_muted"], "letterSpacing": "0.08em",
                            "marginBottom": "8px", "display": "block"}),
                        dcc.Dropdown(
                            id="asset-filter",
                            options=[{"label": a, "value": a} for a in all_assets],
                            value=all_assets, multi=True,
                            style={"minWidth": "280px", "fontSize": "13px"},
                            placeholder="All asset classes",
                        ),
                    ]),
                ]),
            ]),
        ]),
        #BODY
        html.Div(style={"padding": "0 40px 40px"}, children=[
 
            # Summary table
            card([
                html.H3("Summary Statistics",
                        style={"margin": "0 0 16px", "fontSize": "16px",
                               "color": Color["text_dark"], "fontWeight": "600"}),
                html.Div(id="summary-table"),
            ]),
 
            # Two charts side by side
            html.Div(style={"display": "grid",
                            "gridTemplateColumns": "1fr 1fr", "gap": "20px"}, children=[
                card([dcc.Graph(id="volume-chart",    config={"displayModeBar": False})]),
                card([dcc.Graph(id="settlement-chart", config={"displayModeBar": False})]),
            ]),
 
            # Full-width yearly chart
            card([dcc.Graph(id="yearly-chart", config={"displayModeBar": False})]),
        ]),
    ],
)

#--STEP 4: Callbacks--#
@app.callback(
    Output("summary-table",    "children"),
    Output("volume-chart",     "figure"),
    Output("settlement-chart", "figure"),
    Output("yearly-chart",     "figure"),
    Input("year-filter",  "value"),
    Input("asset-filter", "value"),
)
def update(years, assets):
    d = filter_df(years, assets)
 
    tbl_data = summary_table(d)
    table = dash_table.DataTable(
        data=tbl_data.to_dict("records"),
        columns=[{"name": c, "id": c} for c in tbl_data.columns],
        style_header={
            "backgroundColor": Color["grad_start"],
            "color": "white", "fontWeight": "600", "fontSize": "13px",
            "textAlign": "center", "border": "none", "padding": "12px 10px",
        },
        style_cell={
            "textAlign": "center", "fontSize": "13px",
            "color": Color["text_dark"], "padding": "10px 12px",
            "border": f"1px solid {Color['border']}",
            "fontFamily": "Segoe UI, sans-serif",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"},  "backgroundColor": Color["row_odd"]},
            {"if": {"row_index": "even"}, "backgroundColor": Color["row_even"]},
            {"if": {"column_id": "Asset Class"},
             "fontWeight": "600", "color": Color["grad_start"]},
        ],
        style_table={
            "borderRadius": "12px", "overflow": "hidden",
            "border": f"1px solid {Color['border']}",
        },
    )
    return table, volume_chart(d),settlement_chart(d), yearly_chart(d)

#--STEP 5: Run the app--#
if __name__ == "__main__":
    print("\nDashboard ready! Open http://127.0.0.1:8050 in your browser\n")
    app.run(debug=True)