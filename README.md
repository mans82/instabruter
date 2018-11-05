*(This README file is still incomplete, but it's being completed. Hang on...)*
# instabruter
A python script for multi-threaded dictionary attacks on Instagram accounts, with support for tor.
## Tor?
Tor is used for changing public IP address, to avoid *TOO_MANY_REQUESTS* errors. Using it is heavily recommended, although it's not necessary to have tor installed on you system, in order to run instabruter.

For more information about tor, visit [Tor website](https://torproject.org)
## How to install?
Very simple.You don't need any installation. Just clone this repository:

    git clone https://github.com/mans82/instabruter
Then go to the `instabruter` folder (where the repository is cloned), and run `main.py`.
## Any requirements?
Most likely, no. But if you face an error like this:

    File "attacker.py", line 1, in <module>
        import requests
    ImportError: No module named requests

You need to install `requests` python library:

    pip install requests
## How to use?
Here are some examples:
* Start an attack, using a username and a passlist:

      python main.py username passlist.txt

* Start an attack, using an arbitary number of threads (e.g. 32):

      python main.py username passlist.txt -t 32
  or

      python main.py username passlist.txt --threads=32

* Save the attack status, so that you can resume the attack later:
  (Scan status will be saved in `myscan` file.)

      python main.py username passlist.txt -o myscan
  Or use the long option, `--output`, instead of `-o`.

* Now to resume the attack:  
  (long option is `--continue`)

      python main.py -c myscan

* Resume an attack, but use 30 threads instead:  
  (Note that this will be saved to `myscan`)

      python main.py -c myscan -t 30
* Provide another config file, rather than `instabruter.conf`:  
  (There is no short option, sry :( )

      python main.py username passlist.txt --config myconfig.conf

## What is the instabruter.conf?
It is the configuration file of instabruter. Any configuration that is not mentioned in runtime arguments or saved attack file will be read from this file. For example if you have this line in `instabruter.conf`:

    ThreadCount 20
And run:

    python main.py username passlist.txt
, instabruter will use 20 thread for the attack, as defined in the config file.  
Note that command-line arguments will override these configurations.
