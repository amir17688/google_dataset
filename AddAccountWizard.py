#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (C) 2013, Cameron White
from .tools import waiting_effects
from github import Github
from github.GithubException import BadCredentialsException, \
    TwoFactorException, GithubException
from github.Authorization import Authorization
from PyQt4.QtCore import QRegExp
from PyQt4.QtGui import QWizardPage, QWizard, QRadioButton, QLineEdit, \
    QRegExpValidator, QVBoxLayout, QLabel, QFormLayout, QValidator

class GithubCredentialsWizardPage(QWizardPage):
    def __init__(self, parent=None):
        super(GithubCredentialsWizardPage, self).__init__(
            parent,
            title="Credentials",
            subTitle="Enter your username/password or token")
       
        # Radio Buttons 

        self.userPassRadioButton = QRadioButton()
        self.userPassRadioButton.toggled.connect(self.changeMode)
        self.userPassRadioButton.toggled.connect(self.completeChanged.emit)

        self.tokenRadioButton = QRadioButton()
        self.tokenRadioButton.toggled.connect(self.changeMode)
        self.tokenRadioButton.toggled.connect(self.completeChanged.emit)

        #  LineEdits
        
        # usernameEdit
        self.usernameEdit = QLineEdit(
                textChanged=self.completeChanged.emit)
        # Username may only contain alphanumeric characters or dash
        # and cannot begin with a dash
        self.usernameEdit.setValidator(
            QRegExpValidator(QRegExp('[A-Za-z\d]+[A-Za-z\d-]+')))

        # passwordEdit
        self.passwordEdit = QLineEdit(
                textChanged=self.completeChanged.emit)
        self.passwordEdit.setValidator(
            QRegExpValidator(QRegExp('.+')))
        self.passwordEdit.setEchoMode(QLineEdit.Password)
        
        # tokenEdit
        self.tokenEdit = QLineEdit(
                textChanged=self.completeChanged.emit)
        # token may only contain alphanumeric characters
        self.tokenEdit.setValidator(
            QRegExpValidator(QRegExp('[A-Za-z\d]+')))
        self.tokenEdit.setEchoMode(QLineEdit.Password)
      
        # Form

        form = QFormLayout()
        form.addRow("<b>username/password</b>", self.userPassRadioButton)
        form.addRow("username: ", self.usernameEdit)
        form.addRow("password: ", self.passwordEdit)
        form.addRow("<b>token</b>", self.tokenRadioButton)
        form.addRow("token: ", self.tokenEdit)
        
        # Layout

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(form)
        self.setLayout(self.mainLayout)
        
        # Fields

        self.registerField("username", self.usernameEdit)
        self.registerField("password", self.passwordEdit)
        self.registerField("token", self.tokenEdit)

        self.userPassRadioButton.toggle()

        self.require_2fa = False

    def changeMode(self):
        
        if self.userPassRadioButton.isChecked():
            self.usernameEdit.setEnabled(True)
            self.passwordEdit.setEnabled(True)
            self.tokenEdit.setEnabled(False)
        elif self.tokenRadioButton.isChecked():
            self.usernameEdit.setEnabled(False)
            self.passwordEdit.setEnabled(False)
            self.tokenEdit.setEnabled(True)

    def nextId(self):
        
        if self.require_2fa:
            return 2 # TODO remove magic number
        else:
            return 3 # TODO remove magic number
    
    def isComplete(self):
        
        if self.userPassRadioButton.isChecked():
            usernameValidator = self.usernameEdit.validator()
            usernameText = self.usernameEdit.text()
            usernameState = usernameValidator.validate(usernameText, 0)[0]
            passwordValidator = self.passwordEdit.validator()
            passwordText = self.passwordEdit.text()
            passwordState = passwordValidator.validate(passwordText, 0)[0]
            if usernameState == QValidator.Acceptable and \
                    passwordState == QValidator.Acceptable:
                return True

        elif self.tokenRadioButton.isChecked():
            tokenValidator = self.tokenEdit.validator()
            tokenText = self.tokenEdit.text()
            tokenState = tokenValidator.validate(tokenText, 0)[0]
            if tokenState == QValidator.Acceptable:
                return True

        return False
   
    @waiting_effects
    def validatePage(self):
        
        # TODO - clean this up

        if self.userPassRadioButton.isChecked():
            username = str(self.field('username').toString())
            password = str(self.field('password').toString())
            try: 
                g = Github(username, password)
                user = g.get_user()
                authentication = user.create_authorization(scopes=['repo'], note='test')
            except TwoFactorException:
                self.require_2fa = True
                return True
            except GithubException:
                self.require_2fa = False
                return False
            self.setField('token', str(authentication.token))
            self.require_2fa = False
            return True
        elif self.tokenRadioButton.isChecked():
            token = str(self.field('token').toString())
            try:
                self.setField('username', Github(token).get_user().login)
            except BadCredentialsException:
                return False
            else:
                self.require_2fa = False
                return True 
        else:
            self.require_2fa = False
            return False

class AccountTypeWizardPage(QWizardPage):
    def __init__(self, parent=None):
        super(AccountTypeWizardPage, self).__init__(
            parent,
            title="Select Account Type",
            subTitle="Select the type of account to create")
        
        # Radio Buttons

        self.githubRadioButton = QRadioButton("Github account")
        self.githubRadioButton.toggle()

        # Layout

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.githubRadioButton)
        self.setLayout(self.mainLayout)
    
    def nextId(self):
        
        if self.githubRadioButton.isChecked():
            return 1 # TODO remove magic number

class Github2FAWizardPage(QWizardPage):
    def __init__(self, parent=None):
        super(Github2FAWizardPage, self).__init__(
                parent,
                title="Two-Factor Authentication",
                subTitle="Enter required authentication code")
       
        # LineEdits

        self.codeEdit = QLineEdit()
        # codeEdit may only contain 1 or more digits
        self.codeEdit.setValidator(QRegExpValidator(QRegExp(r'[\d]+')))
        
        # Form

        self.form = QFormLayout()
        self.form.addRow("Code: ", self.codeEdit)
        
        # Layout

        self.setLayout(self.form)

        # Fields

        self.registerField('2fa_code*', self.codeEdit)

    def nextId(self):
        
        return 3 # TODO remove magic number

    @waiting_effects
    def validatePage(self):

        username = str(self.field('username').toString())
        password = str(self.field('password').toString())
        code = str(self.field('2fa_code').toString())

        try: # to use 2fa code
            g = Github(username, password)
            user = g.get_user()
            authentication = user.create_authorization(
                   scopes=['repo'], note='test', onetime_password=code)
        except GithubException:
            self.wizard().back() # start over TODO make sure this works
            return False

        self.setField('token', str(authentication.token))
        return True

class UserSummaryWizardPage(QWizardPage):
    def __init__(self, parent=None):
        super(UserSummaryWizardPage, self).__init__(
                parent,
                title="Summary",
                subTitle="Summary of new user account")
        
        # labels

        self.usernameLabel = QLabel()
        self.tokenLabel = QLabel()
        
        # form

        self.form = QFormLayout()
        self.form.addRow("username: ", self.usernameLabel)
        self.form.addRow("token: ", self.tokenLabel)
        
        # layout

        self.setLayout(self.form)
    
    def initializePage(self):
         
        self.usernameLabel.setText(self.field('username').toString())
        self.tokenLabel.setText(self.field('token').toString())

class AddAccountWizard(QWizard):

    def __init__(self, parent=None):
        super(AddAccountWizard, self).__init__(
                parent,
                windowTitle="Sign In")
        
        # TODO - remove magic numbers
        self.setPage(0, AccountTypeWizardPage())
        self.setPage(1, GithubCredentialsWizardPage())
        self.setPage(2, Github2FAWizardPage())
        self.setPage(3, UserSummaryWizardPage())
