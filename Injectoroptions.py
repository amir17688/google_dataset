from color import *

def controlset( string, argv, argv1):
	#depends to pid
	list1 = [
		"injectors/Linux86/ptrace",
		"injectors/Linux64/ptrace",
		"injectors/Windows/Dllinjector",
	]

	#depends to dll
	list2 = [
		"injectors/Windowsx86/tLsInjectorDLL",
	]

	#depends to exe
	list3 = [
		"injectors/Windowsx86/CodecaveInjector",
	]


	if len(argv) >= len(argv1):
		if len(argv) == 0:
			padd = 8
		elif len(argv) == 1:
			padd = 8
		elif len(argv) == 2:
			padd = 8
		else:
			padd = len(argv)+5
	else:
		padd = len(argv1)+5


	if string in list1:
		print (bcolors.GREEN+"""
Module options ({0}):

\tName\t\t{1}\t\tRequired\tDescription
\t----\t\t{2}\t\t--------\t-----------
\tpid\t\t{3}\t\tyes\t\tProcess ID
\tshellcode\t{4}\t\tyes\t\tInject Bytes
""".format(string,"Current Setting".ljust(padd),"---------------".ljust(padd),
	argv.ljust(padd),argv1.ljust(padd)))

	elif string in list2:
		print (bcolors.GREEN+"""
Module options ({0}):

\tName\t\t{1}\t\tRequired\tDescription
\t----\t\t{2}\t\t--------\t-----------
\texe\t\t{3}\t\tyes\t\tTarget exe file
\tdll\t\t{4}\t\tyes\t\tDll file to injection
""".format(string,"Current Setting".ljust(padd),"---------------".ljust(padd),
	argv.ljust(padd),argv1.ljust(padd)))


	elif string in list3:
		print (bcolors.GREEN+"""
Module options ({0}):

\tName\t\t{1}\t\tRequired\tDescription
\t----\t\t{2}\t\t--------\t-----------
\texe\t\t{3}\t\tyes\t\tTarget exe file
\tshellcode\t{4}\t\tyes\t\tInject Bytes
""".format(string,"Current Setting".ljust(padd),"---------------".ljust(padd),
	argv.ljust(padd),argv1.ljust(padd)))


