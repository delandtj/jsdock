# build this with ./buildit.sh
FROM ubuntu:latest

ARG ssh_prv_key
ARG ssh_pub_key

RUN apt-get update && apt-get install -y curl python3-pip python3-dev git \
	pkg-config libvirt-dev sudo libssl-dev libffi-dev locales vim ssh

ADD installit.sh /

# ssh stuff
RUN mkdir -p /root/.ssh && \
    chmod 0700 /root/.ssh && \
    ssh-keyscan github.com > /root/.ssh/known_hosts

RUN echo "$ssh_prv_key" > /root/.ssh/id_rsa && \
    echo "$ssh_pub_key" > /root/.ssh/id_rsa.pub && \
    chmod 600 /root/.ssh/id_rsa && \
    chmod 600 /root/.ssh/id_rsa.pub
RUN echo "Host github.com\n\tStrictHostKeyChecking no\n" >> /root/.ssh/config

# OK, now add jumpy stuff
RUN /installit.sh

CMD ["bash"]
