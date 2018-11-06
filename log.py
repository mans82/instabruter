from sys import stderr
def log_i(msg, end = '\n'): # Log information
    print(' ==> %s' % msg, file = stderr, end = end)

def log_w(msg, end = '\n'): # Log warnings
    print(' W=> %s' % msg, file = stderr, end = end)