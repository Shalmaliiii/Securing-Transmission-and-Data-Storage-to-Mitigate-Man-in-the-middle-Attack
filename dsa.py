import math  
import random 
from hashlib import sha256
 
prime_num = [ 
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 
    71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 
    151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 
    233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 
    317, 331, 337, 347, 349 ]

def primalityTest(n):  
    while True: 
        number = random.randrange(2**(n-1)+1, 2**n - 1)
        for i in prime_num:
            if number % i == 0 and i**2 <= number: break
        else: 
            return number 

def MillerRabinPassed(num):
    d = num-1
    count = 0
    while d % 2 == 0:
        d >>= 1
        count += 1
    def trials(round_tester):
        if pow(round_tester, d, num) == 1:
            return False
        for i in range(count):
            if pow(round_tester, 2**i * d, num) == num-1:
                return False
        return True
    for _ in range (20):
        if trials(random.randrange(2, num)): return False
    return True

def power(x, y, p):
	res = 1
	x = x % p
	while (y > 0):
		if (y & 1): res = (res * x) % p
		y = y >> 1 
		x = (x * x) % p
	return res

def findPrimefactors(s, n) :
	while (n % 2 == 0) :
		s.add(2)
		n = n // 2
	for i in range(3, int(math.sqrt(n)), 2):
            while (n % i == 0):
                s.add(i)
                n = n // i
	if (n > 2) :
		s.add(n)

def findPrimitive(n) :
	s = set()
	phi = n - 1
	findPrimefactors(s, phi)
	for r in range(2, phi + 1):
		flag = False
		for it in s:
			if (power(r, phi // it, n) == 1):
				flag = True
				break
		if (flag == False):
			return r
	return -1

def extendedEuclidean(a, b):
    if a == 0: return (b, 0, 1)
    else:
        g, y, x = extendedEuclidean(b % a, a)
        return (g, x - (b // a) * y, y)

def mod_inv(a, m):
    g, x, y = extendedEuclidean(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    else: return x % m

def generatepq():
    while True:
        bits = 12
        prime = primalityTest(bits)
        if not MillerRabinPassed(prime): 
            continue
        else:
            q = prime
            break  
    p = 2*q + 1
    i = 2
    while not MillerRabinPassed(p):
        i+=1 
        p = q*i+1   # p-1 is a multiple of q
    return p,q
    
def hash_function(message):
    return sha256(message.encode("UTF-8")).hexdigest()
 
def parameter_generation():
    p,q = generatepq()
    flag  = True 
    while(flag):
        h = random.randint(1,p-1)
        if(1<h<(p-1)):
            g=1
            while(g==1):
                g = pow(h,int((p-1)/q))%p
            flag = False
        else:
            print("Wrong entry")
    return p,q,g 

def gen_keys(p,q,g):
    x = random.randint(1,q-1)
    y = pow(g,x)%p
    return x,y  # x is the private key and y is the public key.
 
def signature(text): 
    global keys 
    p, q, g = parameter_generation()   
    keys = gen_keys(p, q, g)
    x = keys[0] # private key 
    y = keys[1] # public key
    hash = hash_function(text) #hashed using sha256
    r, s = 0, 0 
    # Signing the message
    while(not s or not r):  
        k = random.randint(1,q-1)
        r = ((pow(g,k))%p)%q    # r = (g^(k) % p) % q
        i = mod_inv(k,q)
        hashed = int(hash,16) 
        s = (i*(hashed+(x*r)))%q 
    return (p,q,g,r,s,y) # Signature is (r, s)

def verification(text,p,q,g,r,s,y):
    hash = hash_function(text)
    w = mod_inv(s,q)
    hashed = int(hash,16)
    u1 = (hashed*w)%q  
    u2 = (r*w)%q
    v = ((pow(g,u1)*pow(y,u2))%p)%q
    if(v == r):  
        # Signature is valid
        return True
    else: 
        # Signature is invalid
        return False       