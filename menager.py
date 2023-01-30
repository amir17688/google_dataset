def linux86ptrace( pid, shellcode):
	from .Linux86.inject import injectmex86
	injectmex86( pid, shellcode)

def linux64ptrace( pid, shellcode):
	from .Linux64.inject import injectmex64
	injectmex64( pid, shellcode)


def winx86Codecave( exe, shellcode):
	from .Windowsx86.codecave import main
	main( exe, shellcode)


def winx86tLsDLL( exe, dll):
	from .Windowsx86.tlsInjector import main
	main( exe, dll)

def winDLL( pid, shellcode):
	from .Windows.inject import qweqwe
	qweqwe( pid, shellcode)

