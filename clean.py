#test.py
import re
a = open('dickens5.txt', 'r')
b = open('dickens6.txt', 'w')
for line in a:
    line = re.sub(r'\.', r'\n', line)
    b.write(line)