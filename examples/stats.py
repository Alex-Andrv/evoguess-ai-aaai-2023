import os
vars = set()
all = 0
directory = 'examples/result15'
for filename in os.listdir(directory):
    input = open(os.path.join(directory, filename), 'r')
    arr = input.readline().strip().split()
    all += len(arr)
    for v in arr:
        vars.add(v)
print(all)
print(len(vars))