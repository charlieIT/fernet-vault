from argparse import ArgumentParser


def argument(self: ArgumentParser, *args, **kwargs):
    return self.add_argument(*args, **kwargs)

# ArgumentParser.argument = argument


def sanitize_name(name: str) -> str:
    return "".join(x for x in name if x.isalnum() or x in [' ', '-', '_']).strip()


def isvalid_name(name: str) -> bool:
    return name == sanitize_name(name) and not all(c in ['', ' '] for c in name)


def exit_with(err: Exception):
    return exit(getattr(err, 'message', str(err)))
