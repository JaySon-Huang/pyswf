#!/usr/bin/env python
# encoding=utf-8

from __future__ import print_function

import re

with open('avm_instructions.txt') as infile:
    num = 0
    for line in infile:
        line = line.split('//')[0].strip()
        if not line:
            continue
        m = re.match(r'\{.*N\("(\w+)"\)\W+\}', line)
        if not m:
            raise Exception
        if num == 0:
            print('if ch == 0x{0:02x}:'.format(num))
        else:
            print('elif ch == 0x{0:02x}:'.format(num))
        print('    print("{0}")'.format(m.group(1)))
        # print(hex(num), m.group(1))
        num += 1

