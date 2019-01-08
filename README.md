EasyCrypt; A python tool for encrypting files

EasyCrypt is meant to be an easy way of encrypting and sharing files, while
providing secure and robust crypto. EasyCrypt defaults to a 300,000 round
PBKDF2 derivative to secure your crypto key, and uses AES128-GCM with random
IV for encrypting your files.

Here are some examples:

    # In place encrypt 
    ./easycrypt.py example.file
    
    # In place decrypt
    ./easycrypt.py -d example.file
    
    # Encrypt file + embed decrypt code
    ./easycrypt.py -s example.file encrypted.file
    
    # and now decrypt
    ./encrypted.file decrypted.file

    # Pipe example
    dd if=/dev/urandom bs=1M count=64 | ./easycrypt.py | gzip > out.enc.gz

Known Issues:

1. Why don't you use scrypt?  Scrypt is not compatible with older versions of
   the Python Cryptography Library. 

2. Some features may not work on non Unix platforms. If you are in doubt, you
   are strongly encouraged to test using the included 'test.sh' script. 
   
3. Probably does not work on Python 2.6 and older. (Python 2.7/3 are supported)

4. Supporting Python 3 causes the code to look ugly :(

    (c) Charles Shiflett 2018-9
    Released under the LGPL 3.0, which should be included with this work.

