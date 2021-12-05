import base64
import secrets 
import hashlib
from Crypto import Random
from tinyec import registry
from Crypto.Cipher import AES

BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]
def compress(pubKey):
    return hex(pubKey.x) + hex(pubKey.y % 2)[2:]
 
def pas():
    curve = registry.get_curve('brainpoolP256r1')
    alicePrivKey = secrets.randbelow(curve.field.n)
    bobPrivKey = secrets.randbelow(curve.field.n)
    alicePubKey = alicePrivKey * curve.g 
    bobPubKey = bobPrivKey * curve.g
    print("\nPrivate key of Alice : ", alicePrivKey)
    print("\nPrivate key of Bob : ", bobPrivKey)    
    print("\nPublic key of Alice : ", compress(alicePubKey))
    print("\nPublic key of Bob : ", compress(bobPubKey))
    Eve_alice = secrets.randbelow(curve.field.n)
    Eve_bob = secrets.randbelow(curve.field.n)
    print("\nPrivate key for Alice generated by Eve : ", alicePrivKey)
    print("\nPrivate key for Bob generated by Eve : ", bobPrivKey)
    
    Eve_alice_pub = Eve_alice * curve.g
    Eve_bob_pub = Eve_bob * curve.g
    print("\nPublic key for Alice generated by Eve : ", compress(Eve_alice_pub))
    print("\nPublic key for Bob generated by Eve : ", compress(Eve_bob_pub))

    eve3 = alicePubKey * Eve_alice
    eve4 = bobPubKey * Eve_bob

    bobPubKey = Eve_bob_pub
    alicePubKey = Eve_alice_pub

    aliceSharedKey = alicePrivKey * bobPubKey
    bobSharedKey = bobPrivKey * alicePubKey 

    print("\nShared key calculated by Alice: ", compress(aliceSharedKey))
    print("\nShared key calculated by Eve for Alice : ", compress(eve3))
    print("\nShared key calculated by Bob: ", compress(bobSharedKey))
    print("\nShared key calculated by Eve for Bob: ", compress(eve4))

    if aliceSharedKey == eve3 and bobSharedKey == eve4:
        print("\nSUCCESSFUL HACK by Eve.")
        password = compress(aliceSharedKey)
        return password
    else:
        print("\nUNSUCCESSFUL HACK by Eve.")
        print("\nMITM Prevented using ECDHE!")

def encrypt(raw):
    password = pas()
    private_key = hashlib.sha256(password.encode("utf-8")).digest()
    raw = pad(raw)
    iv = Random.new().read(AES.block_size) 
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(raw.encode('utf-8'))),password

def decrypt(enc, password):
    private_key = hashlib.sha256(password.encode("utf-8")).digest()
    enc = base64.b64decode(enc)
    iv = enc[:16]
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[16:]))

print("\nShared keys calculated by Alice and Bob and by Eve for Alice and Bob are unequal.")
pas()              