class StringD:
    def __init__(self):
        self.values = dict()

    def __get__(self, instance, owner):
        return self.values[instance]

    def __set__(self, instance, value):
        if not isinstance(value, str):
            raise TypeError('Value must be a string')

        self.values[instance] = value


class Person:
    name = StringD()

    def __init__(self, name):
        self.name = name

    # def __eq__(self, other):
    #     return self.name == other.name


p = Person('Oleg')
#
# d = {
#     p: 123
# }

print(p.name)
print(dir(p))
print(p.print(1))
