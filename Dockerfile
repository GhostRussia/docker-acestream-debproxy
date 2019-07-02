FROM debian:jessie

MAINTAINER Ghost_Russia

# install base packages
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /tmp

RUN apt-get update -y && \
    apt-get install -y apt-utils libssl1.0.0 libssl-dev && \
    apt-get install -y \
      ca-certificates \
      libpython2.7 \
      python-apsw \
      python-gevent \
      python-m2crypto \
      python-psutil \
      python-pkg-resources \
      unzip \
      wget

# install acestream-engine
RUN wget  -o - http://dl.acestream.org/linux/acestream_3.1.16_debian_8.7_x86_64.tar.gz && \
    tar -vzxf acestream_3.1.16_debian_8.7_x86_64.tar.gz && \
    mv acestream_3.1.16_debian_8.7_x86_64 /opt/acestream && \
    rm -rf /tmp/*

ADD start.sh /usr/bin/start.sh
RUN chmod +x /usr/bin/start.sh

EXPOSE 6878

WORKDIR /tmp
CMD ["/usr/bin/start.sh"]
