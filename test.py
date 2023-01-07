import re
pattern = re.compile("[\\dA-Za-z\\s.,\"$%!?:()-\u2014;\u00e9]+")

def contains_chinese(x):
    r = pattern.findall(x)
    if not r:
        return True
    if r[0] == x:
        return False
    return True

a = "你撤回了一条消息"
b = "昨天 11:23"
c = "11:23"
d = "Monday 11:23"

lst = [a, b, c, d]

for x in lst:
    print(contains_chinese(x))
