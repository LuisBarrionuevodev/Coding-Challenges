import os
print("Directorio actual:", os.getcwd())

with open("cuento1.txt", "r") as file1:
    for line in file1:
        print(line)
