import pandas as pd
import numpy as np
print("Welcome To The Rollercoaster\n")
name=input("what is your name?\n")
print("hello " + name)
height=int(input("Please enter your height in cm?\n"))
bill=0
age=int(input("Please enter your age\n"))
if height>=120:
    print("you can ride")
    if age<=12:
     bill=7
     print("Child tickets are $7")
    elif age<=18:
      bill=10
      print("Youth tickets are $10")
    elif age>= 45 and age<=55:
       bill=0
       print("tickets are free")
    else:
      bill=12
      print("Adult tickets are $12")

    photo=input("do you want a photo taken type Y for yes and N for no\n")
    if photo =="Y":
      bill+=3
      print(f"Your bill is ${bill}")
    else:
      print(f"Your bill is ${bill}")
else:
       print("Too short,sorry maybe next time.")


