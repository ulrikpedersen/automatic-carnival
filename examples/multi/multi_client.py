import PyTango.client

my_object = PyTango.client.Object("multi_my_object")

print(f"my_object.bla = {my_object.bla}")
print(f"my_object.ble = {my_object.ble}")
print(f"my_object.bli = {my_object.bli}")

r1 = my_object.func1()
print(f"my_object.func1() = {r1}")

r2 = my_object.func2(96.44)
print(f"my_object.func2(96.44) = {r2}")

r3 = my_object.func3(45.86, "hello", d=False, c="world")
print(f"my_object.func3(45.86, 'hello', d=False, c='world') = {r3}")

another_object = PyTango.client.Object("multi_another_object")

r1 = another_object.is_valid()
print(f"another_object.is_valid() = {r1}")

r2 = another_object.lets_go("hello, world!")
print(f"another_object.lets_go('hello, world!') = {r2}")
