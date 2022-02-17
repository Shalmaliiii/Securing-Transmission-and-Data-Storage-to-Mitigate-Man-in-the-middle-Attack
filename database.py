import os
import cx_Oracle 

def getConnection():
    password = os.environ.get('password')
    conn = cx_Oracle.connect("SHALMALI/"+password+"@localhost:1521")
    return conn

def ifExists(name):
    conn = getConnection()
    cursor = conn.cursor() 
    query = f"SELECT COUNT(*) FROM USERS WHERE NAME = '{name}'"
    cursor.execute(query) 
    for res in cursor:
        ret = res[0] # COUNT of users
    conn.commit()  
    cursor.close()
    return ret
    
def fetchData(name):
    l = []
    conn = getConnection()
    cursor = conn.cursor()
    query = f"SELECT * FROM USERS WHERE NAME = '{name}'"
    cursor.execute(query)
    for res in cursor:
        l.append(res[0]) # name
        l.append(res[1]) # salt
        l.append(res[2]) # key
    conn.commit()
    cursor.close()
    return l

def insert(name,salt,key):
    conn = getConnection()
    cursor = conn.cursor()
    query = f"INSERT INTO USERS VALUES ('{name}','{salt}','{key}')" # insert name, salt and key in USER database
    cursor.execute(query)
    conn.commit()
    cursor.close()
    print("User Database updated.") 

def Remove_User(name):
    conn = getConnection() 
    cursor = conn.cursor()
    query1 = f"DELETE FROM USERS WHERE NAME = '{name}'"
    query2 = f"DELETE FROM DATABASE WHERE NAME = '{name}'" # remove user from both databases
    cursor.execute(query1)
    cursor.execute(query2)
    conn.commit()
    cursor.close() 

def Store_message(name, message, sharedkey, sign):
    conn = getConnection()
    cursor = conn.cursor()
    query = f"INSERT INTO DATABASE VALUES ('{name}','{message}','{sharedkey}','{sign[0]}','{sign[1]}','{sign[2]}','{sign[3]}','{sign[4]}','{sign[5]}')"
    cursor.execute(query)
    conn.commit()
    cursor.close()
    print("\nEncrypted data added to the Database successfully!")  

def Retrieve_message(name):
    l = [] 
    conn = getConnection() 
    cursor = conn.cursor()
    query = f"SELECT * FROM DATABASE WHERE NAME = '{name}'" 
    cursor.execute(query)
    for res in cursor:
        l.append(res) 
    conn.commit()
    cursor.close()
    return l                

def Delete_message(name,r,s):
    conn = getConnection() 
    cursor = conn.cursor()
    query = f"DELETE FROM DATABASE WHERE NAME = '{name}' AND R = '{r}' AND S = '{s}'"
    cursor.execute(query)
    conn.commit()
    cursor.close() 
