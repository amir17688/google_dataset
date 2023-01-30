#!/usr/bin/env python
#####################################
# Installation module for OWASP-ZSC
#####################################

# AUTHOR OF MODULE NAME
AUTHOR="Mauro Risonho de Paula Assumpcao (firebits)"

# DESCRIPTION OF THE MODULE
DESCRIPTION="This module will install/update OWASP-ZSC - Shellcode/Obfuscate Code Generator"

# INSTALL TYPE GIT, SVN, FILE DOWNLOAD
# OPTIONS = GIT, SVN, FILE
INSTALL_TYPE="GIT"

# LOCATION OF THE FILE OR GIT/SVN REPOSITORY
REPOSITORY_LOCATION="https://github.com/Ali-Razmjoo/OWASP-ZSC.git"

# WHERE DO YOU WANT TO INSTALL IT
INSTALL_LOCATION="owasp-zsc"

# DEPENDS FOR DEBIAN INSTALLS
DEBIAN="git"

# DEPENDS FOR FEDORA INSTALLS
FEDORA="git"

# COMMANDS TO RUN AFTER
AFTER_COMMANDS=""

# THIS WILL CREATE AN AUTOMATIC LAUNCHER FOR THE TOOL
LAUNCHER="python zsc.py"

