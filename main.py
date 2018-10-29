from sys import argv
from sys import exit as sysexit
from time import sleep
from attacker import Attacker

username = argv[1]
passlist = argv[2]
thread_c = int(argv[3])

attacker = Attacker(username, passlist, thread_c)
attacker.start()
try:
    attacker.block()
    print()
except KeyboardInterrupt:
    print()
    print(' ==> Exiting... might take a while...')
    attacker.stop()
    attacker.block()
    print()

