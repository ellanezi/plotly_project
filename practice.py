import plotly.express as px
import pandas as pd
df=pd.DataFrame({
    'Score':[45, 50, 60, 70, 85, 90, 55, 65, 75, 80],
    'Passed': ['No','No','Yes','Yes','Yes','Yes','No','Yes','Yes','Yes']
})
fig=px.histogram(df, x='Score',nbins=5,histnorm='percent',title='Distibution of student scores',color='Passed')
fig.show()