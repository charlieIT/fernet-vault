from ..models import secret
from ..utils import isvalid_name, sanitize_name


def add_notes() -> str:
    notes = []
    print('Notes: ([ENTER] twice to complete)')
    for i in range(100):
        input_ = input("> ")
        if input_ is False:
            return ''
        elif input_ == "":
            break
        else:
            notes.append(input_)

    return "\n".join(notes)


def add_custom() -> dict:
    custom = {}
    while True:
        check = input('Add custom field? [(y)es/(n)o]: ')
        if check not in ['y', 'yes']:
            break
        name = input("Field name: ")
        value = input("Field value: ")
        custom.update({name: value})
        
    return custom
    

def add_secret() -> secret.Secret:
    args = {}
    '''Ask user to interactively define a secret'''
    name = input('Name: ')
    if not isvalid_name(name):
        print("Invalid name")
        return add_secret()
        
    args["name"] = sanitize_name(name)
    args["category"] = input('Choose a category (leave empty for None): ')
    args["url"] = input('URL (leave empty for None): ')
    tags = input("Tags (Comma-separated values or leave empty for None): ")
    args["tags"] = [t.strip() for t in tags.split(',') if t != '' and t is not False]
    args["notes"] = add_notes()
    custom = add_custom()
    return secret.Secret(**{**args, **custom})
