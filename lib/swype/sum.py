import sys
import os

if len(sys.argv)==2:
    fn = sys.argv[1]
    if fn.isdigit():
        fn = max([x for x in os.listdir(os.getcwd()) if x[:4]=="log"+fn])
else:
    fn = max([x for x in os.listdir(os.getcwd()) if x[:4]=="log1"])

f = open(fn,'r')
l = f.read().split("\n")

while "" in l:
    l.remove("")

l = [float(x) for x in l]

print sum(l)/len(l)

f.close()
