# 0,1,1,2,3,5

start = 0
next_ = 1
n = 1
while n <=10:
    print(start,',',end='')
    temp = next_
    next_ = start + next_
    start = temp
    n += 1