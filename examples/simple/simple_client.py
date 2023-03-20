import PyTango.client

my_object = PyTango.client.Object("my_object")

print(f"my_object.bla = {my_object.bla}")
print(f"my_object.ble = {my_object.ble}")
print(f"my_object.bli = {my_object.bli}")
print(f"my_object.array = {my_object.array}")

r1 = my_object.func1()
print(f"my_object.func1() = {r1}")

r2 = my_object.func2(96.44)
print(f"my_object.func2(96.44) = {r2}")

r3 = my_object.func3(45.86, "hello", d=False, c="world")
print(f"my_object.func3(45.86, 'hello', d=False, c='world') = {r3}")

r4 = my_object.func4()
print(f"my_object.func4() = {r4}")

r5 = my_object.zeros((500, 1000))
print(f"my_object.zeros((500, 1000)) = {r5}")
