#!/usr/bin/env python
######################################
# Installation module for King Phisher
######################################

# AUTHOR OF MODULE NAME
AUTHOR="Spencer McIntyre (@zeroSteiner)"

# DESCRIPTION OF THE MODULE
DESCRIPTION="This module will install/update the King Phisher phishing campaign toolkit"

# INSTALL TYPE GIT, SVN, FILE DOWNLOAD
# OPTIONS = GIT, SVN, FILE
INSTALL_TYPE="GIT"

# LOCATION OF THE FILE OR GIT/SVN REPOSITORY
REPOSITORY_LOCATION="https://github.com/securestate/king-phisher/"

# WHERE DO YOU WANT TO INSTALL IT
INSTALL_LOCATION="king-phisher"

# DEPENDS FOR DEBIAN INSTALLS
DEBIAN="git"

# DEPENDS FOR FEDORA INSTALLS
FEDORA="git"

# COMMANDS TO RUN AFTER
AFTER_COMMANDS="cd {INSTALL_LOCATION},yes | pip uninstall distribute,curl -O https://svn.apache.org/repos/asf/oodt/tools/oodtsite.publisher/trunk/distribute_setup.py,python distribute_setup.py,wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O - | python,easy_install -U pip,tools/install.sh"
