from sys import argv
from sys import exit as sysexit
from time import sleep
from attacker import Attacker
import argparse

strings = {
    'DESCRIPTION' : 'A simple tool for doing brute-force attack on instagram accounts, with support for tor network.'
}

parser = argparse.ArgumentParser(description = strings['DESCRIPTION'])


# username = argv[1]
# passlist = argv[2]
# thread_c = int(argv[3])

attacker = Attacker(username, passlist)
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

