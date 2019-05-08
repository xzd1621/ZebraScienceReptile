def change(arr):
    arr['a']=1


if __name__ == '__main__':
    arr = {
        'a':2,
        'b':3
    }
    change(arr)
    print(arr)
