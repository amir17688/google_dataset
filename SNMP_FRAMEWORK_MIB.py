# python
# This file is generated by a program (mib2py). Any edits will be lost.

from pycopia.aid import Enum
import pycopia.SMI.Basetypes
Range = pycopia.SMI.Basetypes.Range
Ranges = pycopia.SMI.Basetypes.Ranges

from pycopia.SMI.Objects import ColumnObject, MacroObject, NotificationObject, RowObject, ScalarObject, NodeObject, ModuleObject, GroupObject

# imports 
from SNMPv2_SMI import MODULE_IDENTITY, OBJECT_TYPE, OBJECT_IDENTITY, snmpModules
from SNMPv2_CONF import MODULE_COMPLIANCE, OBJECT_GROUP
from SNMPv2_TC import TEXTUAL_CONVENTION

class SNMP_FRAMEWORK_MIB(ModuleObject):
	path = '/usr/share/mibs/ietf/SNMP-FRAMEWORK-MIB'
	conformance = 5
	name = 'SNMP-FRAMEWORK-MIB'
	language = 2
	description = 'The SNMP Management Architecture MIB\n\nCopyright (C) The Internet Society (2002). This\nversion of this MIB module is part of RFC 3411;\nsee the RFC itself for full legal notices.'

# nodes
class snmpFrameworkMIB(NodeObject):
	status = 1
	OID = pycopia.SMI.Basetypes.ObjectIdentifier([1, 3, 6, 1, 6, 3, 10])
	name = 'snmpFrameworkMIB'

class snmpFrameworkAdmin(NodeObject):
	OID = pycopia.SMI.Basetypes.ObjectIdentifier([1, 3, 6, 1, 6, 3, 10, 1])
	name = 'snmpFrameworkAdmin'

class snmpAuthProtocols(NodeObject):
	status = 1
	OID = pycopia.SMI.Basetypes.ObjectIdentifier([1, 3, 6, 1, 6, 3, 10, 1, 1])
	name = 'snmpAuthProtocols'

class snmpPrivProtocols(NodeObject):
	status = 1
	OID = pycopia.SMI.Basetypes.ObjectIdentifier([1, 3, 6, 1, 6, 3, 10, 1, 2])
	name = 'snmpPrivProtocols'

class snmpFrameworkMIBObjects(NodeObject):
	OID = pycopia.SMI.Basetypes.ObjectIdentifier([1, 3, 6, 1, 6, 3, 10, 2])
	name = 'snmpFrameworkMIBObjects'

class snmpEngine(NodeObject):
	OID = pycopia.SMI.Basetypes.ObjectIdentifier([1, 3, 6, 1, 6, 3, 10, 2, 1])
	name = 'snmpEngine'

class snmpFrameworkMIBConformance(NodeObject):
	OID = pycopia.SMI.Basetypes.ObjectIdentifier([1, 3, 6, 1, 6, 3, 10, 3])
	name = 'snmpFrameworkMIBConformance'

class snmpFrameworkMIBCompliances(NodeObject):
	OID = pycopia.SMI.Basetypes.ObjectIdentifier([1, 3, 6, 1, 6, 3, 10, 3, 1])
	name = 'snmpFrameworkMIBCompliances'

class snmpFrameworkMIBGroups(NodeObject):
	OID = pycopia.SMI.Basetypes.ObjectIdentifier([1, 3, 6, 1, 6, 3, 10, 3, 2])
	name = 'snmpFrameworkMIBGroups'


# macros
# types 

class SnmpEngineID(pycopia.SMI.Basetypes.OctetString):
	status = 1
	ranges = Ranges(Range(5, 32))


class SnmpSecurityModel(pycopia.SMI.Basetypes.Integer32):
	status = 1
	ranges = Ranges(Range(0, 2147483647))


class SnmpMessageProcessingModel(pycopia.SMI.Basetypes.Integer32):
	status = 1
	ranges = Ranges(Range(0, 2147483647))


class SnmpSecurityLevel(pycopia.SMI.Basetypes.Enumeration):
	status = 1
	enumerations = [Enum(1, 'noAuthNoPriv'), Enum(2, 'authNoPriv'), Enum(3, 'authPriv')]


class SnmpAdminString(pycopia.SMI.Basetypes.OctetString):
	status = 1
	ranges = Ranges(Range(0, 255))
	format = '255t'

# scalars 
class snmpEngineID(ScalarObject):
	access = 4
	status = 1
	OID = pycopia.SMI.Basetypes.ObjectIdentifier([1, 3, 6, 1, 6, 3, 10, 2, 1, 1])
	syntaxobject = SnmpEngineID


class snmpEngineBoots(ScalarObject):
	access = 4
	status = 1
	OID = pycopia.SMI.Basetypes.ObjectIdentifier([1, 3, 6, 1, 6, 3, 10, 2, 1, 2])
	syntaxobject = pycopia.SMI.Basetypes.Integer32


class snmpEngineTime(ScalarObject):
	status = 1
	OID = pycopia.SMI.Basetypes.ObjectIdentifier([1, 3, 6, 1, 6, 3, 10, 2, 1, 3])
	syntaxobject = pycopia.SMI.Basetypes.Integer32
	access = 4
	units = 'seconds'


class snmpEngineMaxMessageSize(ScalarObject):
	access = 4
	status = 1
	OID = pycopia.SMI.Basetypes.ObjectIdentifier([1, 3, 6, 1, 6, 3, 10, 2, 1, 4])
	syntaxobject = pycopia.SMI.Basetypes.Integer32


# columns
# rows 
# notifications (traps) 
# groups 
class snmpEngineGroup(GroupObject):
	access = 2
	status = 1
	OID = pycopia.SMI.Basetypes.ObjectIdentifier([1, 3, 6, 1, 6, 3, 10, 3, 2, 1])
	group = [snmpEngineID, snmpEngineBoots, snmpEngineTime, snmpEngineMaxMessageSize]

# capabilities 

# special additions

# Add to master OIDMAP.
from pycopia import SMI
SMI.update_oidmap(__name__)
