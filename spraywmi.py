#!/usr/bin/env python
#####################################
# Installation module for SprayWMI
#####################################

# AUTHOR OF MODULE NAME
AUTHOR="David Kennedy (ReL1K)"

# DESCRIPTION OF THE MODULE
DESCRIPTION="This module will install/update SprayWMI - mass WMI exploitation tool"

# INSTALL TYPE GIT, SVN, FILE DOWNLOAD
# OPTIONS = GIT, SVN, FILE
INSTALL_TYPE="GIT"

# LOCATION OF THE FILE OR GIT/SVN REPOSITORY
REPOSITORY_LOCATION="https://github.com/trustedsec/spraywmi/"

# WHERE DO YOU WANT TO INSTALL IT
INSTALL_LOCATION="spraywmi"

# DEPENDS FOR DEBIAN INSTALLS
DEBIAN="libpam0g:i386,libpopt0:i386"

# DEPENDS FOR FEDORA INSTALLS
FEDORA="git"

# COMMANDS TO RUN AFTER
AFTER_COMMANDS=""

# THIS WILL CREATE AN AUTOMATIC LAUNCHER FOR THE TOOL
LAUNCHER="spraywmi"

