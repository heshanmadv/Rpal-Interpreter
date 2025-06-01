from src.screener import screener
file = input()
token_list, invalid_flag, invalid_token = screener(file)

with open("output.txt", "w") as file:
    for token in token_list:
        file.write(f"{token.content} {token.type}\n")
        
print(f"Invalid token present: {invalid_flag}")
if invalid_flag:
    print(f"Invalid token: {invalid_token}")       