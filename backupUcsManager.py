#!/usr/bin/python
from UcsSdk import *

# This script takes the back up of UCS Manager Configuration.
# BackupUcs(type, pathPattern, timeoutSec = 600, preservePooledValues = False, dumpXml=None)
# type : full-state or config-logical or config-system or config-all
#
# Note : For "full-state" backup file name extension must be ".tar.gz" and for others ".xml"

if __name__ == "__main__":
	try:
		handle = UcsHandle()
		handle.Login("0.0.0.0", "username", "password")
		
		BackupFilePath = r"C:\Backups\configlogical.xml"
		handle.BackupUcs(type="config-logical", pathPattern=BackupFilePath)


		handle.Logout()

	except Exception, err:
		handle.Logout()
		print "Exception:", str(err)
		import traceback, sys
		print '-'*60
		traceback.print_exc(file=sys.stdout)
		print '-'*60

