import plotly.express as px
import pandas as pd
df=pd.DataFrame ({
    'score':[75,60,80,89,90],
    'grade':['B','B','A','A','A']
})
fig=px.box(df,x='grade', y='score',points='all',title='score distribution')
fig.show()