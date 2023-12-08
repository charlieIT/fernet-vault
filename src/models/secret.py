import json

from ..utils import sanitize_name


class Secret:
    def __init__(self, name: str, **kwargs):
        self.name = sanitize_name(name)
        self.url = kwargs.get('url', '')
        self.category = kwargs.get('category', '')
        self.notes = kwargs.get('notes', '')
        self.tags = kwargs.get('tags', [])

        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def categorize(self, category: str):
        self.category = category
    
    def tag(self, *tags):
        self.tags = list(tags)

    def __str__(self):
        return json.dumps(self.__dict__, indent=4, )
        
    @staticmethod
    def load(secret):
        s = json.loads(secret)
        return Secret(**s)
        