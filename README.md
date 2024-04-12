# GlobalTalk in Docker

## Introduction

This project is intended to make it slightly easier to fire up a
GlobalTalk router. I found the whole idea of
[GlobalTalk](https://marchintosh.com/globaltalk.html) quite
fascinating, but seeing all the hoops required to get Apple Internet
Router setup and running I avoided it until close to the end of
#MARCHintosh 2024. In an effort to get my Apple IIe to join GlobalTalk
I decided to see if there was a way to get everything running in a
Docker container with a way to simply pass in configuration and not
need to actually click around inside the emulated Macintosh to alter
configuration.

## Features

- **Easy to Use**: Configuration can be done from outside the emulated
    Macintosh with command line flags or environment variables
- **Docker Integration**: Uses a docker container to keep all the
    custom packages from cluttering up the host

## Prerequisites

Before you begin, ensure you have the following:

- Docker
- Bootable 68k Macintosh disk image with Apple Internet Router installed
- Quadra 800 rom

## Getting Started

### Installation

To get started with GlobalTalk in Docker, follow these steps:

1. Create a bridge interface on your Linux host

2. Copy the example compose file to docker-compose.yml

3. Adjust the options in the docker-compose.yml to reflect your required settings

4. `docker compose up`

### Configuration

There are several command line flags that can be passed to `start-globaltalk`

### Enhancement Ideas

- MacTCP doesn't support DHCP, maybe `start-globaltalk` could make a
  dhcp client call and allocate an IP address? Would probably need to
  keep a thread running to make sure the lease doesn't expire.
- Support qcow2 images, which can be smaller than raw image files. Raw
  image files can be made smaller on disk by creating them as sparse
  files, but that requires extra steps. Using qemu-nbd makes it
  possible for tools expecting raw images to directly work with qcow2
  images.
- Get virtio-tablet-device working through VNC so that mouse is tracked

### Known Problems

- When AIR is running the emulated Mac crashes after a few hours

## License

This project is licensed under the GNU General Public License v3.0 -
see the [LICENSE.md](LICENSE.md) file for details. For more
information on the GPLv3 License, please visit [GNU's General Public
License](https://www.gnu.org/licenses/gpl-3.0.html).

## Authors

- [FozzTexx](https://mastodon.fozztexx.com/@fozztexx) [blog](https://insentricity.com)

## Acknowledgments

- Thanks to
  [@europlus@europlus.zone](https://social.europlus.zone/@europlus),
  [@smallsco@oldbytes.space](https://oldbytes.space/@smallsco),
  [@robdaemon@tech.lgbt](https://tech.lgbt/@robdaemon), and
  [@wotsac@mastodon.social](https://mastodon.social/@wotsac) for
  helping me figure out how to build a custom version of QEMU and get
  a 68k Mac running, discovering what files and resource sections
  needed to be updated, and providing constant motivation and encouragement
- Thanks to Paul Rickards for [instructions on getting Apple Internet
  Router running](https://biosrhythm.com/?p=2767)
- Everyone involved in creating [GlobalTalk](https://marchintosh.com/globaltalk.html)
