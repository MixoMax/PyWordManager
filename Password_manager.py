import math
import csv
import random
import string
import pyperclip


global key

#TODO:
# OO function for ascii table



def encrypt(message : (str), key : (int)):
    #key is a 1e256 int
    chars = []
    for i in range(len(message)):
        chars.append(ord(message[i]))
    
    chars_normal = []
    for i in range(len(chars)):
        chars_normal.append(int(_normalize_key(chars[i], output_len=len(str(key)))))

    chars_encrypted = []
    for i in range(len(chars_normal)):
        temp = (chars_normal[i] ^ key)
        temp = _normalize_key(temp, output_len=len(str(key)))

        chars_encrypted.append(temp)


    def _special_xor(a : int, b : int, s : bool = False):
        #special xor function that returns the number of 1s in the xor of two numbers
        a,b = str(a), str(b)
        if len(a) != len(b):
            print(len(a), len(b))
            return False
        string = ""
        if a[0] == "-" and b[0] == "-":
            a = a[1:]
            b = b[1:]
            for i in range(len(a)):
                string += "1" if a[i]>b[i] else "0"
        elif a[0] == "-":
            a = a[1:]
            for i in range(len(a)):
                string += "1" if a[i]>b[i] else "0"
        elif b[0] == "-":
            b = b[1:]
            for i in range(len(b)):
                string += "1" if b[i]>a[i] else "0"
        else:
            for i in range(len(a)):
                string += "1" if a[i]>b[i] else "0"
        return string.count("1") if s else string.count("0")
    
    output = ""
    for i in range(len(chars_encrypted)):
        output += chr(_special_xor(chars_encrypted[i], key, s=True))
    
    print(output)
    print([ord(i) for i in output])
    return output


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
        
    
    
    




def decrypt(message, key):
    return False

def scramble_key(key : str):
    #converts string key to int
    key_int = 13
    operators = ["+", "**", "*", "//", "%", "-", "**", "+", "*", "-"]
    key_eval = "0"
    for i in range(len(key)):
        key_eval += operators[i%int(len(operators))] + str(ord(key[i]))
    key_int = int(eval(key_eval))

    key = _normalize_key(str(key_int), 256) #normalize key to 256 characters
    #NOTE: average key length before normalizing is ~ 150 < key length < 300, after normalizing is always 256, so the recursion pattern is not too noticeable
    return key

def key_strength(key, verbose = False):
    temp = key
    temp = str(scramble_key(temp))
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


def save_password(name : (str), password : (str), key):
    #write password to csv file
    encrypted = encrypt(password, key)
    print(encrypted)
    f = open("./passwords.csv", "a", newline = "")
    csv.writer(f).writerow([name, encrypted])
        

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
    
def _can_be_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

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

    



            

    



def main():
    global key
    print("Welcome to the password manager!")
    print("Please enter a key to encrypt your passwords with.")
    key = input("Key: ")
    print("Your key is " + key_strength(key, True))
    key = scramble_key(key)
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
    

def _clear_csv():
    with open("./passwords.csv", "w", newline = "") as f:
        csv.writer(f).writerows([])



def QATest():
    _clear_csv()
    key = scramble_key("Auadf3wedfgsdgfeas")
    print(len(str(key)))
    C = 100
    for i in range(C):
        save_password("test", "test", key)

    if len(read_passwords(key)[0]) != C: #test save_password and read_passwords for quantity
        print("QA Test failed for save_password and read_passwords")
        exit()
    print("QA Test passed. (1)")

    if read_passwords(key)[0][0] != "test": #test save_password and read_passwords for quality
        print("QA Test failed for save_password and read_passwords")
        exit()
    print("QA Test passed. (2)")

    if read_passwords(key)[1][0] != "test": #test save_password and read_passwords for quality
        print("QA Test failed for save_password and read_passwords")
        print(read_passwords(key)[1][0])
        exit()
    print("QA Test passed. (3)")

    delete_password(1, key, silent=True)
    if len(read_passwords(key)[0]) != C-1: #test delete_password
        print("QA Test failed for delete_password")
        print(read_passwords(key))
        exit()
    print("QA Test passed. (4)")

    if decrypt(read_passwords(key)[1][0], key) != "test": #test decrypt
        print("QA Test failed for decrypt (5)")
        print(read_passwords(key)[1][0])
        print(decrypt(read_passwords(key)[1][0], key))
        exit()
    print("QA Test passed. (5)")

    if decrypt(encrypt("test", key), key) != "test": #test encrypt and decrypt function parity
        print("QA Test failed for encrypt and decrypt function parity")
        exit()
    print("QA Test passed. (6)")


key = "MixoMax"
print(key)
key = scramble_key(key)
print(len(str(key)), "\t key len after scramble\n" )

encrypt("Aufessen", int(key))
