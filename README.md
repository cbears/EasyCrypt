EasyCrypt; A python tool for encrypting files

EasyCrypt is meant to be an easy way of encrypting and decrypting files, while
providing secure and robust crypto. It's also meant to be simple enough that
even if you don't know python, it should be clear what is happening by looking
at the source code.  

When encrypting/decrypting your password is hashed with a 300,000 round PBKDF2
derivative. The hash function is SHA256, and the resultant hash along with a 
random IV is used as the key for AES128-GCM encryption of your file.

EasyCrypt has an option to embed the decryption code into the resultant file
which provides a clear and easy way to decrypt the file so long as you have
the original password used for encryption. 

Requires python cryptography library: 

    pip install cryptography

Here are some usage examples:

    # In place encrypt 
    ./easycrypt.py example.file
    
    # In place decrypt
    ./easycrypt.py -d example.file
    
    # Encrypt file + embed decrypt code
    ./easycrypt.py -s example.file encrypted.file
    
    # and now decrypt
    ./encrypted.file decrypted.file

    # Pipe example 
    dd if=/dev/urandom bs=1M count=64 | ./easycrypt.py > out.enc

Known Issues:

1. Why don't you use scrypt?  Scrypt is not compatible with older versions of
   the Python Cryptography Library. 

2. Some features may not work on non Unix platforms. If you are in doubt, you
   are strongly encouraged to test using the methods shown in 'test.sh'.
   
3. Probably does not work on Python 2.6 and older. (Python 2.7/3 are supported)

4. Supporting Python 3 causes the code to look ugly :(

    (c) Charles Shiflett 2018-9
    Released under the LGPL 3.0, which should be included with this work.

