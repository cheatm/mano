from mano import conf
import sys


lines = ["#! /bin/bash"]
for name, value in conf.DICT.items():
    if len(value):
        lines.append("export {}={}".format(name, value))


path = sys.argv[1]
with open(path, "w") as fp:
    fp.write("\n".join(lines))

