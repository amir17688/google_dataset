#!/usr/bin/env python

#------------------Bombermans Team---------------------------------#
#Author  : B3mB4m
#Concat  : b3mb4m@protonmail.com
#Project : https://github.com/b3mb4m/Shellsploit
#LICENSE : https://github.com/b3mb4m/Shellsploit/blob/master/LICENSE
#------------------------------------------------------------------#

import sys
import os

name = os.sep.join([x for x in os.getcwd().split(os.sep) if x != os.getcwd().split(os.sep)[-1]])
sys.path.append(name)

if sys.version_info.major == 3:
    raw_input = input


from .control import *
from .core.logo.logo import banner
#from .core.logo.counter import * #- Will be  improved(buggy)
#Dynamic counter for shellcodes,injectors etc..
from .core.Comp import tab


shellcodeModules = {
	"linux86":
			["binsh_spawn","read","exec","chmod","tcp_bind","reverse_tcp","download&exec"],
	"linux64":
			["read","binsh_spawn","tcp_bind","reverse_tcp"],
	"linux":
			["binsh_spawn","tcp_bind","reverse_tcp","read"],
	"osx86":
			["tcp_bind","binsh_spawn","reverse_tcp"],
	"osx64":
			["reverse_tcp","tcp_bind","binsh_spawn"],
	"FreeBSDx86":
			["binsh_spawn","reverse_tcp2","reverse_tcp","read","exec","tcp_bind"],
	"FreeBSDx64":
			["binsh_spawn","tcp_bind","reverse_tcp","exec"],
	"linux_arm":
			["binsh_spawn","chmod","reverse_tcp","exec"],
	"linux_mips":
			["binsh_spawn","chmod","reverse_tcp","tcp_bind"],
	"windows":
			["messagebox","download&execute","exec", "reverse_tcp", "tcp_bind"],
	"solarisx86":
			["binsh_spawn","read","reverse_tcp","tcp_bind"],
	"injectors":
			["Linux86/ptrace","Linux64/ptrace","Windowsx86/tLsInjectorDLL",
			"Windowsx86/CodecaveInjector","Windows/Dllinjector",
	#Dllinjector is still passive.
			],
	"backdoors":
			["linux86/reverse_tcp","linux64/reverse_tcp","osx86/reverse_tcp",
			"unix/python/reverse_tcp","unix/perl/reverse_tcp",
			"unix/bash/reverse_tcp","unix/ruby/reverse_tcp"]
	}
tab.start(1)
#db = B3mB4mLogo().start()
def start():
	print (banner( "49", "12", "2", "4"))
	shellsploit()

def shellsploit():
	try:
		bash =  bcolors.OKBLUE + bcolors.UNDERLINE + "ssf" + bcolors.ENDC
		bash += bcolors.OKBLUE + " > "+ bcolors.ENDC
		terminal = raw_input(bash)

		if terminal[:4] == "help":
			from .core.help import mainhelp
			mainhelp()
			shellsploit()

		elif terminal[:14] == "show backdoors":
			from .core.backdoors import backdoorlist
			backdoorlist()
			shellsploit()

		elif terminal[:2] == "os":
			from .core.commands import oscommand
			oscommand( terminal[3:])
			shellsploit()


		elif terminal[:6] == "banner":
			print (banner( "47", "12", "2", "4"))
			shellsploit()

		elif terminal[:3] == "use":
			all_sc_modules = []
			for platforms in shellcodeModules.keys():
				for shellcodeType in shellcodeModules[platforms]:
					all_sc_modules.append("{}/{}".format(platforms,shellcodeType))
			if terminal.split()[1] in all_sc_modules:
				for shellcode in all_sc_modules:
					if terminal.split()[1] == shellcode:
						B3mB4m().control(shellcode)
						shellsploit()
			else:
				print ("\nModule not avaible !\n")
				shellsploit()


		elif terminal[:14] == "show injectors":
			from .core.lists import injectorlist
			injectorlist()
			shellsploit()

		elif terminal[:5] == "clear":
			from .core.commands import clean
			clean()
			shellsploit()

		elif terminal[:12] == "show modules":
			from .core.shellcodes import shellcodelist
			shellcodelist()
			shellsploit()


		elif terminal[:4] == "exit":
			sys.exit("\nThanks for using shellsploit !\n")

		else:
			if terminal == "":
				shellsploit()
			else:
				print (bcolors.RED + bcolors.BOLD + "[-] Unknown command: %s" % terminal + bcolors.ENDC)
				shellsploit()



	except(KeyboardInterrupt):
		print("\n[*] (Ctrl + C ) Detected, Trying To Exit ...")
		from sys import exit
		sys.exit()



def main():
	import optparse
	parser = optparse.OptionParser()
	parser.add_option('-p', '--payload', action="store")
	parser.add_option('-e', '--encoder', action="store", default="False")
	parser.add_option('-o', '--output', action="store", default=True)
	parser.add_option('-l','--list', action="store", default=True)
	parser.add_option('-n','--nc', action="store", default=True)
	parser.add_option('--host', action="store")
	parser.add_option('--port', action="store")
	(options, args) = parser.parse_args()


	if options.list == "backdoors":
		from .core.backdoors import backdoorlist
		backdoorlist( require=False)
		sys.exit()

	if options.list == "encoders":
		from .core.backdoors import encoderlist
		encoderlist( require=False)
		sys.exit()

	elif options.nc == "netcat" or options.nc == "nc":
		from .Session.netcat import nc
		if options.port:
			nc( PORT)
		else:
			nc()
		sys.exit()
	else:
		if options.payload:
			if options.host and options.port:
				from .core.backdoors import backdoorlist
				from .core.backdoors import encoderlist
				if options.payload in backdoorlist( require=True):
					from .Session.generator import process
					if "py" in options.encoder and "python" not in options.payload:
						sys.exit("\nThis encoder can not use with that payload\n")
					if options.output:
						process( options.payload, options.host, options.port, options.encoder, options.output)
					else:
						process( options.payload, options.host, options.port, options.encoder,True)
						#Default, file will be create with random name.
				else:
					sys.exit("\npython shellsploit  -p PAYLOAD -e ENCODER --host IP --port P0RT\n")
			else:
				sys.exit("\npython shellsploit  -p PAYLOAD -e ENCODER --host IP --port P0RT\n")
		else:
			start()