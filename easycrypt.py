#!/usr/bin/env python
"""

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

1) Why don't you use scrypt?  Scrypt is not compatible older versions of
the Python Cryptography Library. 

2) Isn't embedding random code within a file a security risk?  Embedding
code within a file isn't meant to prove that a file can be trusted. PGP,
Code Signing, TLS, & So on all provide trust solutions which are outside
the scope of this application.

3) Can I decrypt a file that contains embedded code?  Yes,  just add the
-e option when decrypting the file. You will need to match the version. 

"""

import os
import sys
import argparse
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import cryptography
import getpass
import hashlib
import struct

def getbytes( fn, sz, offset ):
  with open(fn, 'rb') as fi:
    fi.seek(offset)
    return fi.read(sz)

def putbytes( fn, msg, offset):
  with open(fn, 'wb') as fi:
    fi.seek(offset)
    return fi.write(msg)

def parseargs():
  parser = argparse.ArgumentParser()
  parser.add_argument("-d", "--decrypt", help="default is to encrypt", default=False, action='store_true')
  parser.add_argument("-e", "--embed", help="embed decryption routines in output stream", default=False, action='store_true')
  parser.add_argument("file", help="input [output], default is encrypt in place", nargs='+')
  args = parser.parse_args()

  infile = args.file[0]
  outfile = infile
  if len(args.file) > 1:
    outfile = args.file[1]

  return args, infile, outfile

def getcipher( pw, iv, rounds=300000, tag=None ):
  for i in range(rounds):
    idx = struct.pack( "i", i )
    pw = hashlib.sha256( idx + iv + pw ).digest()
  return Cipher(
    algorithms.AES(pw), modes.GCM(iv, tag=tag), backend=default_backend() )
  
def encrypt( infile, outfile, embed=False ):
  iv = os.urandom(16)
  try: 
    pw = bytes("foo", 'utf-8')
    pw = bytes(getpass.getpass(), 'utf-8')
    confirm = bytes(getpass.getpass("Confirm: "), 'utf-8')
  except:
    # Fallback for Python 2 
    pw = getpass.getpass()
    confirm = getpass.getpass("Confirm: ")

  if (pw != confirm):
    raise ValueError("Passwords don't match");
 
  enc = getcipher( pw, iv ).encryptor()
  msg = enc.update(getbytes(infile, -1, 0)) + enc.finalize()
  if embed: 
    data = getbytes( sys.argv[0], -1, 0 )
    try:
      data = str( data, 'utf-8' )
    except: 
      pass
    self_extract = """#!/usr/bin/env bash
tmp_file=$(mktemp -t tmp-easycrypt-XXXXXXXXXX.py)
if [ -z ${1} ]; then 
  echo "usage:" $0 "DEST"
  exit -1
fi
#echo ${tmp_file}
cat << %(tag)s > $tmp_file
%(data)s
%(tag)s
/usr/bin/env python $tmp_file -d -e $0 $1
ret=$?
rm ${tmp_file}
exit ${ret}
%(eq)s=%(eq)s
""" % { 'data': data, 'tag': "__%s__" % "PYTHON", 'eq': "=====" }
    try: 
      self_extract = bytes(self_extract, 'utf-8')
    except:
      pass
    putbytes( outfile, self_extract + iv + msg + enc.tag, 0 )
  else:
    putbytes( outfile, iv + msg + enc.tag, 0 )

def decrypt( infile, outfile, embed=False ):
  offset=0
  if embed:
    fi = getbytes(infile, 16384, 0)
    try: 
      idx = fi.find("======%s" % "=====")
    except:
      idx = fi.find(bytes("======%s" % "=====", "utf-8"))
    offset = idx + 12
    
  iv = getbytes( infile, 16, offset )
  try: 
    pw = bytes("foo", 'utf-8')
    pw = bytes(getpass.getpass(), 'utf-8')
  except:
    # Fallback for Python 2 
    pw = getpass.getpass()

  fi = getbytes(infile, -1, 16+offset)
  dec = getcipher( pw, iv, tag=fi[-16:] ).decryptor()
  msg = dec.update( fi[:-16] ) + dec.finalize()
  putbytes( outfile, msg, 0 )

try: 
  args, infile, outfile= parseargs()

  if args.decrypt:
    decrypt( infile, outfile, args.embed )
  else:
    encrypt( infile, outfile, args.embed )
except cryptography.exceptions.InvalidTag:
  print( "Decrypt failed; bad checksum" )
except Exception as e:
  print( "Application terminated: %s" % (str(e)) )
