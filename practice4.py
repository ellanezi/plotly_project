#scattered plots map 
import plotly.express as px
import pandas as pd
df=pd.DataFrame({
    'City': ['New York', 'Los Angeles', 'Chicago'],
    'Lat': [40.7128, 34.0522, 41.8781],
    'Lon': [-74.0060, -118.2437, -87.6298],
    'Population': [8419600, 3980400, 2716000]
})
fig=px.scatter_geo(df,
    lat='Lat', 
    lon='Lon',
    size='Population',
    hover_name='City',
    title='US cities by population')#shows city when you hover over
fig.show()