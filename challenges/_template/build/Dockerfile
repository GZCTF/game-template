# Use `challenge-base`
FROM ghcr.io/gzctf/challenge-base/socat:alpine

# For a pwn challenge:

# FROM ubuntu:24.04 AS builder
# FROM ghcr.io/gzctf/challenge-base/socat:alpine

# init script is used to set up the environment, put the flag in the right place, etc.
# COPY --chmod=500 src/init.sh /init.sh

# run script is used to start the challenge, it is executed by socat
# COPY --chmod=555 src/run.sh /run.sh

# RUN chown -R ctf:ctf /home/ctf && \
#     chmod -R 750 /home/ctf && \
#     cp -R /lib* /home/ctf && \
#     mkdir /home/ctf/lib64  && \
#     mkdir /home/ctf/dev  && \
#     mknod /home/ctf/dev/null c 1 3 && \
#     mknod /home/ctf/dev/zero c 1 5 && \
#     mknod /home/ctf/dev/random c 1 8 && \
#     mknod /home/ctf/dev/urandom c 1 9 && \
#     chmod 666 /home/ctf/dev/* && \
#     mkdir /home/ctf/bin && \
#     mkdir -p /home/ctf/lib/x86_64-linux-gnu/ && \
#     mkdir -p /home/ctf/lib32/ && \
#     cp /bin/sh /home/ctf/bin && \
#     cp /bin/ls /home/ctf/bin && \
#     cp /bin/cat /home/ctf/bin && \
#     cp /bin/base64 /home/ctf/bin

# COPY --from=builder /lib/x86_64-linux-gnu/libc.so.6 /home/ctf/lib/x86_64-linux-gnu/
# COPY --from=builder /lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 /home/ctf/lib64/
# COPY --from=builder /lib/x86_64-linux-gnu/libc.so.6 /lib/x86_64-linux-gnu/
# COPY --from=builder /lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 /lib64/
# COPY --from=builder /usr/sbin/chroot /usr/sbin/
# COPY --chown=ctf:ctf --chmod=500 remember_it_0 /home/ctf/remember_it_0

# CMD [ "/init.sh" ]

# ----------------------------

# For a crypto challenge:

# FROM ghcr.io/gzctf/challenge-base/gmpy2:alpine

# COPY --chown=ctf:ctf src/chall.py /home/ctf/chall.py

# You can ignore the following lines, they are set in base images
## init script is used to set up the environment, put the flag in the right place, etc.
## COPY --chmod=500 src/init.sh /init.sh
## run script is used to start the challenge, it is executed by socat
## COPY --chmod=555 src/run.sh /run.sh
## USER ctf
## WORKDIR /home/ctf
## CMD [ "/init.sh" ]
