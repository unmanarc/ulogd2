# ulogd2rpm

**HomePage:** http://www.netfilter.org/projects/ulogd/  
**Original specs from:** http://repo.iotti.biz/CentOS/7/srpms/ulogd-2.0.5-2.el7.lux.src.rpm  
**License:**	GPLv2+  
**Current Version:**	2.0.7

## ulogd Description

ulogd is a logging daemon that reads event messages coming from the Netfilter
connection tracking and the Netfilter packet logging subsystem. You have to
enable support for connection tracking event delivery; ctnetlink and the NFLOG
target in your Linux kernel 2.6.x or load their respective modules. The
deprecated ULOG target (which has been superseded by NFLOG) is also supported.

## Motivation

ulogd2 is a very nice software for logging event messages (eg. iptables nflog), but it was dropped off from several RPM based distros.

With this I'm trying to bring the latest version to EL7/EL8/EL9 and Fedora in my COPR repo.