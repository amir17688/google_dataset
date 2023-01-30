#!/usr/bin/python

"""Gets a bunch of info about the current machine"""

import os
import platform
import plistlib
import subprocess


def hardware_info():
    '''Returns system_profiler hardware info as a dictionary'''
    cmd = ['/usr/sbin/system_profiler', 'SPHardwareDataType', '-xml']
    output = subprocess.check_output(cmd)

    info = plistlib.readPlistFromString(output)

    hardware_info = info[0]['_items'][0]
    return hardware_info


def list_users():
    '''Returns home directories in /Users'''
    users_dir = os.listdir('/Users')
    home_dirs = [item for item in users_dir 
                 if not item.startswith('.') and item != 'Shared']
    return home_dirs


def disk_info():
    '''Returns a tuple with size of startup disk and free space in bytes'''
    cmd = ['/usr/sbin/diskutil', 'info', '-plist', '/']
    output = subprocess.check_output(cmd)

    info = plistlib.readPlistFromString(output)
    total_size = info['TotalSize']
    free_space = info['FreeSpace']
    return (total_size, free_space)


def main():
    hw_info = hardware_info()
    processor = hw_info['cpu_type'] + ' ' + hw_info['current_processor_speed']
    (disk_size, free_space) = disk_info()
    info = {}
    info['Host name'] = os.uname()[1]
    info['Serial number'] = hw_info['serial_number']
    info['Machine model'] = hw_info['machine_model']
    info['Processor'] = processor
    info['Memory'] = hw_info['physical_memory']
    info['Users'] = list_users()
    info['Disk size'] = disk_size
    info['Disk free space'] = free_space
    info['OS version'] = platform.mac_ver()[0]

    for key, value in info.items():
        print '%s: %s' % (key, value)


if __name__ == "__main__":
    main()