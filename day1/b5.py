# Find First Non-Repeating Character

# Yêu cầu:
# Tìm ký tự đầu tiên không lặp lại trong chuỗi. 
def first_non_repeating_char(s: str):
    freq = {}
    
    for char in s:
        freq[char] = freq.get(char, 0) + 1

    for char in s:
        if freq[char] == 1:
            return char
    
    return None

s = "swiss"
print(first_non_repeating_char(s)) 