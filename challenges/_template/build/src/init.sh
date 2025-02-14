#!/bin/sh

echo $GZCTF_FLAG > /home/ctf/flag
unset GZCTF_FLAG

socat TCP-LISTEN:1337,reuseaddr,fork EXEC:/run.sh,stderr

# or limit the timeout
# socat -T60 TCP-LISTEN:1337,reuseaddr,fork EXEC:/run.sh,stderr
