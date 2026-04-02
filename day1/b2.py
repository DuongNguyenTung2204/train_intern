# Valid Parentheses (Stack cơ bản) 
# Yêu cầu: 
# Kiểm tra chuỗi ngoặc có hợp lệ không

def is_valid(s: str) -> bool:
    stack = []
    mapping = {')': '(', ']': '[', '}': '{'}
    
    for char in s:
        if char in mapping.values():  
            stack.append(char)
        elif char in mapping:        
            if not stack or stack[-1] != mapping[char]:
                return False
            stack.pop()
        else:
            return False
    
    return not stack

s = "()[]{}"
print(is_valid(s))
print(is_valid("(]"))  
