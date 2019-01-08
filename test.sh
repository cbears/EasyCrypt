rm -rf tmp
mkdir tmp

dd if=/dev/urandom of=tmp/file.orig bs=1M count=64
sum=`shasum tmp/file.orig | cut -d\  -f 1`

function test_result()
{
  if [ "$sum" != "$res" ]; 
  then 
    echo "Failed Test. $sum != $res" 
    exit
  else 
    echo "Passed." 
  fi
}

echo -n "Test loopback ... "
res=$sum 
test_result
res="bad"

for pver in python2 python3
do 
  echo -n "Test $pver standard ... "
  export s3cret=quickbrownfox
  $pver easycrypt.py tmp/file.orig tmp/file.$pver.enc
  $pver easycrypt.py -d tmp/file.$pver.enc tmp/file.$pver
  res=`shasum tmp/file.$pver | cut -d\  -f 1`
  test_result
  res=None

  echo -n "Test $pver embed... "
  $pver easycrypt.py -s tmp/file.orig tmp/file.$pver.enc
  tmp/file.$pver.enc tmp/file.$pver.orig
  res=`shasum tmp/file.$pver.orig | cut -d\  -f 1`
  test_result
  res=None

  echo -n "Test $pver pipe... "
  cat tmp/file.orig | $pver ./easycrypt.py | cat > tmp/file.$pver.pipe.enc
  cat tmp/file.$pver.pipe.enc | $pver ./easycrypt.py -d | cat > tmp/file.$pver.pipe
  res=`shasum tmp/file.$pver.pipe | cut -d\  -f 1`
  test_result
  res=None
done




