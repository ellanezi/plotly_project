#choropleth graph 
import plotly.express as px
import pandas as pd
df=pd.DataFrame({
    'Country': ['United States', 'Canada', 'Mexico', 'Brazil'],
    'Population': [331000000, 38000000, 128000000, 213000000]
})
fig = px.choropleth(df,
locations='Country', #column with region names
    locationmode='country names', #tells plotly how to interpret names
        color='Population',#controls shading=(darker=bigger numbers)
            title='Population by Country')
fig.show()