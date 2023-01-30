#!/usr/bin/python
from UcsSdk import *
import xml.dom.minidom

# This script associates a service profile via UCS Manager Methods.
# Parameter:
# sp		: Service Profile Name
# spDn		: Dn of Service Profile
# bladeDn	: Dn of Blade Server.
#
# NOTE: Please make sure sp, spDn and bladeDn should exist in UCS Manager before executing script.

if __name__ == "__main__":
	try:
		handle = UcsHandle()
		handle.Login("0.0.0.0", "username", "password")

		sp = "sp_name"
		spDn = "org-root/ls-sp_name"
		bladeDn = "sys/chassis-1/blade-1"

		obj = LsServer()
		obj.setattr(LsServer.DN, spDn)
		obj.setattr(LsServer.NAME, sp)
		obj.setattr(LsServer.STATUS, Status.MODIFIED)

		bindObj = LsBinding()
		bindObj.setattr(LsBinding.PN_DN, bladeDn)
		bindObj.setattr(LsBinding.RN, LsBinding().MakeRn())
		obj.AddChild(bindObj)

		inConfig = ConfigConfig()
		inConfig.AddChild(obj)

		ccm = handle.ConfigConfMo(obj.Dn, inConfig)
		if ccm.errorCode == 0:
			moList = []
			for child in ccm.OutConfig.GetChild():
				moList.append(child)
			WriteObject(moList)
		else:
			WriteUcsWarning('[Error]: ConfigConfMo [Code]:' + ccm.errorCode + ' [Description]:' + ccm.errorDescr)

		handle.Logout()

	except Exception, err:
		print "Exception:", str(err)
		import traceback, sys
		print '-'*60
		traceback.print_exc(file=sys.stdout)
		print '-'*60
