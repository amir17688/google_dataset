WIDTH = 32
SIZE = 128
NUM_BANKS = 8

def ctrl_thread():
    ram = CoramMemory(0, WIDTH, SIZE, NUM_BANKS, False)
    channel = CoramChannel(0, 32)
    addr = 0
    sum = 0
    for i in range(4):
        ram.write(0, addr, SIZE*NUM_BANKS)
        channel.write(addr)
        sum = channel.read()
        addr += (SIZE * NUM_BANKS * (WIDTH / 8))
    print('sum=', sum)

ctrl_thread()
     ioval = ioregister.read(0)
        print('ioval=',ioval)
        
    for i in range(8):
        ram.write(0, addr, 128) # from DRAM to BlockRAM
        channel.write(addr)
        sum = channel.read()
        addr += 512
    print('sum=', sum)

    ioregister.write(0, 0)
    ioregister.write(1, sum)
    
    for i in range(10000):
        pass

ctrl_thread()
