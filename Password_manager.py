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



def create_password(blocks, block_length, include_punctuation, name):
    print("Creating password!\n\nPlease wait...")
    possible_characters = string.ascii_letters + string.digits
    password = ""
    
    if include_punctuation:
        block_length -= 1

    for i in range(blocks):
        block = []
        for _ in range(block_length):
            block.append(random.choice(possible_characters))
        if include_punctuation:
            block.append(random.choice(string.punctuation))
        random.shuffle(block)
        password += "".join(block)
        if i != blocks -1: password += "-"
    
    save_password(name, password, key)
    print("Your password for '" + name + "' was created and saved! The password is: " + password)



    
    



def main():
    global key
    print("[S]ave a password, [V]iew passwords, [C]reate random password, s[E]arch passwords, [R]eenter key or [Q]uit?")
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
    elif choice.lower() == "c":
        blocks = 4
        block_length = 5
        include_punctuation = True


        name = input("Name for new Password!: ")
        input0 = input("How many blocks? (Between 2 and 6, default is 4): ")
        try:
            input0 = int(input0)
        except:
            input0 = None
        if type(input0) is int and input0 > 1 and input0 < 7:
            print("Block count set to " + str(input0) + ".")
            blocks = input0
        else:
            print("Block count set to default (4).")

        input1 = input("How long should each block be? (Between 3 and 10, default is 5): ")
        try:
            input1 = int(input1)
        except:
            input1 = None
        if type(input1) is int and input1 > 2 and input1 < 11:
            print("Block length set to " + str(input1) + ".")
            block_length = input1
        else:
            print("Block length set to default (5).")

        input2 = input("Include punctuation? (y/n, default is y): ")
        if input2.lower() == "n":
            print("Punctuation set to False.")
            include_punctuation = False
        else:
            print("Punctuation set to default (True).")
        create_password(blocks, block_length, include_punctuation, name)
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