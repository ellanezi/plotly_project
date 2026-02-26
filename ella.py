import pandas as pd
import numpy as np
print("welcome to the rollercoaster")
name=input("what is your name?\n")
print("hello " + name)
height=int(input("What is your height in cm?\n"))
if height>120:
    print("you can ride, have fun")
else:
    print("Sorry maybe next time")
 
number=int(input("Enter a number\n"))

if number%2==0:
    print("Even")
else:
    print("Odd")
