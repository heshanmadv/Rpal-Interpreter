from src.lexical_analyzer import create_tokens

def screener(file_name):
    # List of keywords in RPAL
    keywords = [
         "let", "in", "where", "rec", "fn",
        "aug", "or", "not", "gr", "ge", "ls", "le",
        "eq", "ne", "true", "false", "nil", "dummy",
        "within", "and"
        ]
    

    has_invalid_token = False
    invalid_token = None
    token_list, characters = [], []
    
    try:
        with open(file_name, 'r') as file:
            characters = list(file.read())  # Read entire content at once and convert to list of characters
        token_list = create_tokens(characters)

    except FileNotFoundError:
        print(f"Error: The file '{file_name}' was not found.")
        exit(1)
        
    except Exception as e:
        print(f"Unexpected error while reading the file: {e}")
        exit(1)

    
    # Iterate through token list in reverse order. This reverse iteration will correctly handle the consequent <DELETE>s
    for i in range(len(token_list) - 1, -1, -1):
      
        token = token_list[i]

        
        # If the token is an identifier and it is a keyword, it should be marked as a keyword.
        if token.type == "<IDENTIFIER>" and token.content in keywords:
            token.make_keyword()
        
        # If the token is should be deleted, it should be removed from the list.
        if token.type == "<DELETE>" or token.content == "\n":            
            token_list.remove(token)
            
        # If there are invalid tokens, the first invalid token will be marked as the invalid token.    
        if token.type == "<INVALID>":
            if has_invalid_token == False:
                invalid_token = token
                
            has_invalid_token = True
            
    # If the previous last token is removed in the previous loop, the last token will be the last token in the list.
    if len(token_list) > 0:
        token_list[-1].is_last_token = True
        
    return token_list, has_invalid_token, invalid_token