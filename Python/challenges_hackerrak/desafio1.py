#!/bin/python3


n = int(input("Ingrese un numero"))

def challenge(n):
    if n%2 != 0:
        print("Weird")
    elif n%2 ==0 and n>=2 and n <=5:
        print("Not Weird")
    elif n%2 ==0 and n>=6 and n<=20:
        print("Weird")
    elif n%2 ==0 and n >20:
        print("Not Weird")            
 
challenge(n)     
