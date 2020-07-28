from collections import namedtuple

MyStruct = namedtuple('MyStruct', ['key', 'name', 'id'])
s = MyStruct(key='dsdasd', name='Dmitry', id=123)

print(s.key)
print(s.name)
print(s.id)
print(type(s))

# Back to dict:
d = s._asdict()
print(d)
