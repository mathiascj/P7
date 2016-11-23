class Recipe:

    def __init__(self, dependencies, start_module, start_direction):
        self.dependencies = dependencies
        self.start_module = start_module
        self.start_direction = start_direction


    def __getitem__(self, item):
        return self.dependencies[item]

    def values(self):
        return self.dependencies.values()

    def items(self):
        return self.dependencies.items()

    def __len__(self):
        return len(self.dependencies)