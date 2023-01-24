import math
import csv
import random
import string
import pyperclip
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

global key
global verbose
verbose = True

#TODO:
# OO function for ascii table
# csv handling

def encrypt(message : (str), key : (int), verbose : bool = False):
    keymod = key % 256
    keymod = keymod if keymod!= 0 else 255
    backup_key = scramble_key(str(key + 1)[192:], False) % 256


    chars = []

    key_arr = [0 for i in range(len(message))]
    for i in range(len(message)):
        temp = ((ord(message[i]) + keymod) % 256)
        if verbose: print(temp.ljust(5), "ord number")
        if chr(temp) not in [",", " ", "", ";", "\t", "\n", "\r"]:
            chars.append(chr(temp))
            key_arr[i] = 0
        else:
            temp = ((ord(message[i]) + backup_key) % 256)
            chars.append(chr(temp))
            key_arr[i] = 1

    output = str("".join(chars)) + ";" + str("".join([str(i) for i in key_arr]))

    return output

def decrypt(message : str, key : int):
    keymod = key % 256
    keymod = keymod if keymod!= 0 else 255
    backup_key = scramble_key(str(key + 1)[192:], False) % 256

    key_arr = message[message.rfind(";")+1:]
    message = message[:message.rfind(";")]

    key_arr = [int(i) for i in key_arr]
    print(key_arr)

    chars = []
    for i in range(len(message)):
        if key_arr[i] == 0:
            temp = ((ord(message[i]) - keymod) % 256)
            chars.append(chr(temp))
        else:
            temp = ((ord(message[i]) - backup_key) % 256)
            chars.append(chr(temp))
    output = "".join(chars)

    return output

def scramble_key(key : str, normal : bool = True, length : int = 256):

    #converts string key to int
    key_int = 13
    operators = ["+", "**", "*", "//", "%", "-", "**", "+", "*", "-"]
    key_eval = "0"
    for i in range(len(key)):
        key_eval += operators[i%int(len(operators))] + str(ord(key[i]))
    key_int = int(eval(key_eval))

    key = _normalize_key(str(key_int), length) if normal else key_int #normalize key to 256 characters
    #NOTE: average key length before normalizing is ~ 150 < key length < 300, after normalizing is always 256, so the recursion pattern is not too noticeable
    return int(key)

def key_strength(key, verbose : bool = False):
    temp = key
    temp = str(scramble_key(temp, False))
    if len(temp) < 50:
        if verbose:
            return "weak (" + str(len(temp)) + ")"
        else:
            return False
    elif len(temp) < 100:
        if verbose:
            return "medium (" + str(len(temp)) + ")"
        else:
            return True
    else:
        if verbose:
            return "strong (" + str(len(temp)) + ")"
        else:
            return True

def _normalize_key(key_string : str, output_len : int = 256):
    #normalizes a string to a given length using splicing or looping and returns the normalized string

    key_string = str(key_string)
    output_len = int(output_len)

    if len(key_string) == output_len:
        return key_string
    elif len(key_string) > output_len:
        key_string = key_string[:output_len]
        return key_string
    elif len(key_string) < output_len:
        key_string = key_string * math.ceil(output_len / len(key_string)) if key_string[0] != "-" else "-" +str( key_string[1:] * (math.floor(output_len / (len(key_string)))+1))
        return key_string[:output_len]
    else:
        return key_string

def save_password(name : (str), password : (str), key : int):
    #write password to csv file
    encrypted = encrypt(password, key)
    print(encrypted, "encrypted password")
    print(name, decrypt(encrypted, key), "decrypted password")
    f = open("./passwords.csv", "a")
    csv.writer(f).writerow((name, encrypted))
        

def read_passwords(key):
    #passwords are stored in a csv file with the name of the password and the encrypted password
    names = []
    passwords = []
    with open("./passwords.csv", "r") as f:
        reader = csv.reader(f)
        for row in reader:
            names.append(row[0])
            passwords.append(decrypt(row[1], key))
    return names, passwords

def list_passwords(key):
    names, passwords = read_passwords(key)
    #print out the names and passwords as ascii tables
    print("idx".ljust(5) + "Name".ljust(20) + "Password")
    print("-" * 40)
    c = 0
    pswd_array = []
    for name in names:
        c += 1
        if len(name) < 20:
            print(str(c).ljust(5) + name.ljust(20) + passwords[names.index(name)])
        else:
            for i in range(math.ceil(len(name) / 19)):
                print(str(c).ljust(5) + name[i*19:(i+1)*19].ljust(20) + passwords[names.index(name)] if i == 0 else "".ljust(5) + name[i*19:(i+1)*19].ljust(20))
        pswd_array.append(passwords[names.index(name)])
    print("-" * 40)
    print("Password idx to copy to clipboard, [R]eturn to main menu, [Q]uit, s[e]arch passwords or [D]elete password?")
    choice = input("Choice: ")
    match choice.lower():
        case "r": main()
        case "q": quit()
        case "e": search_passwords(input("Search: "), key)
        case "d": delete_password(input("Password idx to delete: "), key)

    if _can_be_int(choice) and int(choice) <= len(pswd_array):
        pyperclip.copy(pswd_array[int(choice) - 1])
        print("Password for " + names[int(choice) - 1] + " copied to clipboard.")
    
def delete_password(idx, key, silent = False):
    #deletes password from csv file by index
    if _can_be_int(idx):
        names, passwords = read_passwords(key)
        names.pop(int(idx) - 1)
        passwords.pop(int(idx) - 1)
        with open("./passwords.csv", "w", newline = "") as f:
            csv.writer(f).writerows(zip(names, passwords))
        if not silent:
            print("Password deleted.")
    else:
        print("Invalid idx." if not silent else "")

def search_passwords(s, key):
    names, passwords = read_passwords(key)
    names = [x.lower() for x in names]
    names, passwords = (list(t) for t in zip(*sorted(zip(names, passwords)))) # sort by names
    
    arr = []

    def _score(search, name):
        #returns a score for how similar two strings are
        #score += 1 for each matching character
        #score += 2 for each matching character in the same position

        #q: which way are s1 and s2 supposed to be?
        #a: s1 is the search string, s2 is the password name
        score = 0
        for i in range(len(search)):
            if search[i] == name[i]:
                score += 2
            elif search[i] in name:
                score += 1
        return score

    for name in names:
        arr += [[name, _score(s.lower(), name)]]
    arr = sorted(arr, key=lambda x: x[1], reverse=True)
    print("idx".ljust(5) + "Name".ljust(20) + "Password")
    print("-" * 40)
    c = 0
    pswd_array = []
    for i in arr:
        c += 1
        if len(i[0]) < 20:
            print(str(c).ljust(5) + i[0].ljust(20) + passwords[names.index(i[0])])
        else:
            for i in range(math.ceil(len(name) / 19)):
                print(str(c).ljust(5) + i[0][i*19:(i+1)*19].ljust(20) + passwords[names.index(i[0])] if i == 0 else "".ljust(5) + i[0][i*19:(i+1)*19].ljust(20))
        pswd_array.append(passwords[names.index(i[0])])
    print("-" * 40)
    print("Password idx to copy to clipboard, [R]eturn to main menu, [Q]uit, s[e]arch passwords or [D]elete password?")
    choice = input("Choice: ")
    match choice.lower():
        case "r": main()
        case "q": quit()
        case "e": search_passwords(input("Search: "), key)
        case "d": delete_password(input("Password idx to delete: "), key)


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


def _can_be_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    

TEST_MODE = True
    
    
def _save():
    name = input("Name for new Password!: ")
    print("Please enter the password you would like to save.")
    password = input("Password: ")
    save_password(name, password, key)
    print("Password saved!")
    main()

def _list(key):
    print("Here are your passwords:")
    list_passwords(key)
    main()

def _create():
        blocks = 4
        block_length = 5
        include_punctuation = True


        name = input("Name for new Password!: ")
        input0 = input("How many blocks? (Between 2 and 6, default is 4): ")
        input0 = int(input0) if _can_be_int(input0) else None
        
        print("Block count set to " + str(input0) + "." if type(input0) is int and input0 > 1 and input0 < 7 else "Block count set to default (4).")

        input1 = input("How long should each block be? (Between 3 and 10, default is 5): ")
        input1 = int(input1) if _can_be_int(input1) else None
        
        print("Block length set to " + str(input1) + "." if type(input1) is int and input1 > 2 and input1 < 11 else "Block length set to default (5).")

        input2 = input("Include punctuation? (y/n, default is y): ")
        input2 = False if input2.lower() == "n" else True
        print("Punctuation set to " + ("yes" if input2 else "no") + "." if type(input2) is bool else "Punctuation set to default (yes).")
        
        create_password(blocks, block_length, include_punctuation, name)
        main()
        
def _search():
    print("Please enter the name of the password you would like to search for.")
    name = input("Name: ")
    search_passwords(name, key)
    main()

def _reenter_key():
    print("Please enter a key to encrypt your passwords with.")
    key = input("Key: ")
    print("Your key is " + key_strength(key, True))
    key = scramble_key(key)
    main()

def main():
    global key
    print("[S]ave a password, [V]iew passwords, [C]reate random password, s[E]arch passwords, [R]eenter key or [Q]uit?")
    
    
    
    choice = input("Choice: ").lower()
    match choice:
        case "s": _save()
        case "v": _list(key)
        case "c": _create()
        case "e": _search()
        case "q": print("Goodbye!"); exit()
        case "r": _reenter_key()
        case _: main()
    


if __name__ == "__main__":
    print("Welcome to the password manager!")
    print("Please enter a key to encrypt your passwords with.")
    key = input("Key: ")
    print("Your key is " + key_strength(key, True))
    key = scramble_key(key)
    main()