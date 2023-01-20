import math
import random
import string
import os
import time

global key

def encrypt(message, key):
    encrypted = ""
    for i in range(len(message)):
        if message[i] == " ":
            encrypted += " "
        else:
            encrypted += chr((ord(message[i]) + key - 97) % 26 + 97)
    return encrypted

def decrypt(message, key):
    decrypted = ""
    for i in range(len(message)):
        if message[i] == " ":
            decrypted += " "
        else:
            decrypted += chr((ord(message[i]) - key - 97) % 26 + 97)
    return decrypted

def scramble_key(key : str):
    #converts string key to int
    key_int = 0
    operators = ["+", "**", "*", "//", "%", "-"]
    key_eval = "0"
    for i in range(len(key)):
        key_eval += operators[i%int(len(operators))] + str(ord(key[i]))
    key_int = int(eval(key_eval))
    return key_int

def key_strength(key, verbose = False):
    if(scramble_key(key) < 10000):
        return "Weak" if verbose == False else "Weak (" + str(len(str(scramble_key(key)))) + ")"
    elif(scramble_key(key) < 100000):
        return "Medium" if verbose == False else "Medium (" + str(len(str(scramble_key(key)))) + ")"
    else:
        return "Strong" if verbose == False else "Strong (" + str(len(str(scramble_key(key)))) + ")"

def save_password(name, password, key):
    with open("./passwords.csv", "a") as f:
        f.write(name + "," + encrypt(password, key) + "\n")
        

def read_passwords(key):
    #passwords are stored in a csv file with the name of the password and the encrypted password
    names = []
    passwords = []
    with open("./passwords.csv", "r") as f:
        for line in f:
            line = line.split(",")
            names.append(line[0])
            passwords.append(decrypt(line[1], key))
    return names, passwords

def list_passwords(key):
    names, passwords = read_passwords(key)
    #print out the names and passwords as ascii tables
    print("Name".ljust(20) + "Password")
    for i in range(len(names)):
        print(names[i].ljust(20) + passwords[i])
    
    

def search_passwords(s, key):
    names, passwords = read_passwords(key)
    names = [x.lower() for x in names]
    names, passwords = (list(t) for t in zip(*sorted(zip(names, passwords)))) # sort by names
    
    #assume passwords are sorted by name
    #replace names with int values

    names_int = []
    for i in range(len(names)):
        names_int.append(0)
        for j in range(len(names[i])):
            j = len(names[i]) - j - 1
            names_int[i] += ord(names[i][j]) * j
    
    s_int = 0
    for i in range(len(s)):
        i = len(s) - i - 1
        s_int += ord(s[i]) * i

    def _binary_search(arr, search):
        if len(arr) == 0:
            return False
        if(len(arr) < 10):
            return arr
        mid = len(arr) // 2
        if arr[mid] > search:
            return _binary_search(arr[:mid], search)
        else:
            return _binary_search(arr[mid+1:], search)
    
    print("Name".ljust(20) + "Password")
    for i in _binary_search(names_int, s_int):
        print(names[names_int.index(i)].ljust(20) + passwords[names_int.index(i)])
            



    
    



def main():
    global key
    print("[S]ave a password, [V]iew passwords?, s[E]arch passwords, [R]eenter key or [Q]uit?")
    choice = input("Choice: ")
    if choice.lower() == "s":
        name = input("Name for new Password!: ")
        print("Please enter the password you would like to save.")
        password = input("Password: ")
        save_password(name, password, key)
        print("Password saved!")
        main()
    elif choice.lower() == "v":
        print("Here are your passwords:")
        list_passwords(key)
        main()
    elif choice.lower() == "e":
        print("Please enter the name of the password you would like to search for.")
        name = input("Name: ")
        search_passwords(name, key)
        main()
    elif choice.lower() == "q":
        print("Goodbye!")
        exit()
    elif choice.lower() == "r":
        print("Please enter a key to encrypt your passwords with.")
        key = input("Key: ")
        print("Your key is " + key_strength(key, True))
        key = scramble_key(key)
        main()
    else:
        main()
    




if __name__ == "__main__":
    print("Welcome to the password manager!")
    print("Please enter a key to encrypt your passwords with.")
    key = input("Key: ")
    print("Your key is " + key_strength(key, True))
    key = scramble_key(key)
    main()