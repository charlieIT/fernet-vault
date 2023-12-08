import os
from ..models import vault
from ..models.constants import default_vault_dir


def print_as_list(content: list):
    [print('- [{}]'.format(vault)) for vault in content]
    print("\n")


def list_vaults(base_dir: str = default_vault_dir):
    return [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f)) and not os.path.join(base_dir, f).startswith(".")]


def list_and_select(base_dir: str = default_vault_dir):
    all_vaults = list_vaults(base_dir)
    if len(all_vaults) < 1:
        exit('''* There are no vaults, run `fernetvault "your vault name"` to create a vault''')
                                
    print("Your vaults:")
    print_as_list(all_vaults)
    chosen = input("Select a vault: \n > ")
            
    if chosen in all_vaults:
        return chosen
    return False


def list_vault(which: vault.Vault):
    return which.list()


def list_vault_and_select(vault: vault.Vault):
    all_secrets = list_vault(vault)
    if len(all_secrets) > 0:
        print("\n{} secrets: \n".format(vault.name))
        print_as_list(all_secrets)
        chosen = input("Select a secret: \n > ")
                    
        if chosen in all_secrets:
            return chosen
    else:
        exit("** {} has no secrets".format(vault.name))
    return False
