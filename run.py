from collections import deque
import numpy as np
import copy
l = None
t = deque()
t.append(1)
t.append(2)
t.append(3)
t.append(4)

for i  in range(2):
    if l is None:
        l = copy.deepcopy(t)
    else:
        l.extend(list(t)[-2:])
print l

l= list(l)[:2] + list(t)
print l
print t
