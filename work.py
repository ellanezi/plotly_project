import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
line_style=dict(marker=".",markersize=10,markerfacecolor="#E73195",markeredgecolor="#EC3A8D",
linestyle="solid",linewidth=3)
x=np.array([2023,2024,2025,2026])
y=np.array([15,25,30,20])
y2=np.array([5,12,10,15])
y3=np.array([2,12,6,18])
plt.plot(x,y,**line_style,color="black")
plt.plot(x,y2,**line_style,color="orange")
plt.plot(x,y3,**line_style,color="darkred")
plt.title("Class Size", fontsize=25,family="arial",fontweight="bold")
plt.show()