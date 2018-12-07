import string

mystr = 'my is god'
count = 1
print('count = ',count)
float_num = 2.0
print('float_num = ',float_num)
print(mystr,count,float_num)
print(mystr + ' haha')
print(mystr + str(count))

print('count = %d,float_num = %f'%(count,float_num))
print('count = {0},float_num = {1:.2f}'.format(count,float_num))

a = 1
def change_integer(a):
    a = a + 1
    return a
print (change_integer(a))
print (a)

tmp_list = [250,350]
print(tmp_list[a])