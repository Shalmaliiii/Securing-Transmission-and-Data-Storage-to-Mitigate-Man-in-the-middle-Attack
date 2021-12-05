import os
import dsa
import time
import base64
import secrets 
import hashlib 
import binascii 
import database
from Crypto import Random
from tinyec import registry 
from Crypto.Cipher import AES
  
BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]
def compress(pubKey):
    return hex(pubKey.x) + hex(pubKey.y % 2)[2:]

def ecdhe():
    curve = registry.get_curve('brainpoolP256r1') # equation - y^2= x^3 + a*x + b mod p
    PrivKey1 = secrets.randbelow(curve.field.n) # alpha
    PrivKey2 = secrets.randbelow(curve.field.n) # beta
    PubKey1 = PrivKey1 * curve.g # alpha * G
    PubKey2 = PrivKey2 * curve.g # beta * G
    SharedKey1 = PrivKey1 * PubKey2 # alpha * beta * G
    SharedKey2 = PrivKey2 * PubKey1 # alpha * beta * G
    print("\nExchanging keys using ECDHE . . .")
    time.sleep(1) 
    if SharedKey1 == SharedKey2: 
        password = compress(SharedKey1)
        print("\nThe shared keys are equal.")
        print("\nECDHE has successfully been implemented!")
    else:
        print("Shared keys are not equal.")
        exit() 
    return password

def encrypt(raw): 
    password = ecdhe()
    send = base64.b64encode(password.encode("utf-8"))
    private_key = hashlib.sha256(send).digest()
    raw = pad(raw)  
    print("\nEncrypting data using AES . . .")
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    encrypted_data = base64.b64encode(iv + cipher.encrypt(raw.encode('utf-8')))
    time.sleep(1) 
    print("\nData Encrypted successfully using AES!")    
    print("\nCreating Digital Signature . . .")
    sign = dsa.signature(str(encrypted_data)) 
    time.sleep(1) 
    return encrypted_data , password , sign 
                    
def decrypt(enc, password,p,q,g,r,s,y):
    enc = base64.b64decode(enc)
    isvalid = dsa.verification(str(enc),p,q,g,r,s,y) 
    if isvalid:
        send = base64.b64encode(password.encode("utf-8"))
        private_key = hashlib.sha256(send).digest()
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(private_key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc[16:])) 
    else:
        print("Signature invalid.") 

def display_data(name, signal):
    print("\n----------------------- Displaying the Data -----------------------\n")
    k = 0 
    l = database.Retrieve_message(name)
    for i in l:
        k+=1
        decrypted_message = decrypt(i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8]).decode('utf-8')
        print(f'{k}] ',decrypted_message)
    print()
    print("------------------------------------------------------------------") 
    if signal :
        return k

def SendRetrieve(name):
    while True:
        print("\nChoose desired operation.\n0. Send data\n1. Retrieve data\n2. Delete existing data\n3. Delete account\n4. Exit")
        choice = int(input("\nChoice : "))
        if not choice : 
            plaintext = input("Text to send : ")
            encrypted_message, sharedkey, l = encrypt(plaintext)
            print("\nEncrypted message : ",encrypted_message)
            database.Store_message(name, binascii.hexlify(base64.b64encode(encrypted_message)).decode('utf-8'), sharedkey, l)
        elif choice == 1:
            display_data(name,0)
        elif choice == 2:
            a = display_data(name,1)
            if not a :
                print(f"No data found in {name}'s database.")
                continue
            index = int(input("Index of message to be deleted : "))
            if index < 1 or index > a:
                print("Invalid Delete Query, choose again!")
            else:
                l = database.Retrieve_message(name)
                database.Delete_message(name,l[index-1][6], l[index-1][7])
                print(f"\nData corresponding to index {index} deleted successfully!")
        elif choice == 3:
            if confirm_password(name, 1):
                database.Remove_User(name)
                print(f"[{name}] Account Deleted !")
                break
            else:
                print("Incorrect password. Try again.") 
        else: 
            break       

def isvalid(name):
    if len(name.split(" ")) == 1 and name.lower() == name:
        return True
    print("Invalid username.")
    return False

def confirm_password(name,signal):
    string = ["Password : ", "Confirm Password : "] [signal]
    l = database.fetchData(name)
    name, salt, key = l[0],l[1],l[2]
    salt, key = base64.b64decode(salt), base64.b64decode(key)
    new_key = hashlib.pbkdf2_hmac('sha256', input(string).encode('utf-8'), salt, 100000)
    if new_key == key:
        return True
    return False

def Login(name): 
    if database.ifExists(name) == 0:
        print("Please Sign up to Login.") 
        return False  
    iscorrect = confirm_password(name,0) 
    if iscorrect:
        print("Login successful ! ")         
    else: 
        print("Incorrect password. Try again.") 
        return False 
    return True  

def Signup(name):
    if database.ifExists(name):
        print("Username already exists!") 
        return False   
    salt = os.urandom(32) 
    key = hashlib.pbkdf2_hmac('sha256', input("Password : ").encode('utf-8'), salt, 100000)
    database.insert(name ,binascii.hexlify(base64.b64encode(salt)).decode('utf-8'),binascii.hexlify(base64.b64encode(key)).decode('utf-8'))
    print("Signed up successfully !")
    return True

while True:
    print("\nChoose desired operation.\n1. Sign up\n2. Login\n3. Exit\n")
    ch = int(input("Choice : "))
    if ch==1:
        print("A username must not contain any spaces and no uppercase letters are allowed.")
        name = input("Enter a username : ")
        if isvalid(name) and Signup(name):
            SendRetrieve(name)
        continue
    if ch==2:
        name = input("Username : ")
        if isvalid(name) and Login(name):
            SendRetrieve(name)
        continue
    else:
       break       