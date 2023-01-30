#!/usr/bin/python

import sys
import os
from UcsSdk import *

# This script shows the use of UCS Manager method "ConfigResolveChildren"
# Usage: method_ConfigResolveChildren.py parentDn

basename = os.path.basename (sys.argv[0])

if (len(sys.argv) != 2):
	print "Usage: %s parentDn" % basename
	sys.exit()

ucsm_ip = '0.0.0.0'
user = 'username'
password = 'password'

parentDn = sys.argv[1]

try:
	handle = UcsHandle()
	handle.Login(ucsm_ip,user, password)

	crc = handle.ConfigResolveChildren(FcpoolInitiators.ClassId(), parentDn, None, YesOrNo.TRUE, True)
	if (crc.errorCode == 0):
		moList = []
		for child in crc.OutConfigs.GetChild():
			if (isinstance(child, ManagedObject) == True):
				moList.append(child)
		WriteObject(moList)

	handle.Logout()

except Exception, err:
	print "Exception:", str(err)
	import traceback, sys
	print '-'*60
	traceback.print_exc(file=sys.stdout)
	print '-'*60
