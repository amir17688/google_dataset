#!/usr/bin/python
from UcsSdk import *

# This script shows the use of Generic Operation with Managed Object.
# GetManagedObject 		: Retrieves the Managed Object information from UCS Manager.
# AddManagedObject 		: Adds the Managed Object to UCS Manager.
# SetManagedObject 		: Modify the Property of an existing Managed Object of UCS Manager.
# RemoveManagedObject 	: Removes the Managed Object from UCS Manager.

if __name__ == "__main__":
	try:
		handle = UcsHandle()
		#handle.Login("0.0.0.0","username","password")
		
		# returns a list of all the org Mos at Level 1
		getRsp = handle.GetManagedObject(None, OrgOrg.ClassId(),{OrgOrg.LEVEL:"1"})

		# adds a service profile sp_name with-in every Org returned in the previous operation
		addRsp = handle.AddManagedObject(getRsp, LsServer.ClassId(), { LsServer.NAME :"sp_name"}, True)

		# sets the descriptor of every mo returned by AddManagedObject
		setRsp = handle.SetManagedObject(addRsp, LsServer.ClassId(), {LsServer.DESCR:"sp_description"})

		# removes all the service profiles we had added
		removeRsp = handle.RemoveManagedObject(addRsp)

		handle.Logout()

	except Exception, err:
		handle.Logout()
		print "Exception:", str(err)
		import traceback, sys
		print '-'*60
		traceback.print_exc(file=sys.stdout)
		print '-'*60
