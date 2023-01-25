import math
import csv
import random
import string
import pyperclip
import os


os.chdir(os.path.dirname(os.path.abspath(__file__)))


global key

#TODO:
# OO function for ascii table



def encrypt(message : (str), key : (int)):
    keymod = key % 256
    keymod = keymod if keymod!= 0 else 255
    backup_key = scramble_key(str(key + 1)[192:], False) % 256


    chars = []

    key_arr = [0 for i in range(len(message))]

    for i in range(len(message)):
        temp = ((ord(message[i]) + keymod) % 256)
        if chr(temp) not in [",", " ", "", ";", "\t", "\n", "\r", "Î"]:
            chars.append(chr(temp))
            key_arr[i] = 0
        else:
            temp = ((ord(message[i]) + backup_key) % 256)
            chars.append(chr(temp))
            key_arr[i] = 1
        

    output = (str("".join(chars)), str("".join([str(i) for i in key_arr])))

    return output
    


def decrypt(message : str, key : int):
    keymod = key % 256
    keymod = keymod if keymod!= 0 else 255
    backup_key = scramble_key(str(key + 1)[192:], False) % 256

    key_arr = message[message.rfind(";")+1:]
    message = message[:message.rfind(";")]

    for key in key_arr:
        if key not in ["0", "1", 0, 1]:
            print("ka", key_arr)
        else:
            key_arr = [int(i) for i in key_arr]


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


def key_strength(key, verbose = False):
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


def random_string(length : int = -1):
    if length == -1:
        length = random.randint(5, 256)
    
    temp = "".join([random.choice(string.ascii_letters + string.digits) for i in range(length)])
    return temp.replace("Î", "")


def save_password(name : (str), password : (str), key):
    #saves a password to the csv file
    name, name_key_arr = encrypt(name, key)
    password, pswd_key_arr = encrypt(password, key)
    text = password + "Î" + random_string()
    tup = (name, text)
    print("w", tup)
    with open("passwords.csv", "a") as f:
        writer = csv.writer(f)
        writer.writerow(tup)


        

def read_passwords(key):
    with open("passwords.csv", "r") as f:
        reader = csv.reader(f)
        text = []
        names = []
        for tup1 in reader:
            print("r", tup1)
            text.append(tup1[1])
            names.append(tup1[0])
    
    for i in range(len(text)):
        names[i] = decrypt(names[i], key)
        password = text[i][:text[i].find("Î")]
        text[i] = decrypt(password, key)
    return names, text




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
        _get_key()
        main()
    else:
        main()

def _get_key():
    global key
    print("Welcome to the password manager!")
    print("Please enter a key to encrypt your passwords with.")
    key = input("Key: ")
    print("Your key is " + key_strength(key, True))
    key = scramble_key(key)
    return key

def _single_digit_key(key):
    global single_digit_key

    single_digit_key = str(key)[int((int(str(key)[-1])/10) * len(str(key)))]

def test(c):
    global key
    c += 1
    ran_key = "".join([random.choice(string.ascii_letters + string.digits) for i in range(10)])
    ran_message = "".join([random.choice(string.ascii_letters + string.digits) for i in range(10)])


    key = scramble_key(ran_key)

    encrypted_password = encrypt(ran_message, key)
    decrypted_password = decrypt(encrypted_password, key)

    if ran_message == decrypted_password and encrypted_password != decrypted_password:
        #print(str(c).ljust(8), ran_message.ljust(20), encrypted_password.ljust(20), decrypted_password.ljust(20))
        a = 1
    else:
        print("Passwords do not match!")
        print("key:\t", ran_key)
        print("input:\t", ran_message)
        print("encrypted:\t", encrypted_password)
        print("decrypted:\t", decrypted_password)
        quit()
    
    return c


TEST_MODE = False

if __name__ == "__main__":
    if not TEST_MODE:
        _get_key()

        main()
    elif TEST_MODE:
        c = test(0)
        while c < 1_000_000:
            c = test(c)
            if c % 1000 == 0:
                print(str(c).ljust(8), end="\r", flush=True)