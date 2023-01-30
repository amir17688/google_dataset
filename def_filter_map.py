# -*- coding: utf-8 -*-

_DEF_FILTER_MAP = {
    'appdef'                 : 'Filter',
    'replacementdef'         : 'ReplacementFilter',
    'windownamedef'          : 'WindowNameFilter',
    'devicevendordef'        : 'DeviceVendorFilter',
    'deviceproductdef'       : 'DeviceProductFilter',
    'inputsourcedef'         : 'InputSourceFilter',
    'vkchangeinputsourcedef' : 'InputSourceFilter',
    'modifierdef'            : 'ModifierFilter'
}

_DEFTAG_NAMETAG_MAP = {
    'appdef'                 : 'appname',
    'replacementdef'         : 'replacementname',
    'devicevendordef'        : 'vendorname',
    'deviceproductdef'       : 'productname',
    'uielementroledef'       : '',
    'windownamedef'          : 'name',
    'vkopenurldef'           : 'name',
    'inputsourcedef'         : 'name',
    'vkchangeinputsourcedef' : 'name',
}

def get_name_tag_by_def_tag(defname, d=None):
    return _DEFTAG_NAMETAG_MAP.get(defname.lower(), d)

def get_filter_by_def(defname, d=None):
    return _DEF_FILTER_MAP.get(defname.lower(), d)