class Node:
    def __init__(self, value):
        self.value = value
        self.children = []  
        self.level = 0

# Recursively traverse each child node with increased level        
def preorder_traversal(root):
    if root is None:
        return

    print("." * root.level + root.value)
    
    for child in root.children:
        child.level = root.level + 1
        preorder_traversal(child)  