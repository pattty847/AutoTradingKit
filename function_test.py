import itertools

# Danh sách ban đầu
_list = [1, 2, 3,3,4,4,5]

# Tạo tất cả các hoán vị
permutations = list(itertools.permutations(_list))

print(len(permutations))
# In ra các hoán vị
# for perm in permutations:
#     print(perm)

my_list = []


def swap_elements(lst, index1, index2):
    lst[index1], lst[index2] = lst[index2], lst[index1]


def calculate_list(input_list,compare_list,n = 0):
    new_list = []
    _leng = len(input_list)
    for i in range(_leng):

        my_list.append(input_list)
        
        print(input_list)
        new_list= []
        if i != 0:
            swap_elements(input_list,0,i)
            if my_list[0] == input_list:
                break
            calculate_list(input_list,compare_list)

    
    if n == _leng-1:
        return
    n+=1
    swap_elements(input_list,0,n)
    calculate_list(input_list,compare_list,n)
            # if input_list == compare_list:
            #     return
            
calculate_list(_list,_list)   
    
print(len(my_list))


