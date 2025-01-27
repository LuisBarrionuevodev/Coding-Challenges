import os
print("Directorio actual:", os.getcwd())
frase=[]
with open("cuento1.txt", "r") as file1:
    for line in file1:
       frase += line.split(",")
       
           

for words in frase:
    print(words)
    print(type(words))