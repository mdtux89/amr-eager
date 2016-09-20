import sys

a = open(sys.argv[1]).read().splitlines()
b = open(sys.argv[2]).read().splitlines()

print len(list(set(a) & set(b)))