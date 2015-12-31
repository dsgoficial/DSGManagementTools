#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
def cleanup():
    error_log = []
    for root, dirs, files in os.walk('/home/luiz'):
        for file in files:
            if '.log' in file:
                full_name = os.path.join(root,file)
                print full_name
                try:
                    with open(full_name, 'r') as old:
                        data = old.read().splitlines(True)
                        old.close()
                    with open(full_name, 'w') as new:
                        lines = len(data)
                        new.writelines(data[lines/2:])
                        new.close()
                except IOError as e:
                    print "I/O error({0}): {1}".format(e.errno, e.strerror)
                except:
                    print sys.exc_info()[0]

if __name__ == '__main__':
    cleanup()