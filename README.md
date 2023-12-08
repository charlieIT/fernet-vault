# fernet-vault

`fernet-vault` is a simple tool to **manage secret vaults**.

It allows the definition of multiple secure vaults and secrets, which are stored as encrypted files in the local filesystem.

The project is an ongoing Python coding exercise on symmetric cryptography.

# Requirements

- `cryptography v41.0.7`

## Installation

### Clone the repository

```
git clone https://github.com/charlieIT/fernet-vault
```

### Install locally using `pip`
```bash
pip3 install fernet-vault/
```

# Usage

After installation, the project should be available as `fernetvault`.

`fernet-vault` requires all `vaults` to be setup with a private master password.

The application will not store this password, only the `salt` used for the `key derivation function` and a final `Encrypted Key` (EKEY). The master password is used to setup and unlock the vault and should be kept secret.

## Create vaults

```bash
fernetvault "MySecretVault"
```
```text/plain
Create new? [(y)es/(n)o] y
Vault password: *****
Confirm you vault password: *****
Created MySecretVault @ ~/.vaults/MySecretVault

Unlock vault: 
** MySecretVault has no secrets
```

## Store secrets

### Store a secret `MyLogin` under `MySecretVault`

```
fernetvault MySecretVault --store MyLogin "Super_Secret_Value"
```

```text/plain
Unlock vault: *****
Stored MyLogin
```

### Create a secret interactively

Use `--interactive` flag to access a secret generation form. It is possible to add `custom fields`.

```bash
fernetvault MySecretVault --store --interactive
```
```text/plain
Unlock vault: *****

Name: My Secret Notes
Choose a category (leave empty for None): notes
URL (leave empty for None): mynotes.example.com
Tags (Comma-separated values or leave empty for None): notes, secrets, payments
Notes: ([ENTER] twice to complete)
> This is a 
> super secret 
> note
> 
Add custom field? [(y)es/(n)o]: y
Field name: Notes Login
Field value: SomePassword
Add custom field? [(y)es/(n)o]: n
Stored My Secret Notes
```

### Create a secret from a file
```bash
fernetvault MySecretVault --store SecretFile /foo/bar.file
```
```text/plain
Unlock vault: *****

Stored SecretFile
```

## Manage secrets

### View secrets

Use flag `-s` or `--secret` to select a secret from the vault

```bash
fernetvault MySecretVault -s "My Secret Notes"
```

```text/plain
Unlock vault: *****

{
    "name": "My Secret Notes",
    "url": "mynotes.example.com",
    "category": "notes",
    "notes": "This is a \nsuper secret \nnote",
    "tags": [
        "notes",
        "secrets",
        "payments"
    ],
    "Notes Login": "SomePassword"
}
```

### Export to a file

To redirect output to a file, use `--export` and provide a writable destination file.

```bash
fernetvault MySecretVault -s "My Secret Notes" --export ~/MyNotes.json
```
```text/plain
Unlock vault: *****

Secret exported to ~/MyNotes.json
```
<details>
    <summary>
        Example output
    </summary>

```bash
cat ~/MyNotes.json
```

```json
{
    "name": "My Secret Notes",
    "url": "mynotes.example.com",
    "category": "notes",
    "notes": "This is a \nsuper secret \nnote",
    "tags": [
        "notes",
        "secrets",
        "payments"
    ],
    "Notes Login": "SomePassword"
}
```

</details>

### Remove secrets
```bash
fernetvault MySecretVault -s MyLogin --remove
```

<details>
    <summary>
        Example output
    </summary>

```json
Unlock vault: *****

{
    "name": "MyLogin",
    "url": "",
    "category": "",
    "notes": "",
    "tags": [],
    "value": "Super_Secret_Value"
}

Removed MyLogin
```
    
</details>

## Manage vaults

### Purge vault

<details>
    <summary>
        Example vault setup
    </summary>

Create a new vault

```bash
fernetvault ExampleVault -st ExampleSecret "Example"

fernetvault ExampleVault --list
```

List vault secrets

```text/plain
ExampleVault secrets: 

- [ExampleSecret]
```
<hr/>
    
</details>

Use `--purge` flag to remove a vault

```bash
fernetvault ExampleVault --purge
```
```text/plain
Unlock vault: *****

!! Please confirm vault removal: [(y)es] > y

Removed ExampleVault
```

# Filesystem

Currently, all `vaults` are stored under `~/.vaults/<vault-name>`.

```text/plain
.
└── MySecretVault
    ├── MySecretVault.cfg
    └── secrets
        ├── My Secret Notes
        └── SecretFile

3 directories, 3 files
```

At the moment, each `vault` contains a `.cfg` file with cryptographic assets and a `secrets` directory, where the `encrypted secrets` will be stored.