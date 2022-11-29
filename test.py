import numpy as np
from queue import PriorityQueue


q = PriorityQueue()

q.put((4, 'last'))
q.put((2, '2'))
q.put((3, '3'))
q.put((1, '1'))

q.get()
q.get()
q.get()
s = q.get()[1]
print(s)