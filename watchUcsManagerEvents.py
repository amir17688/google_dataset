#!/usr/bin/python

from UcsSdk import *
import time

# This script shows how to monitor UCS Manager events and define your own call back to take specific action on the respective events.

ucsm_ip = '0.0.0.0'
user = 'username'
password = 'password'


def callback_all(mce):
	print 'Received a New Event with ClassId: ' + str(mce.mo.classId)
	print "ChangeList: ", mce.changeList
	print "EventId: ", mce.eventId
	
def callback_lsServer(mce):
	print 'Received a New Service Profile Event: ' + str(mce.mo.classId)
	print "ChangeList: ", mce.changeList
	print "EventId: ", mce.eventId

try:
	handle = UcsHandle()
	handle.Login(ucsm_ip,user, password)

	# Add an event handle "ev_all" to montitor the events generated by UCS Manager for any of the ClassIds
	ev_all = handle.AddEventHandler()
	
	# Get the list of active event handles.
	handle.GetEventHandlers()
		
	# Remove an event handle "ev_all"
	handle.RemoveEventHandler(ev_all)
	
	# Use your own callback method to take specific action on respective events.
	ev_all_callback = handle.AddEventHandler(callBack = callback_all)
	handle.RemoveEventHandler(ev_all_callback)
	
	# Add an event handle to filter events based on classId = lsServer
	ev_lsServer = handle.AddEventHandler(classId = "LsServer", callBack = callback_lsServer)
	handle.RemoveEventHandler(ev_lsServer)
	
	# loop that keeps the script running for us to get events/callbacks
	while True:
		time.sleep(5)

	handle.Logout()

except Exception, err:
	print "Exception:", str(err)
	import traceback, sys
	print '-'*60
	traceback.print_exc(file=sys.stdout)
	print '-'*60
	handle.Logout()
