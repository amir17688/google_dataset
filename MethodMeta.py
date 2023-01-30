from UcsHandle import *

_MethodFactoryMeta = {

	"AaaChangeSelfPassword": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InConfirmNewPassword":UcsFactoryMeta("InConfirmNewPassword", "inConfirmNewPassword", "Xs:string", "Version142b", "Input", False),
		"InNewPassword":UcsFactoryMeta("InNewPassword", "inNewPassword", "Xs:string", "Version142b", "Input", False),
		"InOldPassword":UcsFactoryMeta("InOldPassword", "inOldPassword", "Xs:string", "Version142b", "Input", False),
		"InUserName":UcsFactoryMeta("InUserName", "inUserName", "Xs:string", "Version142b", "Input", False),
		"OutStatus":UcsFactoryMeta("OutStatus", "outStatus", "Xs:string", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("AaaChangeSelfPassword","aaaChangeSelfPassword", "Version142b"),
	},

	"AaaCheckComputeAuthToken": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InToken":UcsFactoryMeta("InToken", "inToken", "Xs:string", "Version142b", "Input", False),
		"InUser":UcsFactoryMeta("InUser", "inUser", "Xs:string", "Version142b", "Input", False),
		"OutAllow":UcsFactoryMeta("OutAllow", "outAllow", "Xs:string", "Version142b", "Output", False),
		"OutAuthDomain":UcsFactoryMeta("OutAuthDomain", "outAuthDomain", "Xs:string", "Version142b", "Output", False),
		"OutAuthUser":UcsFactoryMeta("OutAuthUser", "outAuthUser", "Xs:string", "Version142b", "Output", False),
		"OutLocales":UcsFactoryMeta("OutLocales", "outLocales", "Xs:string", "Version142b", "Output", False),
		"OutPriv":UcsFactoryMeta("OutPriv", "outPriv", "Xs:string", "Version142b", "Output", False),
		"OutRemote":UcsFactoryMeta("OutRemote", "outRemote", "Xs:string", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("AaaCheckComputeAuthToken","aaaCheckComputeAuthToken", "Version142b"),
	},

	"AaaCheckComputeExtAccess": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InDn":UcsFactoryMeta("InDn", "inDn", "ReferenceObject", "Version142b", "Input", False),
		"InUser":UcsFactoryMeta("InUser", "inUser", "Xs:string", "Version142b", "Input", False),
		"OutAllow":UcsFactoryMeta("OutAllow", "outAllow", "Xs:string", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("AaaCheckComputeExtAccess","aaaCheckComputeExtAccess", "Version142b"),
	},

	"AaaGetAuthTokenClient": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InCookie":UcsFactoryMeta("InCookie", "inCookie", "Xs:string", "Version142b", "Input", False),
		"OutTokens":UcsFactoryMeta("OutTokens", "outTokens", "Xs:string", "Version142b", "Output", False),
		"OutUser":UcsFactoryMeta("OutUser", "outUser", "Xs:string", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("AaaGetAuthTokenClient","aaaGetAuthTokenClient", "Version142b"),
	},

	"AaaGetNComputeAuthTokenByDn": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InCookie":UcsFactoryMeta("InCookie", "inCookie", "Xs:string", "Version142b", "Input", False),
		"InDn":UcsFactoryMeta("InDn", "inDn", "Xs:string", "Version142b", "Input", False),
		"InNumberOf":UcsFactoryMeta("InNumberOf", "inNumberOf", "Xs:unsignedByte", "Version142b", "Input", False),
		"OutTokens":UcsFactoryMeta("OutTokens", "outTokens", "Xs:string", "Version142b", "Output", False),
		"OutUser":UcsFactoryMeta("OutUser", "outUser", "Xs:string", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("AaaGetNComputeAuthTokenByDn","aaaGetNComputeAuthTokenByDn", "Version142b"),
	},

	"AaaKeepAlive": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Meta":UcsFactoryMethodMeta("AaaKeepAlive","aaaKeepAlive", "Version142b"),
	},

	"AaaLogin": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InName":UcsFactoryMeta("InName", "inName", "Xs:string", "Version142b", "Input", False),
		"InPassword":UcsFactoryMeta("InPassword", "inPassword", "Xs:string", "Version142b", "Input", False),
		"OutChannel":UcsFactoryMeta("OutChannel", "outChannel", "Xs:string", "Version142b", "Output", False),
		"OutCookie":UcsFactoryMeta("OutCookie", "outCookie", "Xs:string", "Version142b", "Output", False),
		"OutDomains":UcsFactoryMeta("OutDomains", "outDomains", "Xs:string", "Version142b", "Output", False),
		"OutEvtChannel":UcsFactoryMeta("OutEvtChannel", "outEvtChannel", "Xs:string", "Version142b", "Output", False),
		"OutPriv":UcsFactoryMeta("OutPriv", "outPriv", "Xs:string", "Version142b", "Output", False),
		"OutRefreshPeriod":UcsFactoryMeta("OutRefreshPeriod", "outRefreshPeriod", "Xs:unsignedInt", "Version142b", "Output", False),
		"OutSessionId":UcsFactoryMeta("OutSessionId", "outSessionId", "Xs:string", "Version142b", "Output", False),
		"OutVersion":UcsFactoryMeta("OutVersion", "outVersion", "Xs:string", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("AaaLogin","aaaLogin", "Version142b"),
	},

	"AaaLogout": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InCookie":UcsFactoryMeta("InCookie", "inCookie", "Xs:string", "Version142b", "Input", False),
		"OutStatus":UcsFactoryMeta("OutStatus", "outStatus", "Xs:string", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("AaaLogout","aaaLogout", "Version142b"),
	},

	"AaaRefresh": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InCookie":UcsFactoryMeta("InCookie", "inCookie", "Xs:string", "Version142b", "Input", False),
		"InName":UcsFactoryMeta("InName", "inName", "Xs:string", "Version142b", "Input", False),
		"InPassword":UcsFactoryMeta("InPassword", "inPassword", "Xs:string", "Version142b", "Input", False),
		"OutChannel":UcsFactoryMeta("OutChannel", "outChannel", "Xs:string", "Version142b", "Output", False),
		"OutCookie":UcsFactoryMeta("OutCookie", "outCookie", "Xs:string", "Version142b", "Output", False),
		"OutDomains":UcsFactoryMeta("OutDomains", "outDomains", "Xs:string", "Version142b", "Output", False),
		"OutEvtChannel":UcsFactoryMeta("OutEvtChannel", "outEvtChannel", "Xs:string", "Version142b", "Output", False),
		"OutPriv":UcsFactoryMeta("OutPriv", "outPriv", "Xs:string", "Version142b", "Output", False),
		"OutRefreshPeriod":UcsFactoryMeta("OutRefreshPeriod", "outRefreshPeriod", "Xs:unsignedInt", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("AaaRefresh","aaaRefresh", "Version142b"),
	},

	"AaaTokenLogin": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InName":UcsFactoryMeta("InName", "inName", "Xs:string", "Version142b", "Input", False),
		"InToken":UcsFactoryMeta("InToken", "inToken", "Xs:string", "Version142b", "Input", False),
		"OutChannel":UcsFactoryMeta("OutChannel", "outChannel", "Xs:string", "Version142b", "Output", False),
		"OutCookie":UcsFactoryMeta("OutCookie", "outCookie", "Xs:string", "Version142b", "Output", False),
		"OutDomains":UcsFactoryMeta("OutDomains", "outDomains", "Xs:string", "Version142b", "Output", False),
		"OutEvtChannel":UcsFactoryMeta("OutEvtChannel", "outEvtChannel", "Xs:string", "Version142b", "Output", False),
		"OutPriv":UcsFactoryMeta("OutPriv", "outPriv", "Xs:string", "Version142b", "Output", False),
		"OutRefreshPeriod":UcsFactoryMeta("OutRefreshPeriod", "outRefreshPeriod", "Xs:unsignedInt", "Version142b", "Output", False),
		"OutSessionId":UcsFactoryMeta("OutSessionId", "outSessionId", "Xs:string", "Version142b", "Output", False),
		"OutUser":UcsFactoryMeta("OutUser", "outUser", "Xs:string", "Version142b", "Output", False),
		"OutVersion":UcsFactoryMeta("OutVersion", "outVersion", "Xs:string", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("AaaTokenLogin","aaaTokenLogin", "Version142b"),
	},

	"AaaTokenRefresh": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InCookie":UcsFactoryMeta("InCookie", "inCookie", "Xs:string", "Version142b", "Input", False),
		"InName":UcsFactoryMeta("InName", "inName", "Xs:string", "Version142b", "Input", False),
		"OutChannel":UcsFactoryMeta("OutChannel", "outChannel", "Xs:string", "Version142b", "Output", False),
		"OutCookie":UcsFactoryMeta("OutCookie", "outCookie", "Xs:string", "Version142b", "Output", False),
		"OutDomains":UcsFactoryMeta("OutDomains", "outDomains", "Xs:string", "Version142b", "Output", False),
		"OutEvtChannel":UcsFactoryMeta("OutEvtChannel", "outEvtChannel", "Xs:string", "Version142b", "Output", False),
		"OutPriv":UcsFactoryMeta("OutPriv", "outPriv", "Xs:string", "Version142b", "Output", False),
		"OutRefreshPeriod":UcsFactoryMeta("OutRefreshPeriod", "outRefreshPeriod", "Xs:unsignedInt", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("AaaTokenRefresh","aaaTokenRefresh", "Version142b"),
	},

	"ApeBootPnuOs": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InConfig":UcsFactoryMeta("InConfig", "inConfig", "ConfigConfig", "Version142b", "Input", True),
		"Meta":UcsFactoryMethodMeta("ApeBootPnuOs","apeBootPnuOs", "Version142b"),
	},

	"ApeConfigureCMCLIF": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InConfig":UcsFactoryMeta("InConfig", "inConfig", "ConfigConfig", "Version142b", "Input", True),
		"Meta":UcsFactoryMethodMeta("ApeConfigureCMCLIF","apeConfigureCMCLIF", "Version142b"),
	},

	"ApeCreateHVVnic": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InBladeSlotId":UcsFactoryMeta("InBladeSlotId", "inBladeSlotId", "Xs:unsignedInt", "Version142b", "Input", False),
		"InChassisId":UcsFactoryMeta("InChassisId", "inChassisId", "Xs:unsignedInt", "Version142b", "Input", False),
		"InConfig":UcsFactoryMeta("InConfig", "inConfig", "ConfigConfig", "Version142b", "Input", True),
		"InSwId":UcsFactoryMeta("InSwId", "inSwId", "Xs:string", "Version142b", "Input", False),
		"Meta":UcsFactoryMethodMeta("ApeCreateHVVnic","apeCreateHVVnic", "Version142b"),
	},

	"ApeCreateSfish": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InBladeSlotId":UcsFactoryMeta("InBladeSlotId", "inBladeSlotId", "Xs:unsignedInt", "Version142b", "Input", False),
		"InChassisId":UcsFactoryMeta("InChassisId", "inChassisId", "Xs:unsignedInt", "Version142b", "Input", False),
		"InConfig":UcsFactoryMeta("InConfig", "inConfig", "ConfigConfig", "Version142b", "Input", True),
		"InSwId":UcsFactoryMeta("InSwId", "inSwId", "Xs:string", "Version142b", "Input", False),
		"Meta":UcsFactoryMethodMeta("ApeCreateSfish","apeCreateSfish", "Version142b"),
	},

	"ApeCreateVMVnic": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InBladeSlotId":UcsFactoryMeta("InBladeSlotId", "inBladeSlotId", "Xs:unsignedInt", "Version142b", "Input", False),
		"InChassisId":UcsFactoryMeta("InChassisId", "inChassisId", "Xs:unsignedInt", "Version142b", "Input", False),
		"InConfig":UcsFactoryMeta("InConfig", "inConfig", "ConfigConfig", "Version142b", "Input", True),
		"InSwId":UcsFactoryMeta("InSwId", "inSwId", "Xs:string", "Version142b", "Input", False),
		"Meta":UcsFactoryMethodMeta("ApeCreateVMVnic","apeCreateVMVnic", "Version142b"),
	},

	"ApeDeleteHVVnic": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InVnicDn":UcsFactoryMeta("InVnicDn", "inVnicDn", "ReferenceObject", "Version142b", "Input", False),
		"Meta":UcsFactoryMethodMeta("ApeDeleteHVVnic","apeDeleteHVVnic", "Version142b"),
	},

	"ApeDeleteSfish": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InVmSwitchDn":UcsFactoryMeta("InVmSwitchDn", "inVmSwitchDn", "ReferenceObject", "Version142b", "Input", False),
		"Meta":UcsFactoryMethodMeta("ApeDeleteSfish","apeDeleteSfish", "Version142b"),
	},

	"ApeDeleteVMVnic": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InVnicDn":UcsFactoryMeta("InVnicDn", "inVnicDn", "ReferenceObject", "Version142b", "Input", False),
		"Meta":UcsFactoryMethodMeta("ApeDeleteVMVnic","apeDeleteVMVnic", "Version142b"),
	},

	"ApeGetAdaptorConnectivity": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InFruModel":UcsFactoryMeta("InFruModel", "inFruModel", "Xs:string", "Version142b", "Input", False),
		"InFruSerial":UcsFactoryMeta("InFruSerial", "inFruSerial", "Xs:string", "Version142b", "Input", False),
		"InFruVendor":UcsFactoryMeta("InFruVendor", "inFruVendor", "Xs:string", "Version142b", "Input", False),
		"OutConfig":UcsFactoryMeta("OutConfig", "outConfig", "ConfigConfig", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ApeGetAdaptorConnectivity","apeGetAdaptorConnectivity", "Version142b"),
	},

	"ApeGetPnuOSInventory": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InFruModel":UcsFactoryMeta("InFruModel", "inFruModel", "Xs:string", "Version142b", "Input", False),
		"InFruSerial":UcsFactoryMeta("InFruSerial", "inFruSerial", "Xs:string", "Version142b", "Input", False),
		"InFruVendor":UcsFactoryMeta("InFruVendor", "inFruVendor", "Xs:string", "Version142b", "Input", False),
		"OutOutConfig":UcsFactoryMeta("OutOutConfig", "outOutConfig", "ConfigConfig", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ApeGetPnuOSInventory","apeGetPnuOSInventory", "Version142b"),
	},

	"ApeGetSwitchApeFru": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InSwId":UcsFactoryMeta("InSwId", "inSwId", "Xs:string", "Version142b", "Input", False),
		"OutControllerId":UcsFactoryMeta("OutControllerId", "outControllerId", "Xs:string", "Version142b", "Output", False),
		"OutControllerType":UcsFactoryMeta("OutControllerType", "outControllerType", "Xs:string", "Version142b", "Output", False),
		"OutControllerVendor":UcsFactoryMeta("OutControllerVendor", "outControllerVendor", "Xs:string", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("ApeGetSwitchApeFru","apeGetSwitchApeFru", "Version142b"),
	},

	"ApeInjectStimuli": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InFromSvc":UcsFactoryMeta("InFromSvc", "inFromSvc", "Xs:unsignedInt", "Version142b", "Input", False),
		"InStimuli":UcsFactoryMeta("InStimuli", "inStimuli", "MethodSet", "Version142b", "Input", True),
		"InToSvc":UcsFactoryMeta("InToSvc", "inToSvc", "Xs:unsignedInt", "Version142b", "Input", False),
		"Meta":UcsFactoryMethodMeta("ApeInjectStimuli","apeInjectStimuli", "Version142b"),
	},

	"ApeInsertNewChassis": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InConfig":UcsFactoryMeta("InConfig", "inConfig", "ConfigConfig", "Version142b", "Input", True),
		"InIsRefresh":UcsFactoryMeta("InIsRefresh", "inIsRefresh", "Xs:unsignedInt", "Version142b", "Input", False),
		"InSwId":UcsFactoryMeta("InSwId", "inSwId", "Xs:string", "Version142b", "Input", False),
		"InSwPortId":UcsFactoryMeta("InSwPortId", "inSwPortId", "Xs:unsignedInt", "Version142b", "Input", False),
		"InSwSlotId":UcsFactoryMeta("InSwSlotId", "inSwSlotId", "Xs:unsignedInt", "Version142b", "Input", False),
		"Meta":UcsFactoryMethodMeta("ApeInsertNewChassis","apeInsertNewChassis", "Version142b"),
	},

	"ApeInsertNewFex": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InConfig":UcsFactoryMeta("InConfig", "inConfig", "ConfigConfig", "Version142b", "Input", True),
		"InIsRefresh":UcsFactoryMeta("InIsRefresh", "inIsRefresh", "Xs:unsignedInt", "Version142b", "Input", False),
		"InSwId":UcsFactoryMeta("InSwId", "inSwId", "Xs:string", "Version142b", "Input", False),
		"InSwPortId":UcsFactoryMeta("InSwPortId", "inSwPortId", "Xs:unsignedInt", "Version142b", "Input", False),
		"InSwSlotId":UcsFactoryMeta("InSwSlotId", "inSwSlotId", "Xs:unsignedInt", "Version142b", "Input", False),
		"Meta":UcsFactoryMethodMeta("ApeInsertNewFex","apeInsertNewFex", "Version142b"),
	},

	"ApeInsertNewRack": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InConfig":UcsFactoryMeta("InConfig", "inConfig", "ConfigConfig", "Version142b", "Input", True),
		"InFxId":UcsFactoryMeta("InFxId", "inFxId", "Xs:unsignedInt", "Version142b", "Input", False),
		"InFxPortId":UcsFactoryMeta("InFxPortId", "inFxPortId", "Xs:unsignedInt", "Version142b", "Input", False),
		"InFxSlotId":UcsFactoryMeta("InFxSlotId", "inFxSlotId", "Xs:unsignedInt", "Version142b", "Input", False),
		"InIsRefresh":UcsFactoryMeta("InIsRefresh", "inIsRefresh", "Xs:unsignedInt", "Version142b", "Input", False),
		"Meta":UcsFactoryMethodMeta("ApeInsertNewRack","apeInsertNewRack", "Version142b"),
	},

	"ApeIssueChassisId": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InConfig":UcsFactoryMeta("InConfig", "inConfig", "ConfigConfig", "Version142b", "Input", True),
		"Meta":UcsFactoryMethodMeta("ApeIssueChassisId","apeIssueChassisId", "Version142b"),
	},

	"ApeIssueFexId": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InConfig":UcsFactoryMeta("InConfig", "inConfig", "ConfigConfig", "Version142b", "Input", True),
		"Meta":UcsFactoryMethodMeta("ApeIssueFexId","apeIssueFexId", "Version142b"),
	},

	"ApeIssueRackId": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InConfig":UcsFactoryMeta("InConfig", "inConfig", "ConfigConfig", "Version142b", "Input", True),
		"Meta":UcsFactoryMethodMeta("ApeIssueRackId","apeIssueRackId", "Version142b"),
	},

	"ApeMcGet": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InMcAddress":UcsFactoryMeta("InMcAddress", "inMcAddress", "AddressIPv4", "Version142b", "Input", False),
		"OutConfigs":UcsFactoryMeta("OutConfigs", "outConfigs", "ConfigSet", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ApeMcGet","apeMcGet", "Version142b"),
	},

	"ApeMcGetBiosTokens": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InChassisId":UcsFactoryMeta("InChassisId", "inChassisId", "Xs:unsignedInt", "Version142b", "Input", False),
		"InSlotId":UcsFactoryMeta("InSlotId", "inSlotId", "Xs:unsignedInt", "Version142b", "Input", False),
		"OutFilePath":UcsFactoryMeta("OutFilePath", "outFilePath", "Xs:string", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("ApeMcGetBiosTokens","apeMcGetBiosTokens", "Version142b"),
	},

	"ApeMcGetSmbios": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InChassisId":UcsFactoryMeta("InChassisId", "inChassisId", "Xs:unsignedInt", "Version142b", "Input", False),
		"InSlotId":UcsFactoryMeta("InSlotId", "inSlotId", "Xs:unsignedInt", "Version142b", "Input", False),
		"InUpdateCnt":UcsFactoryMeta("InUpdateCnt", "inUpdateCnt", "Xs:int", "Version142b", "Input", False),
		"OutFilePath":UcsFactoryMeta("OutFilePath", "outFilePath", "Xs:string", "Version142b", "Output", False),
		"OutUpdateCnt":UcsFactoryMeta("OutUpdateCnt", "outUpdateCnt", "Xs:int", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("ApeMcGetSmbios","apeMcGetSmbios", "Version142b"),
	},

	"ApeMcSet": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InConfig":UcsFactoryMeta("InConfig", "inConfig", "ConfigConfig", "Version142b", "Input", True),
		"Meta":UcsFactoryMethodMeta("ApeMcSet","apeMcSet", "Version142b"),
	},

	"ApeMuxOffline": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InChId":UcsFactoryMeta("InChId", "inChId", "Xs:unsignedInt", "Version142b", "Input", False),
		"InMuxSlotId":UcsFactoryMeta("InMuxSlotId", "inMuxSlotId", "Xs:unsignedInt", "Version142b", "Input", False),
		"Meta":UcsFactoryMethodMeta("ApeMuxOffline","apeMuxOffline", "Version142b"),
	},

	"ApeSetServerLifeCycle": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InFruModel":UcsFactoryMeta("InFruModel", "inFruModel", "Xs:string", "Version142b", "Input", False),
		"InFruSerial":UcsFactoryMeta("InFruSerial", "inFruSerial", "Xs:string", "Version142b", "Input", False),
		"InFruVendor":UcsFactoryMeta("InFruVendor", "inFruVendor", "Xs:string", "Version142b", "Input", False),
		"InServerLc":UcsFactoryMeta("InServerLc", "inServerLc", "Xs:string", "Version142b", "Input", False),
		"Meta":UcsFactoryMethodMeta("ApeSetServerLifeCycle","apeSetServerLifeCycle", "Version142b"),
	},

	"ApeSetSwitchInventory": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InConfig":UcsFactoryMeta("InConfig", "inConfig", "ConfigConfig", "Version142b", "Input", True),
		"InSwId":UcsFactoryMeta("InSwId", "inSwId", "Xs:string", "Version142b", "Input", False),
		"Meta":UcsFactoryMethodMeta("ApeSetSwitchInventory","apeSetSwitchInventory", "Version142b"),
	},

	"ComputeGetInventory": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InFaultsOnly":UcsFactoryMeta("InFaultsOnly", "inFaultsOnly", "Xs:string", "Version142b", "Input", False),
		"OutBladeCapProviderConfig":UcsFactoryMeta("OutBladeCapProviderConfig", "outBladeCapProviderConfig", "ConfigSet", "Version142b", "Output", True),
		"OutChassisCapProviderConfig":UcsFactoryMeta("OutChassisCapProviderConfig", "outChassisCapProviderConfig", "ConfigSet", "Version142b", "Output", True),
		"OutChassisConfig":UcsFactoryMeta("OutChassisConfig", "outChassisConfig", "ConfigSet", "Version142b", "Output", True),
		"OutFIConfig":UcsFactoryMeta("OutFIConfig", "outFIConfig", "ConfigSet", "Version142b", "Output", True),
		"OutFaultsOnly":UcsFactoryMeta("OutFaultsOnly", "outFaultsOnly", "Xs:string", "Version142b", "Output", False),
		"OutFexCapProviderConfig":UcsFactoryMeta("OutFexCapProviderConfig", "outFexCapProviderConfig", "ConfigSet", "Version142b", "Output", True),
		"OutFexConfig":UcsFactoryMeta("OutFexConfig", "outFexConfig", "ConfigSet", "Version142b", "Output", True),
		"OutGemCapProviderConfig":UcsFactoryMeta("OutGemCapProviderConfig", "outGemCapProviderConfig", "ConfigSet", "Version142b", "Output", True),
		"OutIOCardCapProviderConfig":UcsFactoryMeta("OutIOCardCapProviderConfig", "outIOCardCapProviderConfig", "ConfigSet", "Version142b", "Output", True),
		"OutLogicalConfig":UcsFactoryMeta("OutLogicalConfig", "outLogicalConfig", "ConfigSet", "Version142b", "Output", True),
		"OutMgmtIfConfig":UcsFactoryMeta("OutMgmtIfConfig", "outMgmtIfConfig", "ConfigSet", "Version142b", "Output", True),
		"OutPhysicalConfig":UcsFactoryMeta("OutPhysicalConfig", "outPhysicalConfig", "ConfigSet", "Version142b", "Output", True),
		"OutRackUnitCapProviderConfig":UcsFactoryMeta("OutRackUnitCapProviderConfig", "outRackUnitCapProviderConfig", "ConfigSet", "Version142b", "Output", True),
		"OutSwitchCapProviderConfig":UcsFactoryMeta("OutSwitchCapProviderConfig", "outSwitchCapProviderConfig", "ConfigSet", "Version142b", "Output", True),
		"OutTopSystemConfig":UcsFactoryMeta("OutTopSystemConfig", "outTopSystemConfig", "ConfigConfig", "Version142b", "Output", True),
		"OutTotalFaults":UcsFactoryMeta("OutTotalFaults", "outTotalFaults", "Xs:unsignedLong", "Version142b", "Output", False),
		"OutTypedFaultHolderConfig":UcsFactoryMeta("OutTypedFaultHolderConfig", "outTypedFaultHolderConfig", "ConfigSet", "Version142b", "Output", True),
		"OutVnicIpv4PooledAddrConfig":UcsFactoryMeta("OutVnicIpv4PooledAddrConfig", "outVnicIpv4PooledAddrConfig", "ConfigSet", "Version142b", "Output", True),
		"OutVnicIpv4ProfDerivedAddrConfig":UcsFactoryMeta("OutVnicIpv4ProfDerivedAddrConfig", "outVnicIpv4ProfDerivedAddrConfig", "ConfigSet", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ComputeGetInventory","computeGetInventory", "Version142b"),
	},

	"ConfigCheckCompatibility": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"InBladePackVersion":UcsFactoryMeta("InBladePackVersion", "inBladePackVersion", "Xs:string", "Version142b", "Input", False),
		"InDetailResult":UcsFactoryMeta("InDetailResult", "inDetailResult", "Xs:string", "Version142b", "Input", False),
		"InInfraPackVersion":UcsFactoryMeta("InInfraPackVersion", "inInfraPackVersion", "Xs:string", "Version142b", "Input", False),
		"InRackPackVersion":UcsFactoryMeta("InRackPackVersion", "inRackPackVersion", "Xs:string", "Version142b", "Input", False),
		"OutConfigSet":UcsFactoryMeta("OutConfigSet", "outConfigSet", "ConfigSet", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ConfigCheckCompatibility","configCheckCompatibility", "Version142b"),
	},

	"ConfigCheckConformance": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"OutConfDns":UcsFactoryMeta("OutConfDns", "outConfDns", "DnSet", "Version142b", "Output", True),
		"OutInProgressDns":UcsFactoryMeta("OutInProgressDns", "outInProgressDns", "DnSet", "Version142b", "Output", True),
		"OutNonConfDns":UcsFactoryMeta("OutNonConfDns", "outNonConfDns", "DnSet", "Version142b", "Output", True),
		"OutNonUpgradableDns":UcsFactoryMeta("OutNonUpgradableDns", "outNonUpgradableDns", "DnSet", "Version142b", "Output", True),
		"OutToResetDns":UcsFactoryMeta("OutToResetDns", "outToResetDns", "DnSet", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ConfigCheckConformance","configCheckConformance", "Version142b"),
	},

	"ConfigCheckFirmwareUpdatable": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InUpdatableDns":UcsFactoryMeta("InUpdatableDns", "inUpdatableDns", "DnSet", "Version142b", "Input", True),
		"OutFailDns":UcsFactoryMeta("OutFailDns", "outFailDns", "DnSet", "Version142b", "Output", True),
		"OutInvalidDns":UcsFactoryMeta("OutInvalidDns", "outInvalidDns", "DnSet", "Version142b", "Output", True),
		"OutPassDns":UcsFactoryMeta("OutPassDns", "outPassDns", "DnSet", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ConfigCheckFirmwareUpdatable","configCheckFirmwareUpdatable", "Version142b"),
	},

	"ConfigConfFiltered": {
		"ClassId":UcsFactoryMeta("ClassId", "classId", "NamingClassId", "Version142b", "InputOutput", False),
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InConfig":UcsFactoryMeta("InConfig", "inConfig", "ConfigConfig", "Version142b", "Input", True),
		"InFilter":UcsFactoryMeta("InFilter", "inFilter", "FilterFilter", "Version142b", "Input", True),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"OutConfigs":UcsFactoryMeta("OutConfigs", "outConfigs", "ConfigSet", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ConfigConfFiltered","configConfFiltered", "Version142b"),
	},

	"ConfigConfMo": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"InConfig":UcsFactoryMeta("InConfig", "inConfig", "ConfigConfig", "Version142b", "Input", True),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"OutConfig":UcsFactoryMeta("OutConfig", "outConfig", "ConfigConfig", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ConfigConfMo","configConfMo", "Version142b"),
	},

	"ConfigConfMoGroup": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InConfig":UcsFactoryMeta("InConfig", "inConfig", "ConfigConfig", "Version142b", "Input", True),
		"InDns":UcsFactoryMeta("InDns", "inDns", "DnSet", "Version142b", "Input", True),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"OutConfigs":UcsFactoryMeta("OutConfigs", "outConfigs", "ConfigSet", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ConfigConfMoGroup","configConfMoGroup", "Version142b"),
	},

	"ConfigConfMos": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InConfigs":UcsFactoryMeta("InConfigs", "inConfigs", "ConfigMap", "Version142b", "Input", True),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"OutConfigs":UcsFactoryMeta("OutConfigs", "outConfigs", "ConfigMap", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ConfigConfMos","configConfMos", "Version142b"),
	},

	"ConfigConfRename": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"InNewName":UcsFactoryMeta("InNewName", "inNewName", "Xs:string", "Version142b", "Input", False),
		"OutConfig":UcsFactoryMeta("OutConfig", "outConfig", "ConfigConfig", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ConfigConfRename","configConfRename", "Version142b"),
	},

	"ConfigEstimateImpact": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InConfigs":UcsFactoryMeta("InConfigs", "inConfigs", "ConfigMap", "Version142b", "Input", True),
		"OutAckables":UcsFactoryMeta("OutAckables", "outAckables", "ConfigMap", "Version142b", "Output", True),
		"OutAffected":UcsFactoryMeta("OutAffected", "outAffected", "ConfigMap", "Version142b", "Output", True),
		"OutOldAckables":UcsFactoryMeta("OutOldAckables", "outOldAckables", "ConfigMap", "Version142b", "Output", True),
		"OutOldAffected":UcsFactoryMeta("OutOldAffected", "outOldAffected", "ConfigMap", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ConfigEstimateImpact","configEstimateImpact", "Version142b"),
	},

	"ConfigFindDependencies": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"InReturnConfigs":UcsFactoryMeta("InReturnConfigs", "inReturnConfigs", "Xs:string", "Version142b", "Input", False),
		"OutConfigs":UcsFactoryMeta("OutConfigs", "outConfigs", "ConfigSet", "Version142b", "Output", True),
		"OutHasDep":UcsFactoryMeta("OutHasDep", "outHasDep", "Xs:string", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("ConfigFindDependencies","configFindDependencies", "Version142b"),
	},

	"ConfigFindDnsByClassId": {
		"ClassId":UcsFactoryMeta("ClassId", "classId", "NamingClassId", "Version142b", "InputOutput", False),
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InFilter":UcsFactoryMeta("InFilter", "inFilter", "FilterFilter", "Version142b", "Input", True),
		"OutDns":UcsFactoryMeta("OutDns", "outDns", "DnSet", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ConfigFindDnsByClassId","configFindDnsByClassId", "Version142b"),
	},

	"ConfigFindHostPackDependencies": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"InHostPackDns":UcsFactoryMeta("InHostPackDns", "inHostPackDns", "DnSet", "Version142b", "Input", True),
		"OutConfigSet":UcsFactoryMeta("OutConfigSet", "outConfigSet", "ConfigSet", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ConfigFindHostPackDependencies","configFindHostPackDependencies", "Version142b"),
	},

	"ConfigFindPermitted": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"InClassId":UcsFactoryMeta("InClassId", "inClassId", "NamingClassId", "Version142b", "Input", False),
		"InFilter":UcsFactoryMeta("InFilter", "inFilter", "FilterFilter", "Version142b", "Input", True),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"OutConfigSet":UcsFactoryMeta("OutConfigSet", "outConfigSet", "ConfigSet", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ConfigFindPermitted","configFindPermitted", "Version142b"),
	},

	"ConfigGetXmlFile": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InFilePath":UcsFactoryMeta("InFilePath", "inFilePath", "Xs:string", "Version142b", "Input", False),
		"OutConfig":UcsFactoryMeta("OutConfig", "outConfig", "ConfigConfig", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ConfigGetXmlFile","configGetXmlFile", "Version142b"),
	},

	"ConfigGetXmlFileStr": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InFilePath":UcsFactoryMeta("InFilePath", "inFilePath", "Xs:string", "Version142b", "Input", False),
		"OutConfig":UcsFactoryMeta("OutConfig", "outConfig", "Xs:string", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("ConfigGetXmlFileStr","configGetXmlFileStr", "Version142b"),
	},

	"ConfigInstallAllImpact": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"InBladePackVersion":UcsFactoryMeta("InBladePackVersion", "inBladePackVersion", "Xs:string", "Version142b", "Input", False),
		"InHostPackDns":UcsFactoryMeta("InHostPackDns", "inHostPackDns", "DnSet", "Version142b", "Input", True),
		"InInfraPackVersion":UcsFactoryMeta("InInfraPackVersion", "inInfraPackVersion", "Xs:string", "Version142b", "Input", False),
		"InRackPackVersion":UcsFactoryMeta("InRackPackVersion", "inRackPackVersion", "Xs:string", "Version142b", "Input", False),
		"OutConfigSet":UcsFactoryMeta("OutConfigSet", "outConfigSet", "ConfigSet", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ConfigInstallAllImpact","configInstallAllImpact", "Version142b"),
	},

	"ConfigMoChangeEvent": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InConfig":UcsFactoryMeta("InConfig", "inConfig", "ConfigConfig", "Version142b", "Input", True),
		"InEid":UcsFactoryMeta("InEid", "inEid", "Xs:unsignedLong", "Version142b", "Input", False),
		"Meta":UcsFactoryMethodMeta("ConfigMoChangeEvent","configMoChangeEvent", "Version142b"),
	},

	"ConfigRefreshIdentity": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"InIdType":UcsFactoryMeta("InIdType", "inIdType", "Xs:string", "Version142b", "Input", False),
		"OutConfig":UcsFactoryMeta("OutConfig", "outConfig", "ConfigConfig", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ConfigRefreshIdentity","configRefreshIdentity", "Version142b"),
	},

	"ConfigReleaseResolveContext": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InContext":UcsFactoryMeta("InContext", "inContext", "Xs:unsignedLong", "Version142b", "Input", False),
		"Meta":UcsFactoryMethodMeta("ConfigReleaseResolveContext","configReleaseResolveContext", "Version142b"),
	},

	"ConfigRenewResolveContext": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InContext":UcsFactoryMeta("InContext", "inContext", "Xs:unsignedLong", "Version142b", "Input", False),
		"OutContext":UcsFactoryMeta("OutContext", "outContext", "Xs:unsignedLong", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("ConfigRenewResolveContext","configRenewResolveContext", "Version142b"),
	},

	"ConfigResolveChildren": {
		"ClassId":UcsFactoryMeta("ClassId", "classId", "NamingClassId", "Version142b", "InputOutput", False),
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InDn":UcsFactoryMeta("InDn", "inDn", "ReferenceObject", "Version142b", "Input", False),
		"InFilter":UcsFactoryMeta("InFilter", "inFilter", "FilterFilter", "Version142b", "Input", True),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"OutConfigs":UcsFactoryMeta("OutConfigs", "outConfigs", "ConfigSet", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ConfigResolveChildren","configResolveChildren", "Version142b"),
	},

	"ConfigResolveChildrenSorted": {
		"ClassId":UcsFactoryMeta("ClassId", "classId", "NamingClassId", "Version142b", "InputOutput", False),
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InDn":UcsFactoryMeta("InDn", "inDn", "ReferenceObject", "Version142b", "Input", False),
		"InFilter":UcsFactoryMeta("InFilter", "inFilter", "FilterFilter", "Version142b", "Input", True),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"InSize":UcsFactoryMeta("InSize", "inSize", "Xs:unsignedShort", "Version142b", "Input", False),
		"OutContext":UcsFactoryMeta("OutContext", "outContext", "Xs:unsignedLong", "Version142b", "Output", False),
		"OutTotalSize":UcsFactoryMeta("OutTotalSize", "outTotalSize", "Xs:unsignedInt", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("ConfigResolveChildrenSorted","configResolveChildrenSorted", "Version142b"),
	},

	"ConfigResolveClass": {
		"ClassId":UcsFactoryMeta("ClassId", "classId", "NamingClassId", "Version142b", "InputOutput", False),
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InFilter":UcsFactoryMeta("InFilter", "inFilter", "FilterFilter", "Version142b", "Input", True),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"OutConfigs":UcsFactoryMeta("OutConfigs", "outConfigs", "ConfigSet", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ConfigResolveClass","configResolveClass", "Version142b"),
	},

	"ConfigResolveClassSorted": {
		"ClassId":UcsFactoryMeta("ClassId", "classId", "NamingClassId", "Version142b", "InputOutput", False),
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InFilter":UcsFactoryMeta("InFilter", "inFilter", "FilterFilter", "Version142b", "Input", True),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"InSize":UcsFactoryMeta("InSize", "inSize", "Xs:unsignedShort", "Version142b", "Input", False),
		"OutContext":UcsFactoryMeta("OutContext", "outContext", "Xs:unsignedLong", "Version142b", "Output", False),
		"OutTotalSize":UcsFactoryMeta("OutTotalSize", "outTotalSize", "Xs:unsignedInt", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("ConfigResolveClassSorted","configResolveClassSorted", "Version142b"),
	},

	"ConfigResolveClasses": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"InIds":UcsFactoryMeta("InIds", "inIds", "ClassIdSet", "Version142b", "Input", True),
		"OutConfigs":UcsFactoryMeta("OutConfigs", "outConfigs", "ConfigSet", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ConfigResolveClasses","configResolveClasses", "Version142b"),
	},

	"ConfigResolveClassesSorted": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"InIds":UcsFactoryMeta("InIds", "inIds", "ClassIdSet", "Version142b", "Input", True),
		"InSize":UcsFactoryMeta("InSize", "inSize", "Xs:unsignedShort", "Version142b", "Input", False),
		"OutContext":UcsFactoryMeta("OutContext", "outContext", "Xs:unsignedLong", "Version142b", "Output", False),
		"OutTotalSize":UcsFactoryMeta("OutTotalSize", "outTotalSize", "Xs:unsignedInt", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("ConfigResolveClassesSorted","configResolveClassesSorted", "Version142b"),
	},

	"ConfigResolveContext": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InContext":UcsFactoryMeta("InContext", "inContext", "Xs:unsignedLong", "Version142b", "Input", False),
		"InSize":UcsFactoryMeta("InSize", "inSize", "Xs:unsignedShort", "Version142b", "Input", False),
		"OutContext":UcsFactoryMeta("OutContext", "outContext", "Xs:unsignedLong", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("ConfigResolveContext","configResolveContext", "Version142b"),
	},

	"ConfigResolveDn": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"OutConfig":UcsFactoryMeta("OutConfig", "outConfig", "ConfigConfig", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ConfigResolveDn","configResolveDn", "Version142b"),
	},

	"ConfigResolveDns": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InDns":UcsFactoryMeta("InDns", "inDns", "DnSet", "Version142b", "Input", True),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"OutConfigs":UcsFactoryMeta("OutConfigs", "outConfigs", "ConfigSet", "Version142b", "Output", True),
		"OutUnresolved":UcsFactoryMeta("OutUnresolved", "outUnresolved", "DnSet", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ConfigResolveDns","configResolveDns", "Version142b"),
	},

	"ConfigResolveParent": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"OutConfig":UcsFactoryMeta("OutConfig", "outConfig", "ConfigConfig", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ConfigResolveParent","configResolveParent", "Version142b"),
	},

	"ConfigScope": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"InClass":UcsFactoryMeta("InClass", "inClass", "NamingClassId", "Version142b", "Input", False),
		"InFilter":UcsFactoryMeta("InFilter", "inFilter", "FilterFilter", "Version142b", "Input", True),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"InRecursive":UcsFactoryMeta("InRecursive", "inRecursive", "Xs:string", "Version142b", "Input", False),
		"OutConfigs":UcsFactoryMeta("OutConfigs", "outConfigs", "ConfigSet", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("ConfigScope","configScope", "Version142b"),
	},

	"EventRegisterEventChannel": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InDn":UcsFactoryMeta("InDn", "inDn", "Xs:string", "Version142b", "Input", False),
		"OutReqID":UcsFactoryMeta("OutReqID", "outReqID", "Xs:unsignedInt", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("EventRegisterEventChannel","eventRegisterEventChannel", "Version142b"),
	},

	"EventRegisterEventChannelResp": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InCtx":UcsFactoryMeta("InCtx", "inCtx", "Xs:string", "Version142b", "Input", False),
		"InDn":UcsFactoryMeta("InDn", "inDn", "Xs:string", "Version142b", "Input", False),
		"InReqID":UcsFactoryMeta("InReqID", "inReqID", "Xs:unsignedInt", "Version142b", "Input", False),
		"Meta":UcsFactoryMethodMeta("EventRegisterEventChannelResp","eventRegisterEventChannelResp", "Version142b"),
	},

	"EventSendEvent": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InDn":UcsFactoryMeta("InDn", "inDn", "Xs:string", "Version142b", "Input", False),
		"InEvent":UcsFactoryMeta("InEvent", "inEvent", "Method", "Version142b", "Input", True),
		"InReqId":UcsFactoryMeta("InReqId", "inReqId", "Xs:unsignedInt", "Version142b", "Input", False),
		"Meta":UcsFactoryMethodMeta("EventSendEvent","eventSendEvent", "Version142b"),
	},

	"EventSendHeartbeat": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"OutSystemTime":UcsFactoryMeta("OutSystemTime", "outSystemTime", "DateTime", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("EventSendHeartbeat","eventSendHeartbeat", "Version142b"),
	},

	"EventSubscribe": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InFilter":UcsFactoryMeta("InFilter", "inFilter", "FilterFilter", "Version142b", "Input", True),
		"Meta":UcsFactoryMethodMeta("EventSubscribe","eventSubscribe", "Version142b"),
	},

	"EventUnRegisterEventChannel": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InDn":UcsFactoryMeta("InDn", "inDn", "Xs:string", "Version142b", "Input", False),
		"InReqID":UcsFactoryMeta("InReqID", "inReqID", "Xs:unsignedInt", "Version142b", "Input", False),
		"Meta":UcsFactoryMethodMeta("EventUnRegisterEventChannel","eventUnRegisterEventChannel", "Version142b"),
	},

	"EventUnsubscribe": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"OutStatus":UcsFactoryMeta("OutStatus", "outStatus", "Xs:string", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("EventUnsubscribe","eventUnsubscribe", "Version142b"),
	},

	"FaultAckFault": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InId":UcsFactoryMeta("InId", "inId", "Xs:unsignedLong", "Version142b", "Input", False),
		"Meta":UcsFactoryMethodMeta("FaultAckFault","faultAckFault", "Version142b"),
	},

	"FaultAckFaults": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InIds":UcsFactoryMeta("InIds", "inIds", "IdSet", "Version142b", "Input", True),
		"Meta":UcsFactoryMethodMeta("FaultAckFaults","faultAckFaults", "Version142b"),
	},

	"FaultResolveFault": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InId":UcsFactoryMeta("InId", "inId", "Xs:unsignedLong", "Version142b", "Input", False),
		"OutFault":UcsFactoryMeta("OutFault", "outFault", "ConfigConfig", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("FaultResolveFault","faultResolveFault", "Version142b"),
	},

	"FsmDebugAction": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"InDirective":UcsFactoryMeta("InDirective", "inDirective", "Xs:string", "Version142b", "Input", False),
		"Meta":UcsFactoryMethodMeta("FsmDebugAction","fsmDebugAction", "Version142b"),
	},

	"LoggingSyncOcns": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InFromOrZero":UcsFactoryMeta("InFromOrZero", "inFromOrZero", "Xs:unsignedLong", "Version142b", "Input", False),
		"InToOrZero":UcsFactoryMeta("InToOrZero", "inToOrZero", "Xs:unsignedLong", "Version142b", "Input", False),
		"OutStimuli":UcsFactoryMeta("OutStimuli", "outStimuli", "MethodSet", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("LoggingSyncOcns","loggingSyncOcns", "Version142b"),
	},

	"LsClone": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"InServerName":UcsFactoryMeta("InServerName", "inServerName", "Xs:string", "Version142b", "Input", False),
		"InTargetOrg":UcsFactoryMeta("InTargetOrg", "inTargetOrg", "ReferenceObject", "Version142b", "Input", False),
		"OutConfig":UcsFactoryMeta("OutConfig", "outConfig", "ConfigConfig", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("LsClone","lsClone", "Version142b"),
	},

	"LsInstantiateNNamedTemplate": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"InNameSet":UcsFactoryMeta("InNameSet", "inNameSet", "DnSet", "Version142b", "Input", True),
		"InTargetOrg":UcsFactoryMeta("InTargetOrg", "inTargetOrg", "ReferenceObject", "Version142b", "Input", False),
		"OutConfigs":UcsFactoryMeta("OutConfigs", "outConfigs", "ConfigSet", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("LsInstantiateNNamedTemplate","lsInstantiateNNamedTemplate", "Version142b"),
	},

	"LsInstantiateNTemplate": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"InNumberOf":UcsFactoryMeta("InNumberOf", "inNumberOf", "Xs:unsignedByte", "Version142b", "Input", False),
		"InServerNamePrefixOrEmpty":UcsFactoryMeta("InServerNamePrefixOrEmpty", "inServerNamePrefixOrEmpty", "Xs:string", "Version142b", "Input", False),
		"InTargetOrg":UcsFactoryMeta("InTargetOrg", "inTargetOrg", "ReferenceObject", "Version142b", "Input", False),
		"OutConfigs":UcsFactoryMeta("OutConfigs", "outConfigs", "ConfigSet", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("LsInstantiateNTemplate","lsInstantiateNTemplate", "Version142b"),
	},

	"LsInstantiateTemplate": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"InServerName":UcsFactoryMeta("InServerName", "inServerName", "Xs:string", "Version142b", "Input", False),
		"InTargetOrg":UcsFactoryMeta("InTargetOrg", "inTargetOrg", "ReferenceObject", "Version142b", "Input", False),
		"OutConfig":UcsFactoryMeta("OutConfig", "outConfig", "ConfigConfig", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("LsInstantiateTemplate","lsInstantiateTemplate", "Version142b"),
	},

	"LsResolveTemplates": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"InExcludeIfBound":UcsFactoryMeta("InExcludeIfBound", "inExcludeIfBound", "Xs:string", "Version142b", "Input", False),
		"InFilter":UcsFactoryMeta("InFilter", "inFilter", "FilterFilter", "Version142b", "Input", True),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"InType":UcsFactoryMeta("InType", "inType", "Xs:string", "Version142b", "Input", False),
		"OutConfigs":UcsFactoryMeta("OutConfigs", "outConfigs", "ConfigMap", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("LsResolveTemplates","lsResolveTemplates", "Version142b"),
	},

	"LsTemplatise": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"InTargetOrg":UcsFactoryMeta("InTargetOrg", "inTargetOrg", "ReferenceObject", "Version142b", "Input", False),
		"InTemplateName":UcsFactoryMeta("InTemplateName", "inTemplateName", "Xs:string", "Version142b", "Input", False),
		"InTemplateType":UcsFactoryMeta("InTemplateType", "inTemplateType", "Xs:string", "Version142b", "Input", False),
		"OutConfig":UcsFactoryMeta("OutConfig", "outConfig", "ConfigConfig", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("LsTemplatise","lsTemplatise", "Version142b"),
	},

	"MethodVessel": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InStimuli":UcsFactoryMeta("InStimuli", "inStimuli", "MethodSet", "Version142b", "Input", True),
		"Meta":UcsFactoryMethodMeta("MethodVessel","methodVessel", "Version142b"),
	},

	"MgmtResolveBackupFilenames": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InBackupSource":UcsFactoryMeta("InBackupSource", "inBackupSource", "Xs:string", "Version142b", "Input", False),
		"InType":UcsFactoryMeta("InType", "inType", "Xs:string", "Version142b", "Input", False),
		"OutBackups":UcsFactoryMeta("OutBackups", "outBackups", "ConfigSet", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("MgmtResolveBackupFilenames","mgmtResolveBackupFilenames", "Version142b"),
	},

	"OrgResolveElements": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"InClass":UcsFactoryMeta("InClass", "inClass", "NamingClassId", "Version142b", "Input", False),
		"InFilter":UcsFactoryMeta("InFilter", "inFilter", "FilterFilter", "Version142b", "Input", True),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"InSingleLevel":UcsFactoryMeta("InSingleLevel", "inSingleLevel", "Xs:string", "Version142b", "Input", False),
		"OutConfigs":UcsFactoryMeta("OutConfigs", "outConfigs", "ConfigMap", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("OrgResolveElements","orgResolveElements", "Version142b"),
	},

	"OrgResolveLogicalParents": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"InSingleLevel":UcsFactoryMeta("InSingleLevel", "inSingleLevel", "Xs:string", "Version142b", "Input", False),
		"OutConfigs":UcsFactoryMeta("OutConfigs", "outConfigs", "ConfigMap", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("OrgResolveLogicalParents","orgResolveLogicalParents", "Version142b"),
	},

	"PolicyResolveNames": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InClientConnectorDn":UcsFactoryMeta("InClientConnectorDn", "inClientConnectorDn", "ReferenceObject", "Version142b", "Input", False),
		"InContext":UcsFactoryMeta("InContext", "inContext", "ReferenceObject", "Version142b", "Input", False),
		"InFilter":UcsFactoryMeta("InFilter", "inFilter", "FilterFilter", "Version142b", "Input", True),
		"InPolicyType":UcsFactoryMeta("InPolicyType", "inPolicyType", "Xs:string", "Version142b", "Input", False),
		"OutPolicyNames":UcsFactoryMeta("OutPolicyNames", "outPolicyNames", "ConfigSet", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("PolicyResolveNames","policyResolveNames", "Version142b"),
	},

	"PoolResolveInScope": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"InClass":UcsFactoryMeta("InClass", "inClass", "NamingClassId", "Version142b", "Input", False),
		"InFilter":UcsFactoryMeta("InFilter", "inFilter", "FilterFilter", "Version142b", "Input", True),
		"InHierarchical":UcsFactoryMeta("InHierarchical", "inHierarchical", "Xs:string", "Version142b", "Input", False),
		"InSingleLevel":UcsFactoryMeta("InSingleLevel", "inSingleLevel", "Xs:string", "Version142b", "Input", False),
		"OutConfigs":UcsFactoryMeta("OutConfigs", "outConfigs", "ConfigMap", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("PoolResolveInScope","poolResolveInScope", "Version142b"),
	},

	"StatsClearInterval": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InDns":UcsFactoryMeta("InDns", "inDns", "DnSet", "Version142b", "Input", True),
		"Meta":UcsFactoryMethodMeta("StatsClearInterval","statsClearInterval", "Version142b"),
	},

	"StatsResolveThresholdPolicy": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"OutConfig":UcsFactoryMeta("OutConfig", "outConfig", "ConfigConfig", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("StatsResolveThresholdPolicy","statsResolveThresholdPolicy", "Version142b"),
	},

	"SwatExample": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InConfig":UcsFactoryMeta("InConfig", "inConfig", "ConfigConfig", "Version142b", "Input", True),
		"Meta":UcsFactoryMethodMeta("SwatExample","swatExample", "Version142b"),
	},

	"SwatGetstats": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"OutConfigs":UcsFactoryMeta("OutConfigs", "outConfigs", "ConfigSet", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("SwatGetstats","swatGetstats", "Version142b"),
	},

	"SwatInject": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InConfig":UcsFactoryMeta("InConfig", "inConfig", "ConfigConfig", "Version142b", "Input", True),
		"Meta":UcsFactoryMethodMeta("SwatInject","swatInject", "Version142b"),
	},

	"SyntheticFSObjInventory": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"Dn":UcsFactoryMeta("Dn", "dn", "ReferenceObject", "Version142b", "InputOutput", False),
		"InConfig":UcsFactoryMeta("InConfig", "inConfig", "ConfigConfig", "Version142b", "Input", True),
		"Meta":UcsFactoryMethodMeta("SyntheticFSObjInventory","syntheticFSObjInventory", "Version142b"),
	},

	"SyntheticFSObjInventoryB": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InConfig":UcsFactoryMeta("InConfig", "inConfig", "ConfigConfig", "Version142b", "Input", True),
		"Meta":UcsFactoryMethodMeta("SyntheticFSObjInventoryB","syntheticFSObjInventoryB", "Version142b"),
	},

	"SyntheticTestTx": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InConfig":UcsFactoryMeta("InConfig", "inConfig", "ConfigSet", "Version142b", "Input", True),
		"InTest":UcsFactoryMeta("InTest", "inTest", "Xs:string", "Version142b", "Input", False),
		"InWhat":UcsFactoryMeta("InWhat", "inWhat", "Xs:string", "Version142b", "Input", False),
		"OutConfig":UcsFactoryMeta("OutConfig", "outConfig", "ConfigSet", "Version142b", "Output", True),
		"Meta":UcsFactoryMethodMeta("SyntheticTestTx","syntheticTestTx", "Version142b"),
	},

	"TrigPerformTokenAction": {
		"Cookie":UcsFactoryMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
		"InContext":UcsFactoryMeta("InContext", "inContext", "ReferenceObject", "Version142b", "Input", False),
		"InSchedName":UcsFactoryMeta("InSchedName", "inSchedName", "Xs:string", "Version142b", "Input", False),
		"InTokenAction":UcsFactoryMeta("InTokenAction", "inTokenAction", "Xs:string", "Version142b", "Input", False),
		"InTokenId":UcsFactoryMeta("InTokenId", "inTokenId", "Xs:unsignedLong", "Version142b", "Input", False),
		"InTriggerableDn":UcsFactoryMeta("InTriggerableDn", "inTriggerableDn", "ReferenceObject", "Version142b", "Input", False),
		"InWindowName":UcsFactoryMeta("InWindowName", "inWindowName", "Xs:string", "Version142b", "Input", False),
		"InWindowType":UcsFactoryMeta("InWindowType", "inWindowType", "Xs:string", "Version142b", "Input", False),
		"OutLastTokenOperation":UcsFactoryMeta("OutLastTokenOperation", "outLastTokenOperation", "Xs:string", "Version142b", "Output", False),
		"OutNewTokenId":UcsFactoryMeta("OutNewTokenId", "outNewTokenId", "Xs:unsignedLong", "Version142b", "Output", False),
		"OutOldTokenId":UcsFactoryMeta("OutOldTokenId", "outOldTokenId", "Xs:unsignedLong", "Version142b", "Output", False),
		"OutOldTriggerableDn":UcsFactoryMeta("OutOldTriggerableDn", "outOldTriggerableDn", "ReferenceObject", "Version142b", "Output", False),
		"OutWindowName":UcsFactoryMeta("OutWindowName", "outWindowName", "Xs:string", "Version142b", "Output", False),
		"OutWindowType":UcsFactoryMeta("OutWindowType", "outWindowType", "Xs:string", "Version142b", "Output", False),
		"Meta":UcsFactoryMethodMeta("TrigPerformTokenAction","trigPerformTokenAction", "Version142b"),
	},

}

