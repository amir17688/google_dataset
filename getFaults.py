#!/usr/bin/python

import sys
import os
from UcsSdk import *

# This script retrieve all the UCS Manager Faults.

# <Update the Credential Parameters below before executing the script>
ucsm_ip = '0.0.0.0'
user = 'username'
password = 'password'

try:
	handle = UcsHandle()
	handle.Login(ucsm_ip,user, password)

	getRsp = handle.GetManagedObject(None, FaultInst.ClassId())
	if (getRsp != None):
		WriteObject(getRsp)

	handle.Logout()

except Exception, err:
	handle.Logout()
	print "Exception:", str(err)
	import traceback, sys
	print '-'*60
	traceback.print_exc(file=sys.stdout)
	print '-'*60

