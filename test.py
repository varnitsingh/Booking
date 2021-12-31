# def f(a):
#     yield a,a*a

# for i in f(2):
#     print(i)
'''
You are given a list of n-1 integers and these integers are in the range of 1 to n. 
There are no duplicates in the list. One of the integers is missing in the list. 
Write an efficient code to find the missing integer.
Input: arr[] = {1, 2, 4, 6, 3, 7, 8}
Output: 5
Explanation: The missing number from 1 to 8 is 5

Input: arr[] = {1, 2, 3, 5}
Output: 4
Explanation: The missing number from 1 to 5 is 4
'''

def find_missing_number(arr):
    
    for i in range(1,len(arr)+2):
        if i not in arr:
            return i

print(find_missing_number([1, 2, 3, 5]))