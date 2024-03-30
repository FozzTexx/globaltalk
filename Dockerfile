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
	libvde-dev \
	libvdeplug-dev \
	make \
	ninja-build \
	patch \
	python3-venv \
	wget \
	xz-utils \
	zlib1g-dev \
    ; rm -rf /var/lib/apt/lists/* \
    ;

RUN : \
    ; cd /tmp \
    ; wget -nv https://download.qemu.org/qemu-8.2.2.tar.xz \
    ;

RUN <<EOF
cd /tmp
git clone https://github.com/elliotnunn/classicvirtio.git
tar xf qemu-8.2.2.tar.xz
cd qemu-8.2.2/
patch -p1 < /tmp/classicvirtio/patches/qemu-m68k-virtio.patch
./configure --target-list=m68k-softmmu --enable-vnc --disable-docs --enable-slirp
make
make install
EOF
