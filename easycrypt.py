#!/usr/bin/env python
import os
import sys
import argparse
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import cryptography
import getpass
import hashlib
import struct

file_type = None
s3cret = None

if sys.version_info[0] < 3:
  file_type = file
  s3cret = os.getenv("s3cret")
else:
  import io
  file_type = io.IOBase
  try:
    s3cret = bytes(os.getenv("s3cret"), 'utf-8')
  except:
    pass

def getbytes( fn, sz, offset ):
  if isinstance(fn, file_type):
    if sys.version_info[0] < 3:
      return fn.read(sz)
    else:
      return fn.buffer.read(sz)

  with open(fn, 'rb') as fi:
    fi.seek(offset)
    return fi.read(sz)

def putbytes( fn, msg, offset):
  if isinstance(fn, file_type):
    if sys.version_info[0] < 3:
      return fn.write(msg)
    else:
      return fn.buffer.write(msg)

  with open(fn, 'wb') as fi:
    fi.seek(offset)
    return fi.write(msg)

def parseargs():
  parser = argparse.ArgumentParser()
  parser.add_argument("-d", "--decrypt", help="default is to encrypt", default=False, action='store_true')
  parser.add_argument("-s", "--shexec", help="generate self executable encrypted file", default=False, action='store_true')
  parser.add_argument("input", help="default is to encrypt in place", nargs='?', default=sys.stdin)
  parser.add_argument("output", nargs='?', default=None)


  args = parser.parse_args()

  if args.output == None:
    if args.input == sys.stdin:
      args.output = sys.stdout
    else:
      args.output = args.input

  return args, args.input, args.output

def getcipher( pw, iv, rounds=300000, tag=None ):
  for i in range(rounds):
    idx = struct.pack( "i", i )
    pw = hashlib.sha256( idx + iv + pw ).digest()
  return Cipher(
    algorithms.AES(pw), modes.GCM(iv, tag=tag), backend=default_backend() )

def encrypt( infile, outfile, embed=False ):
  iv = os.urandom(16)
  pw = None

  if s3cret:
    pw = s3cret
  else:
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
    # Read easycrypt such that it can be embedded in resultant file.
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
/usr/bin/env python $tmp_file -d -s $0 $1
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
    if isinstance(outfile, str):
      os.chmod(outfile, 0o755)
  else:
    putbytes( outfile, iv + msg + enc.tag, 0 )

def decrypt( infile, outfile, embed=False ):
  offset=0
  if embed:
    if outfile == '-':
      sys.stderr.write("Embed decrypt to stdout not supported\n")
      exit(-1)
    fi = getbytes(infile, 16384, 0)
    try:
      idx = fi.find("======%s" % "=====")
    except:
      idx = fi.find(bytes("======%s" % "=====", "utf-8"))
    offset = idx + 12

  iv = getbytes( infile, 16, offset )
  pw = None

  if s3cret:
    pw = s3cret
  else:
    try:
      notused = bytes("foo", 'utf-8')
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
    decrypt( infile, outfile, args.shexec )
  else:
    encrypt( infile, outfile, args.shexec )
except cryptography.exceptions.InvalidTag:
  sys.stderr.write( "Decrypt failed; bad checksum\n" )
except Exception as e:
  sys.stderr.write( "Application terminated: %s\n" % (str(e)) )
