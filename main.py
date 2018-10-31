from sys import argv
from sys import exit as sysexit
from os.path import isfile
from time import sleep
from attacker import Attacker
import argparse

strings = {
    'DESCRIPTION' : 'A tool for brute-forcing instagram accounts, with support for Tor.'
}

parser = argparse.ArgumentParser(description = strings['DESCRIPTION'])
parser.add_argument('-c', '--continue-scan', action = 'store', default = None, dest = 'continue_file')
parser.add_argument('-u', '--username', action = 'store', default = None)
parser.add_argument('-p', '--passlist', action = 'store', default = None)
parser.add_argument('-o', '--save-scan', action = 'store', default = None)

args = parser.parse_args()

if args.continue_file:
    attacker = Attacker.continue_attack(args.continue_file)
elif args.username and args.passlist:
    attacker = Attacker(args.username, args.passlist)
else:
    # not enough arguments
    parser.print_usage()
    sysexit(0)

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

