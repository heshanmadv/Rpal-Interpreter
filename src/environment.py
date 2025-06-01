class Environment():
    def __init__(self, number, parent):
        self.name = "e_" + str(number)
        self.variables = {}
        self.children = []
        self.parent = parent
    
    # This function adds a child to the current environment.    
    def add_child(self, child):
        self.children.append(child)
        child.variables.update(self.variables)
    
    # This function adds a variable to the current environment.    
    def add_variable(self, key, value):
        self.variables[key] = value