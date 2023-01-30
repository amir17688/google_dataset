#!/usr/bin/python

class UcsCcoImage:
    def __init__(self):
        self.imageName = None
        self.version = None
        self.url = None
        self.ipUrl = None
        self.size = None
        self.checksumMd5 = None
        self.fileDescription = None
        self.networkCredential = None
        self.proxy = None
    
class UcsCcoImageList:
    IDAC_TAG_VERSION = "version"
    IDAC_TAG_IMAGE_NAME = "imageName"
    IDAC_TAG_URL = "url"
    IDAC_TAG_IP_URL = "IPurl"
    IDAC_TAG_SIZE = "size"
    IDAC_TAG_CHECKSUM = "checksum"
    IDAC_TAG_FILE_DESCRIPTION = "fileDescription"
    
def DownloadExtFile(url=None, credential=None, destinationPath=None):
    import urllib2
    import os
    from sys import stdout
    from UcsBase import WriteUcsWarning
    
    if not url:
        WriteUcsWarning("Please provide the url")
        return None        
    
    if not credential:
        WriteUcsWarning("Please provide the credential")
        return None   
    
    if not destinationPath:
        WriteUcsWarning("Please provide the path")
        return None
    

    
    file_name = os.path.basename(url)
    destinationFile = os.path.join(destinationPath,file_name)
   
    request = urllib2.Request(url)
    request.add_header("Authorization", "Basic %s" % credential)
    response = urllib2.urlopen(request)
    
    meta = response.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)
    
    f = open(destinationFile, 'wb')
    file_size_dl = 0
    block_sz = 64L
    while True:
        rBuffer = response.read(128*block_sz)
        if not rBuffer:
            break

        file_size_dl += len(rBuffer)
        f.write(rBuffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        stdout.write("\r%s" % status)
        stdout.flush()
        #print status
    print "Downloading Finished."

    f.close()
    
    
def Getmd5sum(filename):
    import md5
    m = md5.new()
    #with open(filename,'rb') as fs:
    fs = open(filename,'rb')

    for chunk in iter(lambda: fs.read(128*m.block_size), ''):
        m.update(chunk)
    
    fs.close()
    return m.hexdigest()



def GetUcsCcoImageList(username=None,password=None,mdfIdList=[]):
    from UcsBase import WriteUcsWarning
    import getpass
    import xml.dom
    import xml.dom.minidom
    import base64
    import urllib2

    
    if (username == None):
        username = raw_input("Username: ")

    if (password == None):
        password = getpass.getpass()
    
    
    ucsMdfIds = (283612660, 283853163, 283862063)
    url = "https://www.cisco.com/cgi-bin/front.x/ida/locator/locator.pl"
    
    idaXmlQueryHeader = 'inputXML=<?xml version="1.0" encoding="UTF-8"?><locator><input>'
    idaXmlQueryMdfId  = '<mdfConcept id="%s" name=""/>'
    idaXmlQueryFooter = '</input></locator>'
    
    # create inputXML string to post as data to the respective url via post method 
    inputXML = ""
    inputXML += idaXmlQueryHeader
    
    if not mdfIdList:
        for mdfId in ucsMdfIds:
            inputXML += (idaXmlQueryMdfId %(mdfId))
    else:
        for mdfId in mdfIdList:
            inputXML += (idaXmlQueryMdfId %(mdfId))
    
    inputXML += idaXmlQueryFooter

    credential = base64.encodestring('%s:%s' % (username, password))[:-1]
    
    request = urllib2.Request(url,data=inputXML)
    request.add_header("Authorization", "Basic %s" % credential)
    response = urllib2.urlopen(request)
    
    idaXmlResponse = response.read()
    #print idaXmlResponse
    
    if not idaXmlResponse:
        WriteUcsWarning("No Response from <%s>" %(url))
        return
    
    # Create XML of Response 
    doc = xml.dom.minidom.parseString(idaXmlResponse)
    imageNodeList = doc.getElementsByTagName("image")
    
    if not imageNodeList:
        WriteUcsWarning("No Images Found")
        return
    
    # Serialize image nodes in objects
    ccoImageList = []
    for imageNode in imageNodeList:
        #print imageNode.toxml()
        
        image = UcsCcoImage()
        image.networkCredential = credential
        
        propertyNodeList = [childNode for childNode in imageNode.childNodes if childNode.nodeType == childNode.ELEMENT_NODE and childNode.localName == "property"]
        for propertyNode in propertyNodeList:
            if not propertyNode.hasAttribute("name"):
                continue
            
            if propertyNode.getAttribute("name") == UcsCcoImageList.IDAC_TAG_VERSION:
                image.version = propertyNode.getAttribute("value")
                continue
            if propertyNode.getAttribute("name") == UcsCcoImageList.IDAC_TAG_IMAGE_NAME:
                image.imageName = propertyNode.getAttribute("value")
                continue
            if propertyNode.getAttribute("name") == UcsCcoImageList.IDAC_TAG_URL:
                image.url = propertyNode.getAttribute("value")
                continue
            if propertyNode.getAttribute("name") == UcsCcoImageList.IDAC_TAG_IP_URL:
                image.ipUrl = propertyNode.getAttribute("value")
                continue
            if propertyNode.getAttribute("name") == UcsCcoImageList.IDAC_TAG_SIZE:
                image.size = propertyNode.getAttribute("value")
                continue
            if propertyNode.getAttribute("name") == UcsCcoImageList.IDAC_TAG_CHECKSUM:
                if propertyNode.getAttribute("type") == "md5":
                    image.checksumMd5 = propertyNode.getAttribute("value")
                    continue
            if propertyNode.getAttribute("name") == UcsCcoImageList.IDAC_TAG_FILE_DESCRIPTION:
                image.fileDescription = propertyNode.getAttribute("value")
                continue
            
        
        ccoImageList.append(image)
        
    return ccoImageList
            
 
         
def GetUcsCcoImage(image=None,path=None):
    from UcsBase import WriteUcsWarning
    import os
    
    if not image:
        return
    
    if not path:
        WriteUcsWarning("Please provide the url")
        return None
    
    if not os.path.isdir(path):
        WriteUcsWarning("Not the valid directory <%s>" %(path))
        return None
        
    if (isinstance(image, UcsCcoImage) == False):
        WriteUcsWarning("Object is not of type UcsCcoImage")
        return
    
        
    imageUrl = image.url
    print ("Processing Image " + image.imageName)
    
    DownloadExtFile(imageUrl, image.networkCredential, path)
    
    localFile = os.path.join(path,image.imageName)
    
    if not os.path.exists(localFile):
        WriteUcsWarning("Download Failed for file <%s>" %(localFile))
        return
    
    md5Sum = Getmd5sum(localFile)
    if not md5Sum:
        WriteUcsWarning("Unable to generate md5sum for file <%s>" %(localFile))
        WriteUcsWarning("Deleting file <%s> ....." %(localFile))
        os.remove(localFile)
        return
    
    if md5Sum != image.checksumMd5:
        WriteUcsWarning("Incorrect md5sum for file <%s>" %(localFile))
        WriteUcsWarning("Deleting file <%s> ....." %(localFile))
        os.remove(localFile)
        return


    print "Processing Image Completed."

