class Token:
    def __init__(self, content, type, line):
        # Initialize the Token with its text (content), category (type), and source code line number
        self.content = content
        self.type = type
        self.line = line
        self.is_first_token = False  # Flag to indicate if this is the first token in the stream
        self.is_last_token = False   # Flag to indicate if this is the last token in the stream
    
    def make_keyword(self):
        # Updates the token type to <KEYWORD>
        # Used when an identifier is recognized as a reserved word in the language
        self.type = "<KEYWORD>"

    def __str__(self):
        # Returns a formatted string representation of the token, useful for debugging and logging
        return f"{self.content} : {self.type}"
    
    def make_first_token(self):
        # Sets the token as the first one in the sequence
        # This might be used by the parser to recognize the start of a program
        self.is_first_token = True
        
    def make_last_token(self):
        # Marks the token as the final token in the stream
        # Important for indicating the end of input for further analysis (e.g., parsing or code generation)
        self.is_last_token = True
        

