#!/usr/bin/env python

__author__ = "Lukasz Uszko"
__copyright__ = "Copyright 2015"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "lukasz.uszko@gmail.com"

import requests
import os
import sys
import configparser
from html.parser import HTMLParser

class PacktFreeBookHtmlParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.claimAttrs=None
        self.bookTitle= str()
        self.formBuildIdAttrs= None
        self.bookTitleTagFound=False
        self.loginFormTagFound=False
    def handle_starttag(self, tag, attrs):
        if tag=='a':
            for name, value in attrs:
                if name=='class' and value=='twelve-days-claim':
                    self.claimAttrs= attrs
        elif tag=='div':
            for name, value in attrs:
                if name=='class' and value=='dotd-title':
                    self.bookTitleTagFound=True
        elif tag=='form':
            for name, value in attrs:
                if name=='id' and value=='packt-user-login-form':
                    self.loginFormTagFound= True          
        elif self.loginFormTagFound and tag=='input':
            for name, value in attrs:
                if name=='name' and value=='form_build_id':
                    self.formBuildIdAttrs =attrs
                    #print(attrs)                
        #print("START_TAG:"+tag)
        #print(attrs)        
    def handle_endtag(self, tag):
        #print("END_TAG:"+tag)
        if(self.bookTitleTagFound and tag=='div'):
            self.bookTitleTagFound=False
            self.bookTitle=  self.bookTitle.replace('\\t','').replace('\\n','')          
        elif self.loginFormTagFound and tag=='form':
            self.loginFormTagFound= False
        pass    
    def handle_data(self,data):
        if(self.bookTitleTagFound):
            self.bookTitle+=data                
    def getClaimUrl(self):
        claimUrl=None
        if self.claimAttrs is not None:
            for name, value in self.claimAttrs:
                if name=='href':
                    claimUrl= value
        return claimUrl
    def getFormBuildId(self):
        formBuildId=str()
        if self.formBuildIdAttrs is not None:
            for name, value in self.formBuildIdAttrs:
                if name=='value':
                    formBuildId+= value
        return formBuildId 
if __name__ == '__main__':
    '''connection parameters'''
    config =configparser.ConfigParser()
    try:
        if(not config.read("configFile.cfg")):
            raise configparser.Error('config file not found')
        email= config.get("LOGIN_DATA",'email')
        password= config.get("LOGIN_DATA",'password')
        downloadBooksAfterClaim= config.get("DOWNLOAD_DATA",'downloadBookAfterClaim')
    except configparser.Error as e:
        print("[ERROR] loginData.cfg file incorrect or doesn't exist! : "+str(e))
        sys.exit(1)
    freeLearningUrl= "https://www.packtpub.com/packt/offers/free-learning"
    packtpubUrl= 'https://www.packtpub.com'
    reqHeaders= {'Content-Type':'application/x-www-form-urlencoded',
             'Connection':'keep-alive'}
    formData= {'email':email,
                'password':password,
                'op':'Login',
                'form_build_id':'',
                'form_id':'packt_user_login_form'}
    print("start grabbing eBook...")
    try:
        r = requests.get(freeLearningUrl,timeout=10)
    except requests.exceptions.RequestException as exception:
        print("[ERROR] - Exception occured %s "%exception )
        sys.exit(1)
    strContent= str(r.content)
    htmlParser=PacktFreeBookHtmlParser()
    try:
        htmlParser.feed(strContent)
        r = requests.get(packtpubUrl+htmlParser.getClaimUrl(),timeout=10)
    except TypeError as typeError:
        print("[ERROR] - Type error occured %s "%typeError )
        sys.exit(1)
    except requests.exceptions.RequestException as exception:
        print("[ERROR] - Exception occured %s "%exception )
        sys.exit(1)
    if(r.status_code is not 200):
        print("login required ...")
        formData['form_build_id']=htmlParser.getFormBuildId()
        session = requests.Session()
        try:
            rPost = session.post(freeLearningUrl, headers=reqHeaders,data=formData)
            if(rPost.status_code is not 200):
                raise requests.exceptions.RequestException("login failed! ")               
            r = session.get(packtpubUrl+htmlParser.getClaimUrl(),timeout=10)
        except requests.exceptions.RequestException as exception:
                print("[ERROR] - Exception occured %s "%exception )
                sys.exit(1)
    if(r.status_code is 200):
        print("[SUCCESS] - eBook: '" + htmlParser.bookTitle +"' has been succesfully grabbed !")
        if downloadBooksAfterClaim=="YES":
            from packtFreeBookDownloader import MyPacktPublishingBooksDownloader
            downloader = MyPacktPublishingBooksDownloader(session)
            downloader.getDataOfAllMyBooks()
            downloader.downloadBooks([htmlParser.bookTitle], downloader.downloadFormats)
            
    else:
        print("[ERROR] - eBook: '" + htmlParser.bookTitle +"' has not been grabbed, respCode: "+str(r.status_code))