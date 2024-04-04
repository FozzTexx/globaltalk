# -*- indent-tabs-mode: nil -*-

FROM debian:12.5
SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]
ENV DEBIAN_FRONTEND=noninteractive

RUN : \
    ; apt-get update \
    ; apt-get install -y --no-install-recommends \
        # Keep package list in alphabetical order
	autoconf \
	automake \
	bison \
	ca-certificates \
	flex \
	git \
	libcap-ng-dev \
	libgcrypt20-dev \
	libglib2.0-dev \
	libpixman-1-dev \
	libslirp0 \
	libtool \
	make \
	ninja-build \
	patch \
	python3-venv \
	wget \
	xz-utils \
	zlib1g-dev \
        iptables \
    ; rm -rf /var/lib/apt/lists/* \
    ;

ENV QEMU_VERS=8.2.2
#ENV QEMU_VERS=9.0.0-rc1

RUN : \
    ; cd /tmp \
    ; wget -nv https://download.qemu.org/qemu-${QEMU_VERS}.tar.xz \
    ;

RUN <<EOF
cd /tmp
tar xf qemu-${QEMU_VERS}.tar.xz
cd qemu-${QEMU_VERS}
./configure \
  --disable-docs \
  --enable-slirp \
  --enable-vnc \
  --target-list=m68k-softmmu \
  ;
make
make install
EOF

RUN <<EOF
mkdir /usr/local/etc/qemu
echo allow br0 > /usr/local/etc/qemu/bridge.conf
EOF
