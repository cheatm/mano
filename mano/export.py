from mano import conf


print("#! /bin/bash")
for name, value in conf.DICT.items():
    print("export {}={}".format(name, value))
