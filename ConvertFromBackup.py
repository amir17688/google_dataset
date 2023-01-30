#!/usr/bin/python
import logging
log = logging.getLogger(__name__)



import os
import re
import xml.dom
import xml.dom.minidom
from Constants import *
from UcsHandle import _AffirmativeList
from UcsBase import *
from MoMeta import _VersionMeta,_ManagedObjectMeta




def GetElementChildNodes(node):
    childList = [childNode for childNode in node.childNodes if childNode.nodeType == childNode.ELEMENT_NODE ]
    return childList

### Modify the Property Name
#====================================================
def GetPropName(prop):
    newProp = re.sub('_+','_',re.sub('^_','',re.sub('[/\-: +]','_',re.sub('([a-z0-9])([A-Z])','\g<1>_\g<2>',prop)))).upper()
    return newProp

### create a string of dictionary propertyMap
#================================================
def CreatePythonPropertyMap(propertyMap):
    s = "{"
    for key,value in propertyMap.iteritems():
        s = s + key + ":" + value + ", "

    if s != "{":
        s = s[:-2]  # removes last 2 char
    return (s + "}")


def MakeRn(classNode):
    classId = classNode.localName
    #print classId
    propMoMeta = UcsUtils.GetUcsPropertyMeta(UcsUtils.WordU(classId) , "Meta")
    rnPattern = propMoMeta.rn
    
    for prop in re.findall("\[([^\]]*)\]",rnPattern):
        prop = UcsUtils.WordL(prop)
        if classNode.hasAttribute(prop):
            if (classNode.getAttribute(prop) != None):
                rnPattern = re.sub('\[%s\]' % UcsUtils.WordU(prop),'%s' % classNode.getAttribute(prop), rnPattern)
            else:
                raise Exception('Property "%s" was None in MakeRn' %prop)
        else:
            raise Exception('Property "%s" was not found in MakeRn arguments' %prop)
    #print rnPattern
    return rnPattern

def IsAddorSet(classNode):
    AddSetFlag = None
    classId = classNode.localName
    propMoMeta = UcsUtils.GetUcsPropertyMeta(UcsUtils.WordU(classId) , "Meta")
    verbs = propMoMeta.verbs
    if verbs:
        if "Add" in verbs or "Set" in verbs:
            AddSetFlag = "Add"
        elif "Get" in verbs:
            AddSetFlag = "Get"
        else:
            return None
    else:
        AddSetFlag = "Empty"
    
    return AddSetFlag


def FormGetCmdlet(classNode, inMo, tagName):
    
    classId = classNode.localName
    propertyMap = {}
    rn = MakeRn(classNode)
    dn = None
    
    if UcsUtils.FindClassIdInMoMetaIgnoreCase(classId) == None:
        gmoFlag = True
        print ("classId %s does not exist in MoMeta." % UcsUtils.WordU(classId))
    else:
        gmoFlag = False
    
    if not gmoFlag:
        peerClassId = UcsUtils.WordU(classId) 
        peerClassIdStr = peerClassId + ".ClassId()"
        #parentClassId = GetClassIdForDn(parentDn)
        #parentClassIdStr = parentClassId + ".ClassId()"
        dnStr = '.DN'
    else:
        peerClassId = ""
        peerClassIdStr = '"'+(classId)+'"'
        #parentClassId = ""
        #parentClassIdStr = "None"
        #dnStr = '"dn"'
    
        ## create property map for attributes
    for attr, val in classNode.attributes.items():
        name = attr
        value = '"' + val + '"'
        #print name, value
        
        paramNameToUse = name
        
        if paramNameToUse is not None:
                if not gmoFlag and UcsUtils.GetUcsPropertyMeta(peerClassId, UcsUtils.WordU(paramNameToUse)) is not None:
                    paramNameToUse = peerClassId + '.' + GetPropName(paramNameToUse)
                else:
                    paramNameToUse = '"'+ paramNameToUse + '"'
            
                propertyMap[paramNameToUse] = value
                    
            

    #tagElement = ""
    #if tag:
    #   tagElement = tag + " = "
    
    
    if classNode.parentNode.localName == "topRoot":
        if rn:
            dn = rn
            cmdlet = "%s = handle.GetManagedObject(%s, %s, {%s%s:\"%s\"})\n" %(tagName, inMo, peerClassIdStr, peerClassId, dnStr, dn)

    else:
        cmdlet = "%s = handle.GetManagedObject(%s, %s, %s)\n" %(tagName, inMo, peerClassIdStr, CreatePythonPropertyMap(propertyMap))

    
        
    return cmdlet


def FormAddCmdlet(classNode, inMo, tagName):
    
    classId = classNode.localName
    propertyMap = {}
    #rn = MakeRn(classNode)
    #dn = None
    
    if UcsUtils.FindClassIdInMoMetaIgnoreCase(classId) == None:
        gmoFlag = True
        print ("classId %s does not exist in MoMeta." % UcsUtils.WordU(classId))
    else:
        gmoFlag = False
    
    if not gmoFlag:
        peerClassId = UcsUtils.WordU(classId) 
        peerClassIdStr = peerClassId + ".ClassId()"
        #parentClassId = GetClassIdForDn(parentDn)
        #parentClassIdStr = parentClassId + ".ClassId()"
        dnStr = '.DN'
    else:
        peerClassId = ""
        peerClassIdStr = '"'+(classId)+'"'
        #parentClassId = ""
        #parentClassIdStr = "None"
        #dnStr = '"dn"'
    
        ## create property map for attributes
    for attr, val in classNode.attributes.items():
        name = attr
        value = '"' + val + '"'
        #print name, value
        
        paramNameToUse = name
        
        if paramNameToUse is not None:
                if not gmoFlag and UcsUtils.GetUcsPropertyMeta(peerClassId, UcsUtils.WordU(paramNameToUse)) is not None:
                    paramNameToUse = peerClassId + '.' + GetPropName(paramNameToUse)
                else:
                    paramNameToUse = '"'+ paramNameToUse + '"'
            
                propertyMap[paramNameToUse] = value
                    
            

    #tagElement = ""
    #if tag:
    #   tagElement = tag + " = "
    
    
    cmdlet = "%s = handle.AddManagedObject(%s, %s, %s, True)\n" %(tagName, inMo, peerClassIdStr, CreatePythonPropertyMap(propertyMap))
       
    return cmdlet
    
def GenSubCmdlet(classNode,inMo,cmdlet,tagName):
    
    if UcsUtils.IsValidClassId(UcsUtils.WordU(classNode.localName)):
        
        if IsAddorSet(classNode) == "Add":
            tempCmdlet = FormAddCmdlet(classNode, inMo, tagName)
        else:
            tempCmdlet = FormGetCmdlet(classNode, inMo, tagName)
    else:
        tempCmdlet = FormAddCmdlet(classNode, inMo, tagName)
        
    cmdlet += tempCmdlet

    inMo = tagName
    
    childList = GetElementChildNodes(classNode)
    callCount = 1

    moPatternToIgnore = re.compile(r'^Aaa[\S]+', re.IGNORECASE)
    
    for child in childList:
        
        if moPatternToIgnore.search(child.localName):
            WriteUcsWarning('[Warning]: Ignored classId: %s' %child.localName)
            continue
        
        if UcsUtils.IsValidClassId(UcsUtils.WordU(child.localName)):
            if IsAddorSet(child) is None or IsAddorSet(child) == "Empty":
                WriteUcsWarning('[Warning]: Verbs Not Set for classId: %s' %child.localName)
                continue
        tagNameNew = tagName + "_" + str(callCount)
        cmdlet = GenSubCmdlet(child,inMo,cmdlet,tagNameNew)
        callCount += 1
    return cmdlet


def GenCmdlet(topNode):
    
    moPatternToIgnore = re.compile(r'^Aaa[\S]+', re.IGNORECASE)
    
    if topNode.localName == "topRoot":
        cmdlet = ""
        for child in GetElementChildNodes(topNode):
            if UcsUtils.IsValidClassId(UcsUtils.WordU(child.localName)):
                
                if moPatternToIgnore.search(child.localName):
                    WriteUcsWarning('[Warning]: Ignored classId: %s' %child.localName)
                    continue
                
                if IsAddorSet(child) is None or IsAddorSet(child) == "Empty":
                    WriteUcsWarning('[Warning]: Verbs Not Set for classId: %s' %child.localName)
                    continue
                
            subCmdlet = ""
            parentGetCmd = FormGetCmdlet(child,"None","obj")
            
            if child.hasChildNodes() and len(GetElementChildNodes(child)) > 0 :
                for subChild in GetElementChildNodes(child):
                    
                    if moPatternToIgnore.search(subChild.localName):
                        WriteUcsWarning('[Warning]: Ignored classId: %s' %subChild.localName)
                        continue
                    
                    if UcsUtils.IsValidClassId(UcsUtils.WordU(subChild.localName)):
                        if IsAddorSet(subChild) is None or IsAddorSet(subChild) == "Empty":
                            WriteUcsWarning('[Warning]: Verbs Not Set for classId: %s' %subChild.localName)
                            continue
                        
                    subCmdlet += "handle.StartTransaction() \n"
                    subCmdlet += GenSubCmdlet(subChild,"obj",parentGetCmd,"mo")
                    subCmdlet += "handle.CompleteTransaction() \n\n"
                    
                cmdlet += subCmdlet
                cmdlet += "############################################################################################\n\n"
                
        return cmdlet


def ConvertFromBackup(path, dumpToFile=False, dumpFilePath=None):
    
    if not path:
        WriteUcsWarning("Please provide the path")
        return None        
    
    if not os.path.exists(path):
        WriteUcsWarning("Please provide the correct path")
        return None

       
    doc = xml.dom.minidom.parse(path)
    topNode = doc.documentElement
    
    if dumpToFile in _AffirmativeList:
        if dumpFilePath:
            finalOutput = GenCmdlet(topNode)
            print "### Script Output is in file < " + dumpFilePath + " >"
            outFile = open(dumpFilePath, 'w')
            outFile.write(finalOutput)
            outFile.close()
            #outFile = open(r"c:\work.txt", 'w+')
        else:
            print "Please profide dumpFilePath"
            return None
    else:
        finalOutput = GenCmdlet(topNode)
        print finalOutput


        




