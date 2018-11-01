*(This README file is still incomplete, but it's being completed. Hang on...)*
# instabruter
A python script for multi-threaded dictionary attacks on Instagram accounts, with support for tor.
## Tor?
Tor is used for changing public IP address, to avoid *TOO_MANY_REQUESTS* errors. Using it is heavily recommended, although it's not necessary to have tor installed on you system, in order to run instabruter.

For more information about tor, visit [Tor website](https://torproject.org)
## How to install?
Very simple.You don't need installation. Just clone this repository:

    git clone https://github.com/mans82/instabruter
Then go to the cloned folder (Must be named 'instabruter') and run `main.py`.
## Any requirements?
Most likely, no. But if you ever faced an error like this:

    File "attacker.py", line 1, in <module>
        import requests
    ImportError: No module named requests

install `requests` python library:

    pip install requests

## How to use?
Here are some examples:
* Start the attack, using a username and a passlist, using 20 threads:

      python main.py -u username -p passlist.txt -t 20

* Resume an attack (Yes, you can pause the attack and resume it later!), from a saved-attack file (here we call it `username.isb`):

      python main.py -c username.isb

* Resume an attack, but use 30 threads instead:

      python main.py -c username.isb -t 30

## What is the instabruter.conf?
It is actually the configuration file of instabruter. Any configuration that is not mentioned in runtime arguments or saved-attack file will be read from this file. For example if you have this line in `instabruter.conf`:

    ThreadCount 20
And run:

    python main.py -u username -p passlist.txt
instabruter will use 20 thread for attacking, as defined in the config file.
