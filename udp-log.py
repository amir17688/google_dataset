#/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (C) Misza13 <misza1313@gmail.com>, 2007
#
# Distributed under the terms of the MIT license.
#
import sys, re, socket
__version__ = '$Id$'

TARGET_HOST = 'toolserver.org'
TARGET_PORT = 42448

input = sys.stdin.read()
log = re.search('Versions: (?P<ver>.*?)\nuid=\d+\((?P<user>\w+)\).*Log Message:\s*(?P<logmsg>.*)',input,re.DOTALL)

if log:
    print 'Routing commit data via UDP...'

    ver = log.group('ver')
    user = log.group('user')
    logmsg = log.group('logmsg').replace('\n',' ')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((TARGET_HOST,TARGET_PORT))
    sock.send('\002%s\002 commited \002%s\002 * \0032%s\003' % (user,ver,logmsg))
    sock.close()
