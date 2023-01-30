#!/usr/bin/env python
#####################################
# Installation module for BIRP
#####################################

# AUTHOR OF MODULE NAME
AUTHOR="David Kennedy (ReL1K)"

# DESCRIPTION OF THE MODULE
DESCRIPTION="This module will install/update the BIRP - Mainframe exploitation"

# INSTALL TYPE GIT, SVN, FILE DOWNLOAD
# OPTIONS = GIT, SVN, FILE
INSTALL_TYPE="GIT"

# LOCATION OF THE FILE OR GIT/SVN REPOSITORY
REPOSITORY_LOCATION="https://github.com/sensepost/birp"

# WHERE DO YOU WANT TO INSTALL IT
INSTALL_LOCATION="birp"

# DEPENDS FOR DEBIAN INSTALLS
DEBIAN="python-pip"

# DEPENDS FOR FEDORA INSTALLS
FEDORA=""

# COMMANDS TO RUN AFTER
AFTER_COMMANDS="pip install py3270 colorama IPython"

# THIS WILL CREATE AN AUTOMATIC LAUNCHER FOR THE TOOL
LAUNCHER="birp"
