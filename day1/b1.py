# Two Sum (Pythonic version) 
# Yêu cầu:
# Cho mảng số nguyên nums và số target, trả về 2 index sao cho tổng = target.

nums = [1, 5, 4, 9, 8, 10, 2, 3]
target = 12

def two_sum_all(nums: list, target):
    seen = {}  
    results = []
    
    for i, num in enumerate(nums):
        complement = target - num
        
        if complement in seen:
            for j in seen[complement]:
                results.append([j, i])
        
        if num not in seen:
            seen[num] = []
        seen[num].append(i)
    
    return results
    
print(two_sum_all(nums=nums, target=target))