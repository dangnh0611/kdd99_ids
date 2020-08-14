#!/usr/bin/env python3
from subprocess import run
import string
import random
import shlex
from sys import argv

def main():
    while(True):
        dst= argv[1]
        rand_str=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
        cmd= f'sshpass -p {rand_str} ssh {dst}'
        print(cmd)
        args=shlex.split(cmd)
        run(args)

if __name__=='__main__':
    main()