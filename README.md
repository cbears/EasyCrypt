EasyCrypt; A python tool for encrypting files

This is meant to be a tool that does one thing, encrypt files, and
do it well.  No attempt is made at backward compatability, instead
when you crypt your file you can choose to include code to decrypt
in the crypted output. This enables always using the latest crypto
algorithms while still being able to decrypt years later using the
same framework. 

EasyCrypt tries to take a reasonable approach to security.  Right
now that is AES-128 GCM with a random 128 bit IV which doubles as
a salt for your key. Your key is also subject to a work function;
A PBKDF2 derivative using 300,000 rounds of the SHA256 HMAC. This
means that with anything aside from a trivially simple key,  your
encrypted file should be computationally expensive to decrypt for
the forseeable future.

Easycrypt uses the python cryptography package, and is meant to work
primarily on linux.  It may work on Windows and Mac as well provided
that Python along with the Python Cryptography package are installed
in your environment.

Here are some examples:

    # In place encrypt file
    python easycrypt.py example.file
    
    # In place decrypt
    python easycrypt.py -d example.file
    
    # Encrypt to encrypted.file and include seld-decrypt
    python easycrypt.py -e example.file encrypted.file
    
    # and now decrypt
    ./encrypted.file decrypted.file

FAQ:

1. Why don't you use scrypt?  Scrypt is not compatible older versions of
the Python Cryptography Library. 

2. Isn't embedding random code within a file a security risk?  Embedding
code within a file isn't meant to prove that a file can be trusted. PGP,
Code Signing, TLS, & So on all provide trust solutions which are outside
the scope of this application.

3. Can I decrypt a file that contains embedded code?  Yes,  just add the
-e option when decrypting the file. You will need to match the version. 


    (c) Charles Shiflett 2016 
    Released under the LGPL 3.0, which should be included with this work.

