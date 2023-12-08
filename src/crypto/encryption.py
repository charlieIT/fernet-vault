import base64
import os
from typing import Union

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError or ModuleNotFoundError:
    print('Error loading Fernet lib. Maybe missing cryptography dependency? `python3 -m pip install cryptography`')
    exit(1)
    
            
class Encryption:
    key: bytes
    salt: Union[None, bytes]
        
    def __init__(self, key: str, salt=None):
        self.key = key.encode()
        self.salt = salt
                                
        self.digest()
                
    def digest(self):
        '''To use Fernet with passkeys the password must be run through a key derivation function'''
        if self.salt is None:
            self.salt = bytes(os.urandom(16))
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000)
        self.key = base64.urlsafe_b64encode(kdf.derive(self.key))

    def RKEY(self):
        ''''A random key'''
        return Fernet.generate_key()

    def EKEY(self):
        '''An encrypted key that will be stored and associated with the vault'''
        f = Fernet(self.key)
        return f.encrypt(self.RKEY())

    def decrypt(self, ekey):
        '''Given an encrypted key, attempt to obtain RKEY'''
        f = Fernet(self.key)
        return f.decrypt(ekey)  # RKEY

    def encrypt(self, something):
        f = Fernet(self.key)
        return f.encrypt(something.encode())
        
    def write(self, to: str):
        with open(to, 'wb') as f:
            f.write(self.salt)
            f.write(self.EKEY())
    
