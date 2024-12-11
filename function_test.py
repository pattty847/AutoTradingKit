def get_all_nt(x):
    if x < 1:
        return
    list_uoc = []
    for i in range(1,x+1):
        sochia = x%i 
        if sochia == 0:
            list_uoc.append(i)
    return list_uoc

def check_nt(x):
    if get_all_nt(x)==[1,x]:
        return True
    return False

nt = check_nt(3)


def get_min_nt(x,list_min_nt=[]):
    if check_nt(x):
        list_min_nt.append(x)
        return list_min_nt
    lst = get_all_nt(x)
    print(lst)
    minnt = None
    for i in lst:
        if i!=1 and i!=x:
            print(i)
            if check_nt(i):
                list_min_nt.append(i)
                minnt = i
                break
    if minnt:
        nt = int(x/minnt)
        print(nt,type(nt))
        get_min_nt(nt,list_min_nt)


def total(lst):
    return sum(lst)

def get_rs(x):
    list_min_nt = []
    get_min_nt(x,list_min_nt)
    print(list_min_nt)
    if len(list_min_nt) == 1:
        return list_min_nt
    x = total(list_min_nt)
    get_rs(x)

while True:
    kq = get_rs(int(input()))
    print(kq)

