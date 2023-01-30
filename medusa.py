#!/usr/bin/env python
#####################################
# Installation module for MEDUSA
#####################################
# built on ubuntu 14.04-lts server
# ppa build of freerdp 1.2 from Remmina
# https://launchpad.net/~remmina-ppa-team/+archive/ubuntu/remmina-next
# using remmina-next freerdp 1.2 builds for trusty

# AUTHOR OF MODULE NAME
AUTHOR="Russ Swift (0xsalt)"

# DESCRIPTION OF THE MODULE
DESCRIPTION="This module will install/update Medusa, the Parallel Network Login Auditor. Uses v1.2 freerdp libs with PtH support."

# INSTALL TYPE GIT, SVN, FILE DOWNLOAD
# OPTIONS = GIT, SVN, FILE
INSTALL_TYPE="GIT"

# LOCATION OF THE FILE OR GIT/SVN REPOSITORY
REPOSITORY_LOCATION="https://github.com/jmk-foofus/medusa.git"

# WHERE DO YOU WANT TO INSTALL IT
INSTALL_LOCATION="medusa"

# DEPENDS FOR DEBIAN INSTALLS
DEBIAN="wget,libxvidcore4,libxv-dev,libxv1,libxrender1,libxrandr-dev,libxml2-dev,libxml2,libxkbfile-dev,libxkbfile1,libxinerama-dev,libxinerama1,libxi-dev,libxi6,libxfixes3,libxext-dev,libxdamage-dev,libxcursor-dev,libxcursor1,libx264-142,libx11-dev,libvpx1,libvorbisenc2,libvorbis0a,libva1,libtheora0,libsvn-dev,libssl-dev,libssh2-1-dev,libssh2-1,libspeex1,libsndfile1,libschroedinger-1.0-0,libreadline6-dev,libreadline6,libpulse0,libpq-dev,libpq5,libpcre3-dev,liborc-0.4-0,libopus0,libopenjpeg2,libogg0,libncurses5-dev,libncurses5,libmp3lame0,libjpeg-turbo8,libjpeg8,libgstreamer-plugins-base1.0-dev,libgstreamer-plugins-base0.10-dev,libgstreamer0.10-dev,libgsm1,libgnutls-dev,libgmp-dev,libgmp10,libgcrypt11-dev,libgcrypt11,libfuse-dev,libfuse2,libfreerdp-plugins-standard,libfreerdp-dev,libflac8,libcups2-dev,libcups2,libavutil52,libavcodec54,libavahi-common-data,libavahi-common3,libavahi-client3,libasyncns0,libasound2-dev,libasound2-data,libasound2,git-core,git,cmake,build-essential,automake"

# DEPENDS FOR FEDORA INSTALLS
FEDORA="git,make,automake,m4,perl,gcc,gcc-c++,kernel-devel,apr-devel,libpqxx,libpqxx-devel,afpfs-ng-devel,openssl-devel,libssh2-devel,postgresql-devel,subversion-devel,freerdp-devel"

# COMMANDS TO RUN AFTER
AFTER_COMMANDS="echo installing afpfs-ng libs,wget -c http://downloads.sourceforge.net/project/afpfs-ng/afpfs-ng/0.8.1/afpfs-ng-0.8.1.tar.bz2 -O /tmp/afpfs-ng-0.8.1.tar.bz2,tar -xvf /tmp/afpfs-ng-0.8.1.tar.bz2 --directory /tmp/,cd /tmp/afpfs-ng-0.8.1/,./configure,make,sudo make install,sh -c `echo '/usr/include/afpfs-ng' > /etc/ld.so.conf.d/afpfs-ng.conf`,mkdir /usr/include/afpfs-ng,cp -v /tmp/afpfs-ng-0.8.1/include/* /usr/include/afpfs-ng/,ln -s /usr/local/lib/libafpclient.so.0.0.0 /usr/lib/libafpclient.so.0,,echo installing ncpfs libs,wget -c http://archive.ubuntu.com/ubuntu/pool/universe/n/ncpfs/libncp_2.2.6-8_amd64.deb -O /tmp/libncp_2.2.6-8_amd64.deb,wget -c http://archive.ubuntu.com/ubuntu/pool/universe/n/ncpfs/libncp-dev_2.2.6-8_amd64.deb -O /tmp/libncp-dev_2.2.6-8_amd64.deb,dpkg -i /tmp/libncp_2.2.6-8_amd64.deb,dpkg -i /tmp/libncp-dev_2.2.6-8_amd64.deb,echo installing freerdp 1.2 libs,wget -c https://launchpad.net/~remmina-ppa-team/+archive/ubuntu/remmina-next/+files/libfreerdp1_1.2.0%7Egit20150207%2Bdfsg-0trusty2_amd64.deb -O /tmp/libfreerdp1_1.2.0~git20150207+dfsg-0trusty2_amd64.deb,wget -c https://launchpad.net/~remmina-ppa-team/+archive/ubuntu/remmina-next/+files/libfreerdp-plugins-standard_1.2.0%7Egit20150207%2Bdfsg-0trusty2_amd64.deb -O /tmp/libfreerdp-plugins-standard_1.2.0~git20150207+dfsg-0trusty2_amd64.deb,wget -c https://launchpad.net/~remmina-ppa-team/+archive/ubuntu/remmina-next/+files/libfreerdp-dev_1.2.0%7Egit20150207%2Bdfsg-0trusty2_amd64.deb -O /tmp/libfreerdp-dev_1.2.0~git20150207+dfsg-0trusty2_amd64.deb,sudo dpkg -i /tmp/libfreerdp1_1.2.0~git20150207+dfsg-0trusty2_amd64.deb,sudo dpkg -i /tmp/libfreerdp-plugins-standard_1.2.0~git20150207+dfsg-0trusty2_amd64.deb,sudo dpkg -i /tmp/libfreerdp-dev_1.2.0~git20150207+dfsg-0trusty2_amd64.deb,cd {INSTALL_LOCATION},./configure,make,make install"

# THIS WILL CREATE AN AUTOMATIC LAUNCHER FOR THE TOOL
LAUNCHER=""
