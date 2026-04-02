# Top K Frequent Elements
# Yêu cầu:
# Cho mảng nums, trả về k phần tử xuất hiện nhiều nhất

nums = [1,2,3,1,2,1]
freq = {}

for num in nums:
    freq[num] = freq.get(num, 0) + 1

max_num = max(freq, key=freq.get)
print(max_num, freq[max_num]) 