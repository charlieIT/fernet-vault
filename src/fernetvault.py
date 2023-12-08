import argparse # Try to create a decent cli
import getpass  # Handle input password without echoing
import os
import schedule
from datetime import datetime, timedelta

from . import utils
from .models.constants import default_vault_dir, default_dir
from .models.vault import Vault, LockedError, SecretNotFoundError, unlock
from .models.secret import Secret
from .crypto import encryption
from .ui import secrets as secretsUI
from .ui import vaults as vaultsUI


def schedule_lock(vault: Vault):
    ''''Schedule  vault lock check, which also locks the vault in case vault conditions are not met'''
    span = datetime.now() + timedelta(minutes=10)
    schedule.every(1).second.until(span).do(vault.lock)
    schedule.run_all()

class Session:
    vault: Vault
    secret: str
    
    def set_vault(self, vault: Vault):
        self.vault = vault
        
    def set_secret(self, secret: str):
        self.secret = secret

def isvault(name):
    return os.path.exists(default_dir(name))

def prompt_password(prompt='Vault password: ') -> str:
    return getpass.getpass(prompt=prompt)

def cli(args: argparse.Namespace):
        
    session = Session()
    
    if not os.path.isdir(default_vault_dir):
        '''Ensure .vaults dir exists'''
        os.mkdir(default_vault_dir)
        
    # Default operations: 
    # 1. list vaults and let user chose, if none selected
    if not args.vault:
        '''No vault was selected, list vaults and allow vault selection'''
        while True:
            selected = vaultsUI.list_and_select()
            if selected:
                args.vault = selected
                return cli(args)
            
    if args.vault and not isvault(args.vault) and not args.purge:
        '''Setup a new vault to continue operations'''
        args.new = input("Create new? [(y)es/(n)o] ")
        if args.new in ['y', 'yes']:
            localkey = prompt_password()
            if not localkey == prompt_password("Confirm you vault password: "):
                exit("Password mismatch")
            
            tmp = Vault(args.vault)
            tmp.initialize(encryption.Encryption(localkey))
            del localkey
            print("Created {}".format(str(tmp)))
            del tmp
        else:
            exit(0)
            
    # authenticate to unlock the vault
    try:
        unlocked = unlock(Vault(args.vault), prompt_password('Unlock vault: '))
        if not unlocked:
            raise LockedError()
        session.vault = unlocked
        del unlocked
    except (LockedError, Exception) as err:
        utils.exit_with(err)
        
    if args.purge:
        '''Remove the vault'''
        confirmation = input("!! Please confirm vault removal: [(y)es] > ")
        if confirmation in ['y', 'yes']:
            try:
                if session.vault.purge():
                    exit("Removed {}".format(session.vault.name))
                else:
                    exit("Could not remove {}".format(session.vault.name))
            except Exception as err:
                utils.exit_with(err)
    
    # schedule_lock(session.vault)

    if args.secret:
        '''capture user selected secret from -s or --secret'''
        session.secret = utils.sanitize_name(args.secret)

        if not utils.isvalid_name(session.secret):
            exit("Invalid name provided")
            
        if args.export:
            '''Exporting a secret'''
            
            try:
                data = session.vault.read(session.secret)
                if args.export == 'stdout':
                    '''echo out the secret'''
                    print(str(data))
                else:
                    '''Try and write to specified file'''
                    try:
                        file = open(args.export, 'w')
                        file.write(str(data))
                        file.close()
                        
                        # :TODO Use finally to handle exit cases
                        exit("Secret exported to {}".format(args.export))
                        
                    except (ValueError, Exception) as ex:
                        print(str(ex))
                        raise
            except (SecretNotFoundError, LockedError, Exception) as err:
                print(str(err))
                utils.exit_with(err)                
            
        if args.remove:
            if session.vault.remove(session.secret):
                exit("Removed {}".format(session.secret))
            else:
                exit("Could not remove {}".format(session.secret))
                
    if args.store and not args.interactive:
        '''Encrypt user provided data or file to secret file'''
        tmp_secret = None
        
        if not utils.isvalid_name(args.store[0]):
            exit("Invalid secret name")
            
        secret_name = utils.sanitize_name(args.store[0])
            
        if os.path.exists(args.store[1]):
            '''Is this a file to digest?'''
            try:
                with open(args.store[1], 'r') as f:
                    x = f.read()
                    tmp_secret = Secret(secret_name, value=x)
            except (PermissionError, Exception) as ex:
                utils.exit_with(ex)
        else:
            try:
                '''Was json given?'''
                tmp_secret = Secret.load(args.store[1])
                # :TODO Should sanitize here or rely on sanitization of module models.secret
                tmp_secret.name = secret_name
            except Exception:
                '''fallback will just stringify the value'''
                tmp_secret = Secret(secret_name, value=str(args.store[1]))
        # finally
        if type(tmp_secret) is Secret:
            if session.vault.store(tmp_secret):
                exit('Stored {}'.format(tmp_secret.name))
            else:
                exit("Could not store, vault is locked (?)")
    
    if args.interactive:
        '''Interactive CLI for creating a secret'''
        s = secretsUI.add_secret()
        if args.debug:
            # Debug mode will print out the new secret
            print("\n{}\n".format(str(s)))
        try:
            success = session.vault.store(s)
            if success:
                exit("Stored {}".format(s.name))
        except LockedError:
            exit("Could not store, vault is locked")
        except Exception:
            exit("Could not store")

    if not args.secret or args.list_secrets:
        # Default operations: 
        # 2. list secrets of the select vault and output selected secret
        while True:
            selected = vaultsUI.list_vault_and_select(session.vault)
            if selected:
                args.secret = selected
                args.export = "stdout"
                args.list_secrets = False
                return cli(args)

def main():
    parser = argparse.ArgumentParser()
    # Vault selection and operations
    parser.add_argument('vault', help="Select a vault", type=str, nargs='?', const='')
    parser.add_argument('--purge',  help="Purge vault", action='store_true')
    parser.add_argument('--list',   help="List vault", action='store_true', dest="list_secrets")
    # Secrets
    parser.add_argument('-s', '--secret', dest='secret', help="Select a secret", type=str)
    parser.add_argument('-rm', '--remove',  help="Remove selected secret", action='store_true')
    parser.add_argument('-o', '--out', '--export', dest="export", help="Export secret to specified file", type=str, nargs='?', default='stdout', const='stdout')
    # Secrets: Create secrets
    parser.add_argument('-st', '--store', dest="store", help="Secret name and content to store", nargs=2, metavar=('name', 'content'), type=str)
    parser.add_argument('--interactive',  help="Add secrets interactively", action='store_true')
    # Debug and verbosity
    parser.add_argument('--debug', dest="debug", help="Activate debug mode", action='store_true')

    args = parser.parse_args()
    
    cli(args)


if __name__ == '__main__':
    main()
