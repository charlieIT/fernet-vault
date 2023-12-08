
import os
import shutil

from datetime import datetime, timedelta
from .secret import Secret
from .constants import default_dir

from ..crypto import encryption
from ..utils import sanitize_name, isvalid_name

class LockedError(Exception):
    def __init__(self, message: str='Vault is locked'):
        super().__init__(message)
        
class SecretNotFoundError(Exception):
    def __init__(self, message: str='Could not find secret'):
        super().__init__(message)

class Vault:
    
    def __init__(self, name: str, **kwargs):
        self.name = sanitize_name(name)
        self.dir = kwargs.get('dir', default_dir(name))
        # :TODO Improve configurability
        self.cfg = os.path.join(self.dir, "{}.cfg".format(self.name))
        self.secrets = os.path.join(self.dir, "secrets/")
        self._islocked = True
        
    def initialize(self, crypto: encryption.Encryption):
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)
        if not os.path.exists(self.cfg):
            crypto.write(self.cfg)
        if not os.path.exists(self.secrets):
            os.mkdir(self.secrets)
    
    def lock(self):
        self._islocked = True
        del self.crypto

    def unlock(self, mkey: str) -> bool:
        with open(self.cfg, 'rb') as f:
            salt = f.read(16)
            ekey = f.read()
            try:
                crypto = encryption.Encryption(mkey, salt)
                crypto.decrypt(ekey)
                self.crypto = crypto
            except Exception:
                return False
        
            self._opened = datetime.now()
            self._islocked = False
            return True

    def isunlocked(self) -> bool:
        if not self._islocked:
            if self._opened + timedelta(minutes=10) > datetime.now():
                return True
        
        self.lock()
        return False

    def store(self, secret: Secret) -> bool:
        if not self.isunlocked():
            raise LockedError()

        # :TODO improve exit return for clarity
        if not isvalid_name(secret.name):
            return False
        
        with open(self.secret_file(secret.name), 'wb') as f:
                f.write(self.crypto.encrypt(str(secret)))
                f.close()
        return True
    
    def read(self, secret: str) -> Secret:
        if not self.isunlocked():
            raise LockedError()
        
        if not self.has_secret(secret):
            raise SecretNotFoundError()
        
        '''Decrypt and return a secret, given its `name`'''
        with open(self.secret_file(secret), 'rb') as f:
                d = self.crypto.decrypt(f.read())
                return Secret.load(d)
    
    def remove(self, secret: str) -> bool:
        '''Remove a secret from the filesytem'''
        if not self.isunlocked():
            return False
        if not self.has_secret(secret):
            return False
        try:
            os.remove(self.secret_file(secret))
            return True
        except OSError:
            return False
    
    def secret_file(self, name: str) -> str:
        '''Obtain a secret's file location'''
        return os.path.join(self.secrets, name)
    
    def has_secret(self, name: str) -> bool:
        return os.path.exists(self.secret_file(name))
    
    # Vaul collections
    def list(self):
        '''List secrets associated with the vault by listing the vault's secret dir'''
        return [f for f in os.listdir(self.secrets) if os.path.isfile(os.path.join(self.secrets, f))]
    
    def purge(self) -> bool:
        if not self.isunlocked():
            return False
        try:
            shutil.rmtree(self.secrets)
            shutil.rmtree(self.dir)
            return True
        except:
            raise

    # built-ins
    def __str__(self):
        return '{} @ {}'.format(self.name, str(self.dir))
    
def unlock(vault: Vault, mkey: str) -> Vault:
    '''
        Unlocks a vault and returns the unlocked vault
        
        Vault operations should only be performed after invoking `unlock`
    '''
    if vault.unlock(mkey):
        return vault
    raise LockedError()
