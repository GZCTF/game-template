#!/bin/sh

# or you can set the user in the dockerfile, if you don't need root for per-connection setup
su ctf -c "python -u /home/ctf/chall.py"
