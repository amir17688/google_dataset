#createvm.py
#
#
#
#
#
#

import sys
print ("\n".join(sys.path))

from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import time
import vmutils
import subprocess
import configparser
import json
from passlib.hash import md5_crypt
import os
import re

#checkHostname()
#checks that the hostname is a valid hostname, and that the hostname is not already in use
#current rules: a VM name must be 5 to 20 characters in length, and VM names can contain letters, numbers, underscores and dashes.
def checkHostname(hostname):
        validString = re.search(r'^(?i)[A-Za-z0-9_-]{%s,%s}$' %(5, 20), hostname)
        #print(validString)
        if (validString == None):
            return False
        else:
            return True
        
#checkRecipe()
#checks that the recipe is defined (i.e., in the list derived from the comma-separated "recipes" string in the config file)
def checkRecipe(configParser, recipe):
        recipes = configParser.get('cocreate_config', 'recipes').split(',')
        if (recipe in recipes):
            return True
        else:
            return False

#cloneVM()
#provides routine for cloning the base VM
def cloneVM(configParser, hostname):
        folder = configParser.get('knife_parameters', 'folder')
        template = configParser.get('knife_parameters', 'template')
        cspec = configParser.get('knife_parameters', 'cspec')
        domain = configParser.get('knife_parameters','domain')
        config = configParser.get('knife_parameters','config')
        knifeargcreate = 'knife vsphere vm clone ' +  hostname +  ' --config '+ config+ ' --template '+ template + ' --folder '+folder+' --cspec '+cspec+' --chostname '+hostname+' --cdomain '+domain+' --start'
        subprocess.check_call(knifeargcreate, shell=True)

#getIP()
#provides routine for getting the IP address of the new VM
def getIP(configParser, hostname):
        vchost = configParser.get('pyvmomi_config', 'vchost')
        vcuser = configParser.get('pyvmomi_config', 'vcuser')
        vcpassword = configParser.get('pyvmomi_config', 'vcpassword')
        vcport = configParser.get('pyvmomi_config', 'vcport')
        si = SmartConnect(host=vchost, user=vcuser,pwd=vcpassword, port=vcport)
        vm = vmutils.get_vm_by_name(si, hostname)
        ipAddress= vm.summary.guest.ipAddress
        while(not isinstance(ipAddress, str)):
                ipAddress= vm.summary.guest.ipAddress
        return ipAddress

#bootstrapVM()
#provides routine for bootstrapping the new VM using knife bootstrap
def bootstrapVM(configParser, ipAddress, hostname, recipe):
        recipes = "recipe[" + recipe + "]"
        sshuser = configParser.get('knife_parameters', 'sshuser')
        sshpassword = configParser.get('knife_parameters', 'sshpassword')
        config = configParser.get('knife_parameters','config')
        secretkeyfile = configParser.get('knife_parameters', 'secretkey')
        bootstrapargcreate = 'knife bootstrap '+ ipAddress+' --config '+ config+ ' --node-name '+ hostname +' --ssh-user '+sshuser+ ' --ssh-password '+sshpassword+ ' --secret-file '+ secretkeyfile+ ' --sudo --use-sudo-password -r '+ recipes
        subprocess.check_call(bootstrapargcreate, shell=True)

#createVM()
#creates the VM using the broken down functions
#Returns the VM IP and FQDN if successful or None values (and an error message) if not. Also returns progress value.
def createVM(request_id, hostname, recipe, updateProgress):
        configParser = configparser.RawConfigParser()
        configFilePath = r'/opt/chef-tools/createvm/createvm.config'
        configParser.read(configFilePath)
        
        subdomain = configParser.get('cocreate_config', 'subdomain')
        progress = 0
        
        validHostname = checkHostname(hostname)
        if(validHostname == False):
            return None, None, 'Invalid hostname', progress
        
        fqdn = hostname + "." + subdomain
        
        validRecipe = checkRecipe(configParser, recipe)
        if(validRecipe == False):
            return None, None, 'Unsupported template', progress
        
        updateProgress(request_id, progress, "Beginning VM template cloning")
        try:
            cloneVM(configParser, hostname)
        except subprocess.CalledProcessError:
            print("A cloning error occurred")
            return None, None, 'VM cloning failed', progress
        
        progress = 33
        
        updateProgress(request_id, progress, "Waiting for new VM IP address")
        ipAddress = None
        try:
            ipAddress = getIP(configParser, hostname)
        except:
            print("Could not get IP Address")
            return None, None, 'Could not obtain VM IP address', progress
        
        progress = 67
        
        updateProgress(request_id, progress, "Beginning VM bootstrap")
        try:
            bootstrapVM(configParser, ipAddress, hostname, recipe)
        except subprocess.CalledProcessError:
            print("An error occurred during bootstrap")
            return None, None, 'VM bootstrap failed', progress
        
        # The URL may not be relevant for bare VM sandboxes (which are not yet supported).
        url = "http://" + fqdn + "/" + recipe
        
        progress = 100
        
        updateProgress(request_id, progress, "VM creation complete", url)
        return ipAddress, fqdn, None, progress
    
        #Code snippets for adding databags
        #Create the databag for the user by creating a json with their information and running a knife command
        #hashPass = md5_crypt.encrypt("password")
        #filename = dnsName + ".json"
        #with open(filename, 'w+') as outfile:
                #json.dump({"id": dnsName, "username": "username", "password": hashPass}, outfile)

        #configParser = configparser.RawConfigParser()
        #configFilePath = r'/opt/chef-tools/createvm/createvm.config'
        #configParser.read(configFilePath)

        #userInfo = configParser.get('knife_parameters','databag')
        #secretkeyfile = configParser.get('knife_parameters', 'secretkey')
        #config = configParser.get('knife_parameters','config')
        #knifeAddDatabag = 'knife data bag from file ' + userInfo+ ' '+ filename+ ' --secret-file '+ secretkeyfile + ' -d  --config '+ config 
        #sts1 =  os.system(knifeAddDatabag)