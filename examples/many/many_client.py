from time import time

import tango.client

N = 100

obj_names = ["obj{i:04d}" for i in range(N)]

start = time()
objs = map(tango.client.Object, obj_names)
dt = time() - start
print(f"Took {dt}s to create {N} objects (avg {dt/N}s/object)")

start = time()
res = [obj.func3(1, 2) for obj in objs]
dt = time() - start
print(f"Took {dt}s to call func3 on {N} objects (avg {dt/N}s/object)")
