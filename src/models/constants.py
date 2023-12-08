
from os import path

default_vault_dir = path.expanduser('~') + '/.vaults/'
default_config_dir = path.join(str(default_vault_dir), ".config")

def default_dir(vault: str) -> str:
    return path.join(default_vault_dir, vault)

def default_cfg(vault: str) -> str:
    return path.join(default_dir(vault), "{}.cfg".format(vault))

def default_secrets(vault: str) -> str:
    return path.join(default_dir(vault), "secrets")
