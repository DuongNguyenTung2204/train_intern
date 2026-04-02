# Flatten Nested List 
# Yêu cầu: 
# Flatten một list lồng nhau bất kỳ.

def flatten(lst):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten(item))  
        else:
            result.append(item)
    return result

nested = [1, [2, [3, 4], 5], 6]
flat = flatten(nested)
print(flat)  