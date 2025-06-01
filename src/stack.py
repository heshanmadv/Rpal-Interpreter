class Stack:
    def __init__(self, type):
        self.type = type
        self.stack = []
       

     # Adds an element to the top of the stack
    def push(self, item):
        self.stack.append(item)

    # Removes and returns the top element of the stack if it’s not empty
    def pop(self):
        if self.is_empty():
            message = (
                "Error: Attempted to pop from an empty CSE machine stack."
                if self.type == "CSE"
                else "Error: Attempted to pop from an empty AST construction stack."
            )
            print(message)
            exit(1)
        return self.stack.pop()
        
    # Provides a string representation of the stack for easier inspection during debugging
    def __repr__(self):
        return str(self.stack)
    
    # Checks whether the stack currently contains any elements
    def is_empty(self):
        return len(self.stack) == 0
        
    # Allow index-based access to elements
    def __getitem__(self, index):
        return self.stack[index]
    
    # Allow assignment to elements at specific indices
    def __setitem__(self, index, value):
        self.stack[index] = value
        
    # Support reversed iteration through the stack
    def __reversed__(self):
        return reversed(self.stack)

   

   
