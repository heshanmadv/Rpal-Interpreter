# This file contains the structures used in the project.
class Delta:
    def __init__(self, number):
        self.number = number
        
class Tau:
    def __init__(self, number):
        self.number = number
        
class Lambda:
    def __init__(self, number):
        self.number = number
        self.bounded_variable = None
        self.environment = None
        
class Eta:
    def __init__(self, number):
        self.number = number
        self.bounded_variable = None
        self.environment = None        