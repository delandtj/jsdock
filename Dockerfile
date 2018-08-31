# build this with ./buildit.sh
FROM ubuntu:latest

ARG ssh_prv_key
ARG ssh_pub_key

RUN apt-get update && apt-get -y upgrade
RUN apt -y install apt-utils
RUN apt-get install -y curl python3-pip python3-dev git \
	pkg-config libvirt-dev sudo libssl-dev libffi-dev locales vim ssh \
  iproute2 bash-completion inetutils-ping inetutils-telnet inetutils-tools \
  inetutils-traceroute


# ssh stuff
RUN mkdir -p /root/.ssh && \
    chmod 0700 /root/.ssh && \
    ssh-keyscan github.com > /root/.ssh/known_hosts && \
    mkdir -p /run/sshd

# workdirs for code
RUN mkdir -p /opt/code

RUN echo "$ssh_prv_key" > /root/.ssh/id_rsa && \
    echo "$ssh_pub_key" > /root/.ssh/id_rsa.pub && \
    cat /root/.ssh/id_rsa.pub > /root/.ssh/authorized_keys && \
    chmod 600 /root/.ssh/id_rsa && \
    chmod 600 /root/.ssh/id_rsa.pub
RUN echo "Host github.com\n\tStrictHostKeyChecking no\n" >> /root/.ssh/config
RUN sed -ie 's/^\#Port .*/Port 6322/' /etc/ssh/sshd_config

# OK, now add jumpy stuff
ADD installit.sh /root
# RUN /installit.sh

# Or whatwver (robot maybe)?
CMD ["/usr/sbin/sshd", "-D"]
