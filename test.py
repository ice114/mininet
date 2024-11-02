# 以0xffff为例，0xffffffff同理
m = 65493

more_than_0=m<2**15-1
less_than_0=(m&0x800000000)>>15
print(more_than_0)
print(less_than_0)
print(-(((m&0xffff)^ 0xffff)+1))
# 手动操控补码输出，其中m&0xffff获得补码，然后取反加一，再加负号。+-优先级高于位运算
print(   ~((m&0xffff)^0xffff) )
# 先m&0xffff截取，把16位之前的无限位数置0了，得到补码，
# 再^0xffff对16位取反之后对所有位取反（即除后16位之外，前面的位取反），
# 可以把16位之前的无限位数恢复至1，python自动根据补码输出


def trans2ten(num):
    if abs(num<2**15-1):
        return num
    else:
        return -(((num & 0xffff) ^ 0xffff) + 1)

print(trans2ten(65533))

a=[[1,2],[2,3]]

for i in a:
    if i[0]==1:
        print(i)