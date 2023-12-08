class Category:
    def __init__(self, name):
        self.name = name
        self.active = True
                    
    def disable(self):
        self.active = False
    