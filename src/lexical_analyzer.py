from src.tokens import Token

def create_tokens(characters): 
    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    operators = '+-*<>&.@/:=~|$!#%^_[]{}\"?'
    punctuation = '();,'
    digits = '0123456789'
    underscore = '_'
    newline = '\n'

    token_types, tokens, token_lines = [], [], []
    buffer = ''
    i, line_number = 0, 1

    try:
        while i < len(characters):

            # Detect and extract string literals enclosed in single quotes
            if characters[i] == "'":
                buffer += characters[i]
                i += 1

                while i < len(characters):
                    if characters[i] == "\n":
                        line_number += 1

                    if characters[i] == "'":
                        buffer += characters[i]
                        i += 1
                        break
                    else:
                        buffer += characters[i]
                        i += 1

                if len(buffer) == 1 or buffer[-1] != "'":
                    print("String is not properly terminated.")
                    exit(1)

                tokens.append(buffer)
                token_types.append('<STRING>')
                token_lines.append(line_number)
                buffer = ''  

            # Parse numeric tokens, ensuring validity
            elif characters[i] in digits:
                buffer += characters[i]
                i += 1

                while i < len(characters): 
                    if characters[i] in digits:
                        buffer += characters[i]
                        i += 1
                    elif characters[i] in letters:
                        buffer += characters[i]
                        i += 1
                    else:
                        break

                tokens.append(buffer)
                token_lines.append(line_number)

                # Check if it's a valid integer or an invalid token
                try:
                    int(buffer)
                except:
                    token_types.append('<INVALID>')
                else:
                    token_types.append('<INTEGER>')

                buffer = ''

            # Recognize identifiers (letters followed by alphanumerics or underscores)
            elif characters[i] in letters:
                buffer += characters[i]
                i += 1

                while i < len(characters) and (characters[i] in letters or characters[i] in digits or characters[i] == underscore):
                    buffer += characters[i]
                    i += 1

                tokens.append(buffer)
                token_types.append('<IDENTIFIER>')
                token_lines.append(line_number)
                buffer = ''

            # Capture single-line comments that start with //
            elif characters[i] == '/' and characters[i+1] == '/':
                buffer += characters[i]
                buffer += characters[i+1]
                i += 2

                while i < len(characters) and characters[i] != '\n':
                    buffer += characters[i]
                    i += 1

                tokens.append(buffer)
                token_types.append('<DELETE>')
                token_lines.append(line_number)
                buffer = ''

            # Ignore whitespace and tab characters, treating sequences as a single space
            elif characters[i] == ' ' or characters[i] == '\t':
                buffer += characters[i]
                i += 1

                while i < len(characters) and (characters[i] == ' ' or characters[i] == '\t'):
                    buffer += characters[i]
                    i += 1

                tokens.append(buffer)
                token_types.append('<DELETE>')
                token_lines.append(line_number)
                buffer = ''

            # Handle punctuation characters as separate tokens
            elif characters[i] in punctuation:
                buffer += characters[i]
                tokens.append(buffer)
                token_types.append(buffer)
                token_lines.append(line_number)
                buffer = ''
                i += 1

            # Process newline characters for tracking line numbers
            elif characters[i] == '\n':
                tokens.append(newline)
                token_types.append('<DELETE>')
                token_lines.append(line_number)
                line_number += 1
                i += 1

            # Identify operators, ensuring not to confuse with comments
            elif characters[i] in operators:
                while i < len(characters) and characters[i] in operators:
                    if characters[i] == '/' and characters[i+1] == '/':
                        tokens.append(buffer)
                        token_types.append('<OPERATOR>')
                        buffer = ''
                        token_lines.append(line_number)
                        break     

                    buffer += characters[i]
                    i += 1

                tokens.append(buffer)
                token_types.append('<OPERATOR>')
                token_lines.append(line_number)
                buffer = ''

            # Report any character that doesn’t fit known categories
            else:
                print(f"Invalid character: {characters[i]} at position {i}")
                exit(1)

    except IndexError:
        # Handle out-of-bounds access gracefully
        pass

    number_of_tokens = len(tokens)

    for i in range(number_of_tokens):
        if i == 0:
            tokens[i] = Token(tokens[i], token_types[i], token_lines[i])
            tokens[i].make_first_token()
        elif i == number_of_tokens - 1:
            # Special case: remove trailing newline as final token
            if tokens[i] == '\n':
                tokens[i - 1].make_last_token()
                tokens.remove(tokens[i])
                token_types.remove(token_types[i])
                token_lines.remove(token_lines[i])
            else:
                tokens[i] = Token(tokens[i], token_types[i], token_lines[i])
                tokens[i].make_last_token()
        else:
            tokens[i] = Token(tokens[i], token_types[i], token_lines[i])

    return tokens
