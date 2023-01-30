#!/usr/bin/env python

from __future__ import print_function, unicode_literals, division, absolute_import  # We require Python 2.6 or later

__author__ = "Lukasz Uszko, Daniel van Dorp"
__copyright__ = "Copyright 2016"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "lukasz.uszko@gmail.com, daniel@vandorp.biz"

import sys

PY2 = sys.version_info[0] == 2
if PY2:
    from future import standard_library
    standard_library.install_aliases()
    from builtins import *
    from builtins import str
    from builtins import map
    from builtins import object
    reload(sys)
    sys.setdefaultencoding('utf8')

import requests
import os
import configparser
import re
from collections import OrderedDict
from bs4 import BeautifulSoup



class MyPacktPublishingBooksDownloader(object):
    
    def __init__(self,session=None):
    
        self.packtPubUrl= "https://www.packtpub.com"
        self.myBooksUrl= "https://www.packtpub.com/account/my-ebooks"
        self.loginUrl= "https://www.packtpub.com/register"
        self.myPacktEmail, self.myPacktPassword= self.getLoginData("configFile.cfg")
        self.downloadFolderPath,self.downloadFormats,self.downloadBookTitles= self.getDownloadData("configFile.cfg")
        if(not os.path.exists(self.downloadFolderPath)):
            print("[ERROR] Download folder path: '"+self.downloadFolderPath+ "' doesn't exist" )
            sys.exit(1)
        self.session= session
        if self.session is None:
            self.createSession()
        self.bookData=None
        
    
    def getLoginData(self, cfgFilePath):
        config =configparser.ConfigParser()
        try:
            if(not config.read(cfgFilePath)):
                raise configparser.Error(cfgFilePath+ ' file not found')
            email= config.get("LOGIN_DATA",'email')
            password= config.get("LOGIN_DATA",'password')
            return (email,password)
        except configparser.Error as e:
            print("[ERROR] "+cfgFilePath+ " file incorrect or doesn't exist! : "+str(e))
            sys.exit(1)
            
    def getDownloadData(self, cfgFilePath):
        config =configparser.ConfigParser()
        try:
            if(not config.read(cfgFilePath)):
                raise configparser.Error(cfgFilePath+ ' file not found')
            downloadPath= config.get("DOWNLOAD_DATA",'downloadFolderPath')
            downloadFormats= tuple(format.replace(' ', '') for format in config.get("DOWNLOAD_DATA",'downloadFormats').split(','))
            downloadBookTitles= None
            try:
                downloadBookTitles= [title.strip(' ') for title in config.get("DOWNLOAD_DATA",'downloadBookTitles').split(',')]
                if len(downloadBookTitles)is 0:
                    downloadBookTitles= None
                print(downloadBookTitles)
            except configparser.Error as e:
                pass
            return (downloadPath,downloadFormats,downloadBookTitles)
        except configparser.Error as e:
            print("[ERROR] "+cfgFilePath+ " file incorrect or doesn't exist! : "+str(e))
            sys.exit(1)
    
    def createSession(self):
        reqHeaders= {'Content-Type':'application/x-www-form-urlencoded',
                    'Connection':'keep-alive'}
        formData= {'email':self.myPacktEmail,
                'password':self.myPacktPassword,
                'op':'Login',
                'form_build_id':'',
                'form_id':'packt_user_login_form'}
        try:
            #to get form_build_id
            print("Creates session ...")
            r = requests.get(self.loginUrl,timeout=10)
            content = BeautifulSoup(str(r.content), 'html.parser')
            formBuildId = [element['value'] for element in content.find(id='packt-user-login-form').find_all('input',{'name':'form_build_id'})]
            formData['form_build_id']=formBuildId[0]
        except requests.exceptions.RequestException as exception:
            print("[ERROR] - Exception occured %s "%exception )
                
        try:
            self.session = requests.Session()
            rPost = self.session.post(self.loginUrl, headers=reqHeaders,data=formData)
            if(rPost.status_code is not 200):
                raise requests.exceptions.RequestException("login failed! ")               
        except requests.exceptions.RequestException as exception:
            print("[ERROR] - Exception occured %s "%exception )
            sys.exit(1)
            
    def getDataOfAllMyBooks(self):
        try:
            print("Getting books data ...")
            r = self.session.get(self.myBooksUrl,timeout=10)
            if(r.status_code is 200):
                print("opened  '"+ self.myBooksUrl+"' succesfully!")
            myBooksHtml = BeautifulSoup(r.text, 'html.parser')
            all =  myBooksHtml.find(id='product-account-list').find_all('div', {'class':'product-line unseen'})
            self.bookData= [ {'title': re.sub(r'\s*\[e\w+\]\s*','',attr['title'], flags=re.I ).strip(' '), 'id':attr['nid']}   for attr in all]
            for i,div in enumerate(myBooksHtml.find_all('div', {'class':'product-buttons-line toggle'})):
                downloadUrls= {}
                for a_href in div.find_all('a'):
                    m = re.match(r'^(/[a-zA-Z]+_download/(\w+)(/(\w+))*)',a_href.get('href'))
                    if m:
                        if m.group(4) is not None:
                           downloadUrls[m.group(4)]= m.group(0)
                        else:
                            downloadUrls['code']= m.group(0)
                self.bookData[i]['downloadUrls']=downloadUrls 
        except requests.exceptions.RequestException as exception:
            print("[ERROR] - Exception occured %s "%exception )
            
            
    def downloadBooks(self,titles=None,formats=None): #titles= list('C# tutorial', 'c++ Tutorial') ; format=tuple('pdf','mobi','epub','code')
        try:
            #download ebook
            if formats is None:
                formats=('pdf','mobi','epub','code')   
            if titles is not None:
                tempBookData = [data for i,data in enumerate(self.bookData) if any(data['title']==title for title in titles) ]
            else:
                tempBookData=self.bookData
            nrOfBooksDownloaded=0
            for i, book in enumerate(tempBookData):
                for format in formats:
                    #print(format)
                    if format in list(tempBookData[i]['downloadUrls'].keys()):
                        if format == 'code':
                            fileType='zip'
                        else:
                            fileType = format
                        formattedTitle= ''.join(list(map(str.capitalize, tempBookData[i]['title'].split(' '))))
                        for ch in ['?',':','*','/']:
                            if ch in formattedTitle:
                                formattedTitle=formattedTitle.replace(ch,'_')
                        fullFilePath=os.path.join(self.downloadFolderPath,formattedTitle+'.'+fileType)
                        if(os.path.isfile(fullFilePath)):
                            print(fullFilePath+" already exists")
                            pass
                        else:
                            if format == 'code':
                                print("downloading code for eBook: '"+tempBookData[i]['title']+ "'...")                           
                            else:
                                print("downloading eBook: '"+tempBookData[i]['title']+"' in '."+format+ "' format...")
                            r = self.session.get(self.packtPubUrl+tempBookData[i]['downloadUrls'][format],timeout=100)
                            if(r.status_code is 200):
                                with open(fullFilePath,'wb') as f:
                                    f.write(r.content)
                                if format == 'code':
                                    print("[SUCCESS] code for eBook: '"+tempBookData[i]['title']+"' downloaded succesfully!")                           
                                else:
                                    print("[SUCCESS] eBook: '"+tempBookData[i]['title']+'.'+format+"' downloaded succesfully!")      
                                nrOfBooksDownloaded=i+1
                            else:
                                raise requests.exceptions.RequestException("Cannot download "+tempBookData[i]['title'])                            
            print(str(nrOfBooksDownloaded)+" eBooks have been downloaded !")          
        except requests.exceptions.RequestException as exception:
            print("[ERROR] - Exception occured during GET request%s "%exception )
        except IOError as exception:
            print("[ERROR] - Exception occured durin opening file %s "%exception )
        
       
        
if __name__ == '__main__':
    
    downloader = MyPacktPublishingBooksDownloader()
    downloader.getDataOfAllMyBooks()
    downloader.downloadBooks(downloader.downloadBookTitles, downloader.downloadFormats)
    print("--done--")
